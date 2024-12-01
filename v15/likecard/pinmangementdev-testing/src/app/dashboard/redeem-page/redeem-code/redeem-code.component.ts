import { Component } from '@angular/core';
import {
  FormBuilder,
  FormControl,
  FormGroup,
  Validators,
} from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { MessageService } from 'primeng/api';
import { RedeemService } from 'src/app/services/redeem/redeem.service';
import {
  ProductAttribute,
  ProductAttributeValue,
} from 'src/models/Product/models';
import { PrepaidRedeemBodyWithHash } from 'src/models/prepaid/models';
import { SerialRedeemBodyWithHash } from 'src/models/serial/model';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-redeem-code',
  templateUrl: './redeem-code.component.html',
  styleUrls: ['./redeem-code.component.scss'],
})
export class RedeemCodeComponent {
  constructor(
    private store: Store,
    private activatedRoute: ActivatedRoute,
    private formBuilder: FormBuilder,
    private redeemService: RedeemService,
    private router: Router
  ) {}
  options = [
    { label: `True`, value: false },
    { label: `False`, value: true },
  ];
  isPrepaid: boolean;
  isRedeemed: boolean;
  remainingValue: number;
  serialMessage: string;
  isHaveSecret: boolean = false;
  isSubmitted: boolean = false;
  SpHash: string;
  SKU: string;

  serialRedeemForm = this.formBuilder.group({
    code: ['', Validators.required],
    sp_hash: ['', []],
    secret: ['', []],
  });
  prepaidRedeemForm = this.formBuilder.group({
    code: ['', Validators.required],
    pin_code: ['', Validators.required],
    user_id: ['', Validators.required],
    transaction_id: ['', Validators.required],
    deduct_value: [null, Validators.required],
    sp_hash: ['', []],
    secret: ['', []],
  });
  prepaidBody: PrepaidRedeemBodyWithHash = {} as PrepaidRedeemBodyWithHash;
  serialBody: SerialRedeemBodyWithHash = {} as SerialRedeemBodyWithHash;
  productAttributes: ProductAttribute[];
  ngOnInit() {
    window.onbeforeunload = () => {
      sessionStorage.setItem('redirectToFirstStep', 'true');
    };
    const parentRoute = this.activatedRoute.parent;
    if (parentRoute) {
      parentRoute.params.subscribe((params) => {
        this.SpHash = params['sp-hash'];
        this.SKU = params['product_sku'];
        this.serialRedeemForm.patchValue({ sp_hash: params['sp-hash'] });
        this.prepaidRedeemForm.patchValue({ sp_hash: params['sp-hash'] });
        this.redeemService
          .authServiceProviderWithHash(params['sp-hash'], params['product_sku'])
          .subscribe((res) => {
            if (res.ok) {
              if (res.result.codes_additional_value === 'secret') {
                this.isHaveSecret = true;
                if (this.isPrepaid) {
                  this.prepaidRedeemForm.controls['secret'].addValidators([
                    Validators.required,
                  ]);
                } else {
                  this.serialRedeemForm.controls['secret'].addValidators([
                    Validators.required,
                  ]);
                }
              } else {
                this.productAttributes = res.result.product_attributes[0];
                for (let attr of this.productAttributes) {
                  if (this.isPrepaid) {
                    const newFormGroup = new FormGroup({
                      ...this.prepaidRedeemForm.controls,
                      [attr.name]: new FormControl(
                        null,
                        attr.required ? Validators.required : []
                      ),
                    });
                    this.prepaidRedeemForm = newFormGroup;
                  } else {
                    const newFormGroup = new FormGroup({
                      ...this.serialRedeemForm.controls,
                      [attr.name]: new FormControl(
                        null,
                        attr.required ? Validators.required : []
                      ),
                    });
                    this.serialRedeemForm = newFormGroup;
                  }
                }
              }
            }
          });
      });
    }
    this.activatedRoute.params.subscribe((params) => {
      if (params['product_type'] == 1) {
        this.isPrepaid = true;
      } else {
        this.isPrepaid = false;
      }
    });
  }

  onSubmit(event: SubmitEvent): void {
    this.store.dispatch(openLoadingDialog());
    if (this.isPrepaid) {
      let value = this.prepaidRedeemForm.value;
      this.prepaidBody.code = value.code as string;
      this.prepaidBody.pin_code = value.pin_code as string;
      this.prepaidBody.user_id = value.user_id as string;
      this.prepaidBody.transaction_id = value.transaction_id as string;
      this.prepaidBody.deduct_value = value.deduct_value!;
      this.prepaidBody.sp_hash = value.sp_hash as string;
      this.prepaidBody.product_type = 'prepaid';
      if (this.isHaveSecret) {
        this.prepaidBody.secret = value.secret as string;
      }
      if (this.productAttributes && !this.isHaveSecret) {
        this.prepaidBody.product_attribute_values =
          this.getProductAttrWithValues(value);
      }
      this.redeemService
        .redeemPrepaidWithHash(this.prepaidBody)
        .subscribe((res) => {
          this.isSubmitted = true;
          if (res.ok) {
            this.store.dispatch(closeLoadingDialog());
            this.scrolToResult();
            this.isRedeemed = true;
            this.remainingValue = res.result.remaining_value;
          } else {
            this.isRedeemed = false;
          }
        });
    } else {
      let value = this.serialRedeemForm.value;
      this.serialBody.code = value.code as string;
      this.serialBody.sp_hash = value.sp_hash as string;
      this.serialBody.product_type = 'serial';
      if (this.isHaveSecret) {
        this.serialBody.secret = value.secret as string;
      }
      if (this.productAttributes && !this.isHaveSecret) {
        this.serialBody.product_attribute_values =
          this.getProductAttrWithValues(value);
      }

      this.redeemService
        .redeemSerialWithHash(this.serialBody)
        .subscribe((res) => {
          this.isSubmitted = true;
          if (res.ok) {
            this.store.dispatch(closeLoadingDialog());
            this.scrolToResult();
            this.isRedeemed = true;
            this.serialMessage = res.message;
          } else {
            this.isRedeemed = false;
            this.serialMessage = '';
          }
        });
    }
  }
  getProductAttrWithValues(value: any) {
    const productAttrWithValues = this.productAttributes.map((obj) => ({
      id: obj.id,
      value: value[obj.name],
    }));
    return productAttrWithValues;
  }
  navigateBack() {
    this.router.navigate([`redeem-page/${this.SpHash}/${this.SKU}`]);
  }
  scrolToResult() {
    setTimeout(() => {
      const resultDiv = document.getElementById('resultDiv');
      if (resultDiv) {
        resultDiv.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
        });
      }
    }, 0);
  }
}
