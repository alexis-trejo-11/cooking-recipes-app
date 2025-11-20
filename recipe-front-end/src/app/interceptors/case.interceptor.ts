import {
  HttpEvent,
  HttpRequest,
  HttpResponse,
  HttpInterceptorFn,
  HttpHandlerFn,
} from '@angular/common/http';
import { map } from 'rxjs/operators';
import humps from 'humps';

export const caseInterceptor: HttpInterceptorFn = (req: HttpRequest<any>, next: HttpHandlerFn) => {
  // Avoid transforming multipart/form-data requests
  const contentType = req.headers.get('Content-Type') || '';
  let newReq = req;
  if (req.body && !contentType.includes('multipart/form-data')) {
    const snakeBody = humps.decamelizeKeys(req.body);
    newReq = req.clone({ body: snakeBody });
  }

  return next(newReq).pipe(
    map((evt: HttpEvent<any>) => {
      if (evt instanceof HttpResponse && evt.body != null) {
        const camelBody = humps.camelizeKeys(evt.body);
        return evt.clone({ body: camelBody });
      }
      return evt;
    })
  );
};
