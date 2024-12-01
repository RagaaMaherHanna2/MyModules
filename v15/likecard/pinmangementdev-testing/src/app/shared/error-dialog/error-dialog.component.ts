import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { createSelector, Store } from '@ngrx/store';
import { AuthService } from 'src/app/services/auth.service';
import { environment } from 'src/environments/environment';
import { closeErrorDialog, errorFeature } from 'src/store/errorSlice';

@Component({
  selector: 'app-error-dialog',
  templateUrl: './error-dialog.component.html',
  styleUrls: ['./error-dialog.component.scss'],
})
export class ErrorDialogComponent implements OnInit {
  open$ = this.store.select(
    createSelector(errorFeature, (state) => state.open)
  );
  message$ = this.store.select(
    createSelector(errorFeature, (state) => state.message)
  );
  logout$ = this.store.select(
    createSelector(errorFeature, (state) => state.logout)
  );
  constructor(
    private readonly store: Store,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {}

  dismiss(): void {
    this.store.dispatch(closeErrorDialog());

    this.logout$.subscribe((res) => {
      if (res) {
        localStorage.removeItem(environment.TOKEN_KEY);
        localStorage.removeItem(environment.USER_ROLES_KEY);
        localStorage.removeItem(environment.USER_KEY);
        localStorage.removeItem('first_login');
        this.router.navigate(['/auth/login']);
        // this.authService.logout();
      }
    });
  }
}
