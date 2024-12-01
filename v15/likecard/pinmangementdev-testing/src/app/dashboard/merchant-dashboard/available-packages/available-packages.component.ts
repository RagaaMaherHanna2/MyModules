import { ActivatedRoute } from '@angular/router';
import { ExcelService } from './../../../services/excel.service';
import { MerchantService } from '../../../services/Merchant/merchant.service';
import { FormBuilder, FormControl, Validators } from '@angular/forms';
import {
  MerchantProductDetails,
  MerchantProductFilter,
  PrepaidPullCodeRequest,
  PullCodeRequest,
} from './../../../../models/Merchant/models';
import { Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';
import { Package } from 'src/models/package/models';
import { PackageService } from 'src/app/services/Package/package.service';
import { setBalance } from 'src/store/balanceSlice';
import { environment } from 'src/environments/environment';
import { WalletService } from 'src/app/services/wallet/wallet.service';
import { PermissionService } from 'src/app/services/permission/permission.service';

@Component({
  selector: 'app-available-packages',
  templateUrl: './available-packages.component.html',
  styleUrls: ['./available-packages.component.scss'],
})
export class AvailablePackagesComponent implements OnInit {
  product: MerchantProductDetails;
  showPullCodeModal: boolean = false;
  pullCodeMerchantForm = this.formBuilder.group({
    quantity: [0, [Validators.required]],
  });
  locale = $localize.locale;
  userCurrency: string =
    localStorage.getItem(environment.CURRENCY_SYMBOL) || 'null';
  hasPullPermission: boolean = false;

  constructor(
    private formBuilder: FormBuilder,
    private service: MerchantService,
    private excelService: ExcelService,
    private store: Store,
    private activatedRoute: ActivatedRoute,
    private packageService: PackageService,
    private walletService: WalletService,
    private permissionService: PermissionService
  ) {}

  checkPermission(Code: string): boolean {
    return this.permissionService.checkUserPermission(Code);
  }

  get_has_serial_label(has_serial: boolean) {
    if (has_serial) return $localize`HAS VOUCHER`;
    else return $localize``;
  }
  show_modal_pull_code() {
    this.showPullCodeModal = true;
  }
  ngOnInit(): void {
    this.hasPullPermission = this.checkPermission('1.2');
    this.activatedRoute.params.subscribe((id) => {
      let input: MerchantProductFilter = {
        id: +id['id'],
      };
      this.service.detail(input).subscribe((res) => {
        this.product = res.result.data[0];
        if (this.product.product_details.is_prepaid) {
          this.pullCodeMerchantForm.addControl(
            'email' as any,
            new FormControl(null, [Validators.required, Validators.email])
          );
          this.pullCodeMerchantForm.controls['quantity'].setValidators([
            Validators.min(1),
            Validators.max(50000),
          ]);
        }
      });
    });
  }
  isSubmitButtonDisabled() {
    return false;
  }

  getPackageCodes(): void {
    this.store.dispatch(openLoadingDialog());
    this.packageService
      .listCode({
        reference: undefined,
        limit: Number.MAX_SAFE_INTEGER,
        offset: 0,
        from: '',
        name: '',
        product: [],
        sorting: '',
        status: [],
        to: '',
      })
      .subscribe((res) => {
        if (res.ok) {
          this.excelService.convertJSONtoExcel(
            res.result.data,
            [],
            `${this.product.product} codes`
          );
        }
      });
  }
  submit() {
    this.showPullCodeModal = false;
    this.store.dispatch(openLoadingDialog());
    let value = this.pullCodeMerchantForm.value;
    if (this.product.product_details.is_prepaid) {
      let input: PrepaidPullCodeRequest = {
        product: this.product.product_details.id,
        quantity: value.quantity!,
        email_id: this.pullCodeMerchantForm.get('email')?.value,
      };
      this.pullCode(input);
    } else {
      let input: PullCodeRequest = {
        product: this.product.product_details.id,
        quantity: value.quantity!,
      };
      this.pullCode(input);
    }
  }

  pullCode(input: any) {
    this.service.pullCodes(input).subscribe((res) => {
      if (res.ok) {
        const pulled_serials = res.result.pulled_serials.map((item) => {
          const {
            serial_number: voucher_number,
            serial_code: voucher_code,
            ...rest
          } = item;
          return { voucher_number, voucher_code, ...rest };
        });

        this.excelService.convertJSONtoExcel(
          pulled_serials,
          [],
          `${
            this.product.product_details.name ?? ''
          } Pulled Codes - (${new Date()
            .toLocaleString()
            .replace(/\//g, '-')
            .replace(/:/g, ';')
            .replace(',', ' ')})`
        );
        this.service
          .detail({
            id: this.product.id,
          })
          .subscribe((res) => {
            if (res.ok) {
              this.product = res.result.data[0];

              this.store.dispatch(closeLoadingDialog());
            }
          });
        this.walletService.getUserBalance().subscribe((res) => {
          if (res.ok) {
            const balance =
              res.result.balance +
              +(localStorage.getItem(environment.BALANCE_KEY) ?? 0);
            this.store.dispatch(
              setBalance({ balance, currency: res.result.currency })
            );
          }
        });
      }
    });
  }
  getProdutType(item: any) {
    if (item.is_prepaid) return $localize`Prepaid Card`;
    else return $localize`Voucher`;
  }

  generatePerfix(type: string | undefined) {
    return type === 'percent' ? '%' : '$';
  }
  getProductExpiryPeriodValue(expiry_period: any) {
    if (expiry_period > 0) {
      return expiry_period;
    } else if (expiry_period === 0) {
      return 'unlimited';
    }
  }
  getFoodicsDiscountType(discountTypeId: string) {
    if (discountTypeId === '1') return $localize`Order Level`;
    else return $localize`Product Level`;
  }
}
