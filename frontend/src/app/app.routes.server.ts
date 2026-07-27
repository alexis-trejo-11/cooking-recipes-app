import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  {
    // On-demand SSR so parameterized routes (e.g. recipes/:id) work without
    // needing getPrerenderParams. The Docker image runs this Node SSR server.
    path: '**',
    renderMode: RenderMode.Server,
  },
];
