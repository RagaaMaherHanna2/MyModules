import { openLoadingDialog, closeLoadingDialog } from 'src/store/loadingSlice';
import { getISODate } from 'src/app/shared/utils/date';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { Store } from '@ngrx/store';
import { Router, ActivatedRoute } from '@angular/router';
import { Validators, FormBuilder } from '@angular/forms';
import { MessageService } from 'primeng/api';
import { Component } from '@angular/core';
import { ProductService } from 'src/app/services/Product';
import { MerchantProductInvitation } from 'src/models/Product/models';
import { PackageService } from 'src/app/services/Package/package.service';
import { closeErrorDialog, openErrorDialog } from 'src/store/errorSlice';
import { EditMerchantInvitation } from 'src/models/package/models';

@Component({
  selector: 'app-edit-merchant',
  templateUrl: './edit-merchant.component.html',
  styleUrls: ['./edit-merchant.component.scss'],
  providers: [MessageService],
})
export class EditMerchantComponent {
  merchantInvitation: MerchantProductInvitation =
    {} as MerchantProductInvitation;
  productId: number = -1;
  editMerchantForm = this.formBuilder.group({
    reference: [{ value: '', disabled: true }, [Validators.required]],
    name: [{ value: '', disabled: true }, [Validators.required]],
    price: [0, [Validators.required, Validators.min(0)]],
    limit: [0, [Validators.required]],
    tax: [''],
    unlimited: [false],
    quantity: this.formBuilder.group({
      type: ['add', [Validators.required]],
      amount: [0, [Validators.required, Validators.min(0)]],
    }),
  });
  merchant_invite_id: number;
  minDate: Date = new Date();
  constructor(
    private router: Router,
    private formBuilder: FormBuilder,
    private messageService: MessageService,
    private productService: ProductService,
    private activatedRoute: ActivatedRoute,
    private packageService: PackageService,
    private readonly store: Store<{}>
  ) {}


  formatedTax: String = ''



  ngOnInit(): void {
    this.activatedRoute.params.subscribe((params) => {
      this.productId = +params['product_id'];
      this.productService.getProductDetails(this.productId).subscribe((res) => {
        console.log(res);

        const product = res.result.data[0];
        if (product) {
          this.merchantInvitation = product.invited_merchant.filter(
            (invitation) => invitation.id === +params['invite_id']
          )[0];

          if (this.merchantInvitation) {
            this.formatedTax =this.merchantInvitation?.tax_id?.name
            ? `${this.merchantInvitation.tax_id.name}(${this.merchantInvitation.tax_id.amount}${this.merchantInvitation.tax_id.amount_type === 'percent' ? '%' : '$'})`
            : $localize`No Tax`,
            console.log(this.merchantInvitation)
            this.editMerchantForm.patchValue({
              price: this.merchantInvitation.price ?? 0,
              reference: this.merchantInvitation.merchant.reference,
              name: this.merchantInvitation.merchant.name,
              tax: this.merchantInvitation.tax_id
              ? `${this.merchantInvitation.tax_id.name}(${this.merchantInvitation.tax_id.amount}${this.merchantInvitation.tax_id.amount_type === 'percent' ? '%' : '$'})`
              : '',
              limit: this.merchantInvitation.limit,
              unlimited: this.merchantInvitation.unlimited,
            });
            if (this.merchantInvitation.unlimited) {
              this.editMerchantForm.controls.quantity.disable();
            }
          } else {
            this.handleWrongIds();
          }
        } else {
          this.handleWrongIds();
        }
      });
    });
  }
  handleWrongIds(): void {
    this.store.dispatch(
      openErrorDialog({
        message: $localize`There was an error, please try again`,
      })
    );
    setTimeout(() => {
      this.router.navigate(['/dashboard/product/list']);
      this.store.dispatch(closeErrorDialog());
    }, 3000);
  }
  submit() {
    let value = this.editMerchantForm.value;
    const bodyRequest: EditMerchantInvitation = {
      id: this.merchantInvitation.id,
      unlimited: value.unlimited!,
    };
    if (this.editMerchantForm.controls.price.dirty && value.price) {
      bodyRequest.price = value.price;
    }
    if (!value.unlimited && value.quantity && value.quantity.amount) {
      if (value.quantity.type === 'add') {
        bodyRequest.quantity = value.quantity.amount;
      } else {
        bodyRequest.quantity = -value.quantity.amount;
      }
    }    this.store.dispatch(openLoadingDialog());

    this.packageService
      .editInviteMerchant(bodyRequest)
      .subscribe((res) => {
        this.store.dispatch(closeLoadingDialog());
        if (res.ok) {
          this.messageService.add({
            severity: 'success',
            summary: 'Successful',
            detail: $localize`Merchant Invite Edited successfully`,
            life: 3000,
          });
          this.router.navigate([
            `/dashboard/product/details/${this.productId}`,
          ]);
        } else {
          this.messageService.add({
            severity: 'error',
            summary: $localize`Merchant Invite Editing Failed`,
            detail: res.message,
            life: 3000,
          });
        }
      });
  }

  changeLimitState(event: { checked: boolean }): void {
    if (event.checked) {
      this.editMerchantForm.controls.quantity.disable();
      return;
    }
    this.editMerchantForm.controls.quantity.enable();
  }
}
