import { Component } from '@angular/core';
import {
  AbstractControl,
  FormBuilder,
  FormGroup,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { MessageService } from 'primeng/api';
import { AuthService } from 'src/app/services/auth.service';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-verify-reset-password',
  templateUrl: './verify-reset-password.component.html',
  styleUrls: ['./verify-reset-password.component.scss'],
})
export class VerifyResetPasswordComponent {
  verifyResetPasswordForm = this.formBuilder.group(
    {
      token: ['', [Validators.required]],
      password: ['', [Validators.required]],
      validatePassword: ['', [Validators.required]],
    },
    {
      validators: [this.passwordMatchValidator],
    }
  );
  constructor(
    private authService: AuthService,
    private formBuilder: FormBuilder,
    private router: Router,
    private messageService: MessageService,
    private store: Store
  ) {}

  passwordMatchValidator(group: FormGroup): ValidationErrors | null {
    const password = group.controls['password'];
    const validatePassword = group.controls['validatePassword'];
    if (
      password.dirty &&
      validatePassword.dirty &&
      password.value !== validatePassword.value
    ) {
      return {
        passwordMismatch: true,
      };
    }
    return null;
  }

  verifyResetPassword(): void {
    this.store.dispatch(openLoadingDialog());
    const params = {
      token: this.verifyResetPasswordForm.controls['token'].value!,
      new_password: this.verifyResetPasswordForm.controls['password'].value!,
    };
    this.authService.verifyResetPassword(params).subscribe((res) => {
      if (res.ok) {
        this.store.dispatch(closeLoadingDialog());
        this.messageService.add({
          detail: $localize`Password reset successful! Please log in to continue`,
          summary: $localize`Success`,
          icon: 'pi pi-check-circle',
          severity: 'success',
        });
        this.router.navigate(['/auth/login']);
      }
    });
  }
}
