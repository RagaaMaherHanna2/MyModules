import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
} from '@angular/common/http';
import { Observable, catchError, tap, throwError } from 'rxjs';
import { Store } from '@ngrx/store';
import { closeLoadingDialog } from 'src/store/loadingSlice';
import { openErrorDialog } from 'src/store/errorSlice';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root',
})
export class ErrorInterceptor implements HttpInterceptor {
  constructor(private store: Store, private router: Router) {}

  intercept(
    request: HttpRequest<unknown>,
    next: HttpHandler
  ): Observable<HttpEvent<unknown>> {
    return next.handle(request).pipe(
      tap((res) => {
        const result: any = res;
        if (result.ok === false || (result.body && result.body.ok === false)) {
          this.store.dispatch(closeLoadingDialog());
          this.store.dispatch(
            openErrorDialog({
              message:
                result.body.message ??
                $localize`An error happened. Please Try Again`,
            })
          );
        }
      }),
      catchError((err) => {
        this.store.dispatch(closeLoadingDialog());

        // This code is a bit dumb. but the error handling in odoo is hell.
        if (
          (err.status === 401 || err.status === 403) &&
          err.error.message.startsWith('401')
        ) {
          this.store.dispatch(
            openErrorDialog({
              message: $localize`Unauthorized. Please log in again`,
              logout: true,
            })
          );
        } else if (err.status === 400) {
          if (err.error.message.startsWith('100')) {
            this.store.dispatch(
              openErrorDialog({
                message: $localize`You do not have permission, If you have any questions, Contact The Merchant`,
              })
            );
            this.router.navigate([`/dashboard/`]);
          } else {
            this.store.dispatch(
              openErrorDialog({
                message:
                  err.error.message ??
                  $localize`An error happened. Please Try Again`,
              })
            );
          }
        } else {
          this.store.dispatch(
            openErrorDialog({
              message:
                err.error.message ??
                $localize`An error happened. Please Try Again`,
            })
          );
        }
        return throwError(() => new Error(err.status));
      })
    );
  }
}
