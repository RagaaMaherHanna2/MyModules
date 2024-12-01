import { Component } from '@angular/core';
import { createSelector, Store } from '@ngrx/store';
import { ConfirmationService } from 'primeng/api';
import {
  closeConfirmationDialog,
  confirmationFeature,
} from 'src/store/confirmationSlice';

@Component({
  selector: 'app-confirmation-dialog',
  templateUrl: './confirmation-dialog.component.html',
  styleUrls: ['./confirmation-dialog.component.scss'],
  providers: [ConfirmationService],
})
export class ConfirmationDialogComponent {
  constructor(private readonly store: Store) {}

  open$ = this.store.select(
    createSelector(confirmationFeature, (state) => state.open)
  );
  message$ = this.store.select(
    createSelector(confirmationFeature, (state) => state.message)
  );
  icon$ = this.store.select(
    createSelector(confirmationFeature, (state) => state.icon)
  );
  callback$ = this.store.select(
    createSelector(confirmationFeature, (state) => state.callbackFunction)
  );

  onHide() {
    this.store.dispatch(closeConfirmationDialog());
  }
  confirm() {
    this.callback$
      .subscribe((callback) => {
        callback();
        this.onHide();
      })
      .unsubscribe();
  }
}
