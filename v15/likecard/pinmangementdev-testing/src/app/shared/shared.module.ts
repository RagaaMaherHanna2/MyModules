import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ErrorDialogComponent } from './error-dialog/error-dialog.component';
import { DialogModule } from 'primeng/dialog';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { ConfirmationDialogComponent } from './confirmation-dialog/confirmation-dialog.component';
import { LoadingDialogComponent } from './loading-dialog/loading-dialog.component';
import { ReferenceComponent } from './reference/reference.component';

@NgModule({
  declarations: [
    ConfirmationDialogComponent,
    ErrorDialogComponent,
    LoadingDialogComponent,
    ReferenceComponent,
  ],
  imports: [
    CommonModule,
    ConfirmDialogModule,
    DialogModule,
    ProgressSpinnerModule,
  ],
  exports: [
    ConfirmationDialogComponent,
    ErrorDialogComponent,
    LoadingDialogComponent,
    ReferenceComponent,
  ],
})
export class SharedModule {}
