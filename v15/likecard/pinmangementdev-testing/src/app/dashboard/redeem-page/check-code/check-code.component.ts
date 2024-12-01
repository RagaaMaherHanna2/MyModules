import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { MessageService } from 'primeng/api';
import { RedeemService } from 'src/app/services/redeem/redeem.service';
import { SecretCode } from 'src/models/Product/models';
import { code } from 'src/models/serial/model';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-check-code',
  templateUrl: './check-code.component.html',
  styleUrls: ['./check-code.component.scss'],
})
export class CheckCodeComponent {
  constructor(
    private formBuilder: FormBuilder,
    private redeemService: RedeemService,
    private store: Store,
    private messageService: MessageService,
    private activatedRoute: ActivatedRoute,
    private router: Router
  ) {}
  redeemForm = this.formBuilder.group({
    codes: ['', Validators.required],
    sp_hash: ['', []],
    secret: ['', []],
  });
  codes: code[];
  sku: string;
  isHaveSecret: boolean = false;

  ngOnInit() {
    this.activatedRoute.params.subscribe((params) => {
      console.log(params);
      this.redeemService
        .authServiceProviderWithHash(params['sp-hash'], params['product_sku'])
        .subscribe((res) => {
          if (res.ok) {
            this.redeemForm.patchValue({ sp_hash: params['sp-hash'] });
            this.sku = params['product_sku'];

            if (res.result.codes_additional_value === 'secret') {
              this.isHaveSecret = true;
              this.redeemForm.controls['secret'].addValidators([
                Validators.required,
              ]);
            }
          }
        });
    });
  }

  onSubmit(event: SubmitEvent): void {
    let codesList = this.redeemForm.value.codes!.split(/\r?\n/);
    codesList = codesList.filter((code) => code.trim() !== '');
    this.store.dispatch(openLoadingDialog());
    let codes: SecretCode[] = [
      { code: codesList[0], secret: this.redeemForm.value.secret! },
    ];
    this.redeemService
      .checkCodesWithHash({
        codes: codes,
        sp_hash: this.redeemForm.value.sp_hash,
        sku: this.sku,
      })
      .subscribe((res) => {
        if (res.ok) {
          this.codes = res.result;
          this.store.dispatch(closeLoadingDialog());

          setTimeout(() => {
            const resultDiv = document.getElementById('resultDiv');
            if (resultDiv) {
              resultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
          }, 0);
        }
      });
  }

  onCopy(link: string): void {
    window.navigator.clipboard.writeText(link);
    this.messageService.add({
      icon: 'pi pi-copy',
      summary: `Copied`,
      detail: `How To Use Link Copied Successfully`,
      severity: 'info',
    });
  }
  next(): void {
    let productType = this.codes[0]['product_type'] === 'serial' ? 0 : 1;
    this.router.navigate([
      `/redeem-page/${this.redeemForm.value.sp_hash}/${this.sku}/redeem-code/${productType}`,
    ]);
  }
}
