import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { MerchantsService } from 'src/app/services/merchants/merchants.service';
import { environment } from 'src/environments/environment';
import {
  GetMerchantsBody,
  MerchantInvite,
  MerchantsInviteList,
} from 'src/models/invites/invites.model';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { Store } from '@ngrx/store';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-merchants-list',
  templateUrl: './merchants-list.component.html',
  styleUrls: ['./merchants-list.component.scss'],
})
export class MerchantsListComponent {
  merchants: GetListResponse<MerchantsInviteList> = {
    totalCount: 0,
    data: [],
  };
  pageSize: number = environment.PAGE_SIZE;
  loading: boolean = true;
  offset: number = 0;
  item: MerchantInvite = {} as MerchantInvite;
  dialog: boolean = false;
  showAddModal: boolean = false;
  merchantForm = this.formBuilder.group({
    name: ['', [Validators.required]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required]],
  });
  userCurrency: string =
    localStorage.getItem(environment.CURRENCY_SYMBOL) || 'null';
  filter: string = '';

  constructor(
    private merchantsService: MerchantsService,
    private router: Router,
    private formBuilder: FormBuilder,
    private messageService: MessageService,
    private store: Store
  ) {}

  goToDetails(item: MerchantsInviteList) {
    this.router.navigate([`/dashboard/merchants/details/${item.id}`]);
  }

  getCreatedMerchant(): void {
    this.loading = true;
    let body: GetMerchantsBody = {
      limit: environment.PAGE_SIZE,
      offset: this.offset,
      id: 0,
      name: this.filter,
    };

    this.merchantsService.getCreatedMerchant(body).subscribe((res) => {
      if (res.ok) {
        this.merchants = res.result;
      }
      this.loading = false;
    });
  }

  getBalance(item: MerchantsInviteList): number {
    if (item.all_merchant_invitations.length > 0) {
      return item.all_merchant_invitations[0].balance;
    }
    return 0;
  }

  changePage(event: { first: number; rows: number }): void {
    this.offset = event.first;
    this.getCreatedMerchant();
  }

  openNewMerchant() {
    this.item = {} as MerchantInvite;
    this.dialog = true;
    this.showAddModal = true;
  }

  hideDialog() {
    this.showAddModal = false;
  }

  submit(): void {
    this.store.dispatch(openLoadingDialog());
    this.merchantsService.createMerchant(this.item).subscribe((res) => {
      this.store.dispatch(closeLoadingDialog());
      if (res.ok) {
        this.messageService.add({
          severity: 'success',
          summary: 'Successful',
          detail: $localize`Merchant Created Successfully`,
          life: 3000,
        });
        this.hideDialog();
        this.getCreatedMerchant();
      } else {
        this.messageService.add({
          severity: 'error',
          summary: $localize`Adding Merchant Failed`,
          detail: res.message,
          life: 3000,
        });
      }
    });
  }
  reinitMerchantForm() {
    this.merchantForm = this.formBuilder.group({
      name: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
    });
  }
  applyFilter(event: any) {
    this.filter = event.target.value;
    let ev: LazyLoadEvent = {};
    ev.first = 0;
    ev.sortField = '';
    this.getCreatedMerchant();
  }
}
