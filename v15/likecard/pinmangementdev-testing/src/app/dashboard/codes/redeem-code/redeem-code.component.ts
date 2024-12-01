import { Component } from '@angular/core';
import { Validators, FormBuilder } from '@angular/forms';
import { Store } from '@ngrx/store';
import { CodeService } from 'src/app/services/Code/code.service';
import { RedeemPrepaidCodeResponse, RedeemPrepaidCodeRequest } from 'src/models/prepaid/models';
import { openLoadingDialog, closeLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-redeem-code',
  templateUrl: './redeem-code.component.html',
  styleUrls: ['./redeem-code.component.scss'],
})
export class RedeemCodeComponent {
  locale = $localize.locale;
  codeForm = this.formBuilder.group({
    code: ['', [Validators.required]],
    user_id: ['', [Validators.required]],
    language: [this.locale?.substring(0, 2), [Validators.required]],
    deduct_value: [0, [Validators.required, Validators.min(1)]],
    transaction_id: ['', [Validators.required]],
    pin_code: ['', [Validators.required]],
  });

  languageOptions = [
    { label: $localize`Arabic`, value: 'ar' },
    { label: $localize`English`, value: 'en' },
  ];

  redeem_result: RedeemPrepaidCodeResponse;
  show_result: boolean = false;
  constructor(
    private store: Store,
    private formBuilder: FormBuilder,
    private codeService: CodeService
  ) {}
  onSubmit(event: SubmitEvent): void {
    this.show_result = false;
    const code: RedeemPrepaidCodeRequest = {
      code: this.codeForm.get('code')?.value!,
      user_id: this.codeForm.get('user_id')?.value!,
      language: this.codeForm.get('language')?.value!,
      deduct_value: this.codeForm.get('deduct_value')?.value!,
      transaction_id: this.codeForm.get('transaction_id')?.value!,
      pin_code: this.codeForm.get('pin_code')?.value!,
      is_prepaid: true,
    };
    this.store.dispatch(openLoadingDialog());
    this.codeService.redeem(code).subscribe((res) => {
      if (res.ok) {
        this.show_result = true;
        this.redeem_result = res.result;
        this.store.dispatch(closeLoadingDialog());
      }
    });
  }
}
