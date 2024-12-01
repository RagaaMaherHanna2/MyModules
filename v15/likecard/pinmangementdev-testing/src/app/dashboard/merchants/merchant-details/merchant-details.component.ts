import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { MessageService } from 'primeng/api';
import { PackageService } from 'src/app/services/Package/package.service';
import { ProductService } from 'src/app/services/Product';
import { MerchantsService } from 'src/app/services/merchants/merchants.service';
import { TaxesService } from 'src/app/services/taxes/taxes.service';
import { environment } from 'src/environments/environment';
import {
  MerchantProductInvitation,
  shortProduct,
} from 'src/models/Product/models';
import {
  GetMerchantsBody,
  MerchantsInviteList,
} from 'src/models/invites/invites.model';
import {
  EditMerchantInvitation,
  inviteMerchantToProduct,
} from 'src/models/package/models';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-merchant-details',
  templateUrl: './merchant-details.component.html',
  styleUrls: ['./merchant-details.component.scss'],
})
export class MerchantDetailsComponent implements OnInit {
  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private merchantsService: MerchantsService,
    private store: Store,
    private formBuilder: FormBuilder,
    private taxesService: TaxesService,
    private productService: ProductService,
    private packageService: PackageService,
    private messageService: MessageService
  ) {}
  merchantId: number;
  invite: MerchantsInviteList;
  locale = $localize.locale;
  submitted: boolean;
  enabledInvitations: number;
  redeemedCodes: number;
  balance: number;
  showAddProductModal: boolean = false;
  showEditInvitationModal: boolean = false;
  availableProducts: shortProduct[];
  taxOptions: any = [{ optionLabel: $localize`No Tax`, id: undefined }];
  invitation: inviteMerchantToProduct = {} as inviteMerchantToProduct;
  inviteProductForm = this.formBuilder.group({
    product: ['', [Validators.required]],
    price: [, [Validators.required], Validators.min(0.1)],
    limit: [0, [Validators.required]],
    tax: [undefined, []],
    unlimited: [false],
  });
  editInviteProductForm = this.formBuilder.group({
    product: [{ value: '', disabled: true }, [Validators.required]],
    productPurchaseCost: [''],
    name: [{ value: '', disabled: true }, [Validators.required]],
    price: [0.1, [Validators.required, Validators.min(0.1)]],
    limit: [0, [Validators.required]],
    tax: [''],
    unlimited: [false],
    quantity: this.formBuilder.group({
      type: ['add', [Validators.required]],
      amount: [0, [Validators.required, Validators.min(0)]],
    }),
  });
  editedInvitation: MerchantProductInvitation = {} as MerchantProductInvitation;
  formatedTax: String = '';

  userCurrency: string =
    localStorage.getItem(environment.CURRENCY_SYMBOL) || 'null';
  selctedProduct: shortProduct[];
  selectedProductCost: string = '';

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      const id = +params['id'];

      if (id) {
        let body: GetMerchantsBody = {
          limit: environment.PAGE_SIZE,
          offset: 0,
          id: 0,
          name: '',
        };
        this.merchantsService.getCreatedMerchant(body).subscribe((res) => {
          if (res.ok) {
            this.getMerchantDetails(id);
          }
          this.taxesService.listTaxes(undefined).subscribe((res) => {
            this.taxOptions.push(
              ...res.result.data.map((r) => ({
                ...r,
                optionLabel: `${r.name} (${r.amount}${
                  r.amount_type === 'percent' ? '%' : '$'
                })`,
              }))
            );
          });
        });
      }
    });
  }

  getMerchantDetails(id: number) {
    this.enabledInvitations = 0;
    this.redeemedCodes = 0;
    this.balance = 0;
    let body: GetMerchantsBody = {
      limit: environment.PAGE_SIZE,
      offset: 0,
      id: id,
      name: '',
    };
    this.merchantsService.getCreatedMerchant(body).subscribe((res) => {
      if (res.ok) {
        this.invite = res.result.data.filter((item) => item.id === id)[0];
        if (this.invite.all_merchant_invitations.length > 0) {
          this.balance += this.invite.all_merchant_invitations[0].balance;
          this.invite.all_merchant_invitations.forEach((item) => {
            if (item.enabled) {
              this.enabledInvitations++;
            }
            this.redeemedCodes += item.pulled_serials_count;
          });
        }
      }
    });
  }
  inviteProduct() {
    this.hideEditInviteDialog();
    this.showAddProductModal = true;
    this.productService
      .getProductsNotInvitedToMerchant(this.invite.id)
      .subscribe((res) => {
        this.availableProducts = res.result.data;
        this.availableProducts.sort(function (a, b) {
          var textA = a.name.toUpperCase();
          var textB = b.name.toUpperCase();
          return textA < textB ? -1 : textA > textB ? 1 : 0;
        });
      });
  }
  hideInviteProductDialog() {
    this.showAddProductModal = false;
    this.submitted = false;
    this.inviteProductForm.reset();
  }
  submitInviteProduct() {
    this.submitted = true;
    let value = this.inviteProductForm.value;
    this.invitation.price = value.price ?? 0.0;
    if (!value.unlimited) {
      this.invitation.limit = value.limit ?? 0;
    }
    if (value.tax) {
      this.invitation.tax_id = value.tax ?? 0;
    }
    this.invitation.unlimited = value.unlimited!;
    this.invitation.merchant = this.invite.reference;
    this.invitation.product = value.product ?? '';

    this.store.dispatch(openLoadingDialog());
    this.packageService.inviteMerchant(this.invitation).subscribe((res) => {
      this.store.dispatch(closeLoadingDialog());
      if (res.ok) {
        this.messageService.add({
          severity: 'success',
          summary: $localize`Successful`,
          detail: $localize`Product added successfully`,
          life: 3000,
        });
        this.hideInviteProductDialog();
        this.getMerchantDetails(this.invite.id);
      }
    });
  }
  changeLimitState(event: { checked: boolean }): void {
    if (event.checked) {
      this.inviteProductForm.controls.limit.disable();
      return;
    }
    this.inviteProductForm.controls.limit.enable();
  }

  editInvite(invitation: MerchantProductInvitation): void {
    this.hideInviteProductDialog();
    this.showEditInvitationModal = true;
    this.editedInvitation = invitation;
    (this.formatedTax = this.editedInvitation?.tax_id?.name
      ? `${this.editedInvitation.tax_id.name} (${
          this.editedInvitation.tax_id.amount
        }${this.editedInvitation.tax_id.amount_type === 'percent' ? '%' : '$'})`
      : $localize`No Tax`),
      this.editInviteProductForm.patchValue({
        price: this.editedInvitation.price ?? 0,
        product: this.editedInvitation.product,
        productPurchaseCost:
          this.editedInvitation.product_details.purchase_cost,
        name: this.editedInvitation.product,
        tax: this.editedInvitation.tax_id
          ? `${this.editedInvitation.tax_id.name} (${
              this.editedInvitation.tax_id.amount
            }${
              this.editedInvitation.tax_id.amount_type === 'percent' ? '%' : '$'
            })`
          : '',
        limit: this.editedInvitation.limit,
        unlimited: this.editedInvitation.unlimited,
      });
    if (this.editedInvitation.unlimited) {
      this.editInviteProductForm.controls.quantity.disable();
    }
  }
  hideEditInviteDialog() {
    this.showEditInvitationModal = false;
    this.submitted = false;
    this.editInviteProductForm.reset();
  }
  changeInviteState(invitation: MerchantProductInvitation): void {
    this.store.dispatch(openLoadingDialog());
    this.packageService
      .editInviteMerchant({
        ...invitation,
        enabled: !invitation.enabled,
      })
      .subscribe((res) => {
        if (res.ok) {
          this.messageService.add({
            severity: 'success',
            summary: $localize`Success`,
            detail: $localize`Invite state changed successfully`,
          });
          this.store.dispatch(closeLoadingDialog());
          this.getMerchantDetails(this.invite.id);
        }
      });
  }

  submitEditInvitation() {
    let value = this.editInviteProductForm.value;
    const bodyRequest: EditMerchantInvitation = {
      id: this.editedInvitation.id,
      unlimited: value.unlimited!,
    };
    if (this.editInviteProductForm.controls.price.dirty && value.price) {
      bodyRequest.price = value.price;
    }
    if (!value.unlimited && value.quantity && value.quantity.amount) {
      if (value.quantity.type === 'add') {
        bodyRequest.quantity = value.quantity.amount;
      } else {
        bodyRequest.quantity = -value.quantity.amount;
      }
    }
    this.store.dispatch(openLoadingDialog());

    this.packageService.editInviteMerchant(bodyRequest).subscribe((res) => {
      this.store.dispatch(closeLoadingDialog());
      if (res.ok) {
        this.hideEditInviteDialog();
        this.messageService.add({
          severity: 'success',
          summary: 'Successful',
          detail: $localize`Product Invite Edited successfully`,
          life: 3000,
        });
        this.getMerchantDetails(this.invite.id);
      } else {
        this.messageService.add({
          severity: 'error',
          summary: $localize`Product Invite Editing Failed`,
          detail: res.message,
          life: 3000,
        });
      }
    });
  }

  editChangeLimitState(event: { checked: boolean }): void {
    if (event.checked) {
      this.editInviteProductForm.controls.quantity.disable();
      return;
    }
    this.editInviteProductForm.controls.quantity.enable();
  }

  getFormattedTax(invitation: MerchantProductInvitation) {
    let formattedTax = invitation?.tax_id?.name
      ? `${invitation.tax_id.name} (${invitation.tax_id.amount}${
          invitation.tax_id.amount_type === 'percent' ? '%' : '$'
        })`
      : $localize`No Tax`;
    return formattedTax;
  }
  updateCostPrice() {
    if (this.inviteProductForm.value.product) {
      this.selctedProduct = this.availableProducts.filter(
        (product) => product.id == this.inviteProductForm.value.product
      );
      this.selectedProductCost =
        this.selctedProduct.length > 0
          ? this.selctedProduct[0].purchase_cost + ' ' + this.userCurrency
          : '';
    }
  }
}
