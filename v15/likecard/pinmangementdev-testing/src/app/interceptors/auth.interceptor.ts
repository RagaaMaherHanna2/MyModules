import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpHeaders,
} from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor() {}

  intercept(
    request: HttpRequest<any>,
    next: HttpHandler
  ): Observable<HttpEvent<any>> {
    request = request.clone({
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
      }),
    });
    let token = localStorage.getItem(environment.TOKEN_KEY);
    if (token) {
      request = request.clone({
        headers: new HttpHeaders({
          'Content-Type': 'application/json',
          Authorization: `Bearer ` + token
        }),
      });
    }
    return next.handle(request);
  }
}
