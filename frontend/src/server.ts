import {
  AngularNodeAppEngine,
  createNodeRequestHandler,
  isMainModule,
  writeResponseToNodeResponse,
} from '@angular/ssr/node';
import express from 'express';
import { join } from 'node:path';

const browserDistFolder = join(import.meta.dirname, '../browser');

/**
 * Public runtime config from env vars (NOT secrets — visible in the browser).
 * Assigned on globalThis so SSR uses the same values as the client after HTML injection.
 */
const runtimeEnv = {
  apiUrl: process.env['API_BASE_URL'] ?? 'http://localhost:8080/api/v1',
  baseUrl: process.env['BASE_URL'] ?? 'http://localhost:4200',
};
(
  globalThis as typeof globalThis & { __env?: typeof runtimeEnv }
).__env = runtimeEnv;

const app = express();

// Trust the reverse proxy (Cloudflare / nginx) so req.hostname reflects the
// original Host / X-Forwarded-Host header.
app.set('trust proxy', true);

/**
 * Hostnames this server is allowed to answer for, configured at runtime via
 * the ALLOWED_HOSTS env var (comma-separated). Use "*" to disable the check.
 * Requests with an unknown Host header get a 403 (basic Host-header defense).
 */
const allowedHosts = (process.env['ALLOWED_HOSTS'] ?? '')
  .split(',')
  .map((host) => host.trim().toLowerCase())
  .filter(Boolean);

// Also feed the same allow-list to Angular's SSR engine; otherwise it treats
// unknown Host headers as SSRF risks and silently falls back to client-side
// rendering (Angular security advisory GHSA-x288-3778-4hhx).
const angularApp = new AngularNodeAppEngine(
  allowedHosts.length ? { allowedHosts } : undefined,
);

app.use((req, res, next) => {
  if (allowedHosts.length === 0 || allowedHosts.includes('*')) {
    next();
    return;
  }

  const host = (req.hostname || '').toLowerCase();
  if (allowedHosts.includes(host)) {
    next();
    return;
  }

  res.status(403).send('Forbidden: host not allowed');
});

/**
 * Inject window.__env into HTML so the browser bundle reads API_BASE_URL / BASE_URL
 * from the container env at request time (no rebuild needed when they change).
 */
async function injectRuntimeEnv(response: Response): Promise<Response> {
  const contentType = response.headers.get('content-type') ?? '';
  if (!contentType.includes('text/html')) {
    return response;
  }

  const html = await response.text();
  const script = `<script>window.__env=${JSON.stringify(runtimeEnv)};</script>`;
  const injected = html.includes('</head>')
    ? html.replace('</head>', `${script}</head>`)
    : `${script}${html}`;

  const headers = new Headers(response.headers);
  headers.delete('content-length');

  return new Response(injected, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

/**
 * Serve static files from /browser
 */
app.use(
  express.static(browserDistFolder, {
    maxAge: '1y',
    index: false,
    redirect: false,
  }),
);

/**
 * Handle all other requests by rendering the Angular application.
 */
app.use((req, res, next) => {
  angularApp
    .handle(req)
    .then(async (response) => {
      if (!response) {
        next();
        return;
      }
      const withEnv = await injectRuntimeEnv(response);
      await writeResponseToNodeResponse(withEnv, res);
    })
    .catch(next);
});

/**
 * Start the server if this module is the main entry point, or it is ran via PM2.
 * The server listens on the port defined by the `PORT` environment variable, or defaults to 4000.
 */
if (isMainModule(import.meta.url) || process.env['pm_id']) {
  const port = process.env['PORT'] || 4000;
  app.listen(port, (error) => {
    if (error) {
      throw error;
    }

    console.log(`Node Express server listening on http://localhost:${port}`);
    console.log(`Runtime API_BASE_URL=${runtimeEnv.apiUrl}`);
  });
}

/**
 * Request handler used by the Angular CLI (for dev-server and during build) or Firebase Cloud Functions.
 */
export const reqHandler = createNodeRequestHandler(app);
