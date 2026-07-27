/**
 * Local / compile-time defaults. Prefer runtime values from
 * `getApiUrl()` / `getBaseUrl()` (env vars via the SSR server).
 */
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8080/api/v1',
  baseUrl: 'http://localhost:4200',
};
