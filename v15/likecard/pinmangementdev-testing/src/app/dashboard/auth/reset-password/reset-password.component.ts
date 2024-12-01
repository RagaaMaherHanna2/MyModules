import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Store } from '@ngrx/store';
import { MessageService } from 'primeng/api';
import { AuthService } from 'src/app/services/auth.service';
import { environment } from 'src/environments/environment';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-reset-password',
  templateUrl: './reset-password.component.html',
  styleUrls: ['./reset-password.component.scss'],
})
export class ResetPasswordComponent {
  resetPasswordForm = this.formBuilder.group({
    email: ['', [Validators.required, Validators.email]],
  });
  locale = $localize.locale;

  get email() {
    return this.resetPasswordForm.get('email')!;
  }

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private messageService: MessageService,
    private readonly store: Store
  ) {}
  reset(): void {
    this.store.dispatch(openLoadingDialog());
    this.authService
      .resetPassword({
        email: this.email.value!,
        url: `${environment.DASHBOARD_LINK}/${this.locale}/auth/verify`,
      })
      .subscribe((res) => {
        if (res.ok) {
          this.store.dispatch(closeLoadingDialog());
          this.messageService.add({
            detail: $localize`We've sent you an email. Please check your inbox.`,
            summary: $localize`Success`,
            icon: 'pi pi-check-circle',
            severity: 'success',
          });
        }
      });
  }
}
