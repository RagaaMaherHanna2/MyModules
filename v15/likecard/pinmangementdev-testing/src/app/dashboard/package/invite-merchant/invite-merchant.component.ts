import { openLoadingDialog, closeLoadingDialog } from 'src/store/loadingSlice';
import { getISODate } from 'src/app/shared/utils/date';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { Store } from '@ngrx/store';
import { PackageService } from './../../../services/Package/package.service';
import { MessageService } from 'primeng/api';
import { Router, ActivatedRoute } from '@angular/router';
import { Validators, FormBuilder } from '@angular/forms';
import {
  inviteMerchantToProduct,
} from './../../../../models/package/models';
import { Component } from '@angular/core';
import { UserService } from 'src/app/services/User/user.service';
import { TaxesService } from 'src/app/services/taxes/taxes.service';
import { name } from 'src/store/accessRightSlice';

@Component({
  selector: 'app-invite-merchant',
  templateUrl: './invite-merchant.component.html',
  styleUrls: ['./invite-merchant.component.scss'],
})
export class InviteMerchantComponent {
  taxOptions: any = [{ optionLabel: $localize`No Tax`, id: undefined}];
  merchant: inviteMerchantToProduct = {} as inviteMerchantToProduct;
  fetchingMerchant: boolean = false;
  inviteMerchantForm = this.formBuilder.group({
    merchant: ['', [Validators.required]],
    price: [0, [Validators.required]],
    limit: [0, [Validators.required]],
    tax: [undefined, []],
    unlimited: [false],
  });
  submitted: boolean = false;
  productId: string;
  merchantInfo: {
    found: boolean;
    name: string;
  } = {
    found: false,
    name: $localize`Please enter a reference`,
  };
  constructor(
    private router: Router,
    private formBuilder: FormBuilder,
    private messageService: MessageService,
    private packageService: PackageService,
    private userService: UserService,
    private taxesService: TaxesService,
    private activatedRoute: ActivatedRoute,
    private readonly store: Store<{}>
  ) {}
  ngOnInit(): void {
    this.activatedRoute.params.subscribe((id) => {
      this.productId = id['reference'];
    });

      this.taxesService.listTaxes(undefined).subscribe((res) => {
        this.taxOptions.push(...res.result.data.map(r => ({...r, optionLabel: `${r.name}(${r.amount}${r.amount_type === 'percent' ? '%' : '$'})`})));
      });



  }
  getMerchantInfo(event: any): void {
    if (event.target.value) {
      this.fetchingMerchant = true;
      this.inviteMerchantForm.controls.merchant.disable();
      this.userService
        .getUserByReference({ reference: event.target.value })
        .subscribe((res) => {
          setTimeout(() => {}, 1000);
          if (!res.ok) {
            this.merchantInfo.found = false;
            this.merchantInfo.name = $localize`Please enter a correct reference`;
            setTimeout(() => {
              this.inviteMerchantForm.controls.merchant.setErrors({
                notFound: true,
              });
            }, 0);
          } else {
            this.merchantInfo.found = true;
            this.merchantInfo.name = res.result.name;
          }

          this.fetchingMerchant = false;
          this.inviteMerchantForm.controls.merchant.enable();
        });
    }
  }

  submit() {
    this.submitted = true;

    let value = this.inviteMerchantForm.value;
    this.merchant.price = value.price ?? 0.0;
    if (!value.unlimited) {
      this.merchant.limit = value.limit ?? 0;
    }
    if (value.tax) {
      this.merchant.tax_id = value.tax ?? 0;
    }
    this.merchant.unlimited = value.unlimited!;
    this.merchant.merchant = value.merchant as string;
    this.merchant.product = this.productId;

    this.store.dispatch(openLoadingDialog());
    this.packageService.inviteMerchant(this.merchant).subscribe((res) => {
      this.store.dispatch(closeLoadingDialog());
      if (res.ok) {
        this.messageService.add({
          severity: 'success',
          summary: $localize`Successful`,
          detail: $localize`Merchant Invited successfully`,
          life: 3000,
        });
        this.router.navigate(['dashboard/product/details/', this.productId]);
      }
    });
  }
  isSubmitButtonDisabled() {
    return false;
  }
  changeLimitState(event: { checked: boolean }): void {
    if (event.checked) {
      this.inviteMerchantForm.controls.limit.disable();
      return;
    }
    this.inviteMerchantForm.controls.limit.enable();
  }
}
function getTaxes() {
  throw new Error('Function not implemented.');
}

