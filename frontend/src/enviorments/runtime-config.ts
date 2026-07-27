import { environment } from './enviroment';

/**
 * Public runtime config injected by the SSR server (see server.ts).
 * On the browser this is set via a <script> in the HTML before Angular boots.
 * During SSR, server.ts assigns the same object on globalThis from process.env.
 */
export interface RuntimeEnv {
  apiUrl: string;
  baseUrl: string;
}

declare global {
  // eslint-disable-next-line no-var -- ambient global used by Express injection
  var __env: Partial<RuntimeEnv> | undefined;
}

export function getApiUrl(): string {
  return globalThis.__env?.apiUrl || environment.apiUrl;
}

export function getBaseUrl(): string {
  return globalThis.__env?.baseUrl || environment.baseUrl;
}
