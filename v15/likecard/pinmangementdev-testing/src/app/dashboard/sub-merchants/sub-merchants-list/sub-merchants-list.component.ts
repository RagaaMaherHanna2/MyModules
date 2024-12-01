import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { SubMerchantsService } from 'src/app/services/sub-merchants/sub-merchants.service';
import { environment } from 'src/environments/environment';
import {
  MerchantInvite,
  MerchantsInviteList,
} from 'src/models/invites/invites.model';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { Store } from '@ngrx/store';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-merchants-list',
  templateUrl: './sub-merchants-list.component.html',
  styleUrls: ['./sub-merchants-list.component.scss'],
})
export class SubMerchantsListComponent {
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

  constructor(
    private subMerchantsService: SubMerchantsService,
    private router: Router,
    private formBuilder: FormBuilder,
    private messageService: MessageService,
    private store: Store
  ) {}

  goToDetails(item: MerchantsInviteList) {
    this.router.navigate([`/dashboard/sub-merchants/details/${item.id}`]);
  }

  // getInvitations(): void {
  //   this.loading = true;
  //   this.merchantsService
  //     .getInvitesList(this.offset, this.pageSize)
  //     .subscribe((res) => {
  //       if (res.ok) {
  //         this.merchants = res.result;
  //       }
  //       this.loading = false;
  //     });
  // }

  getCreatedSubMerchant(): void {
    this.loading = true;
    this.subMerchantsService
      .getCreatedSubMerchant(this.offset, this.pageSize)
      .subscribe((res) => {
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
    this.getCreatedSubMerchant();
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
    this.subMerchantsService.createSubMerchant(this.item).subscribe((res) => {
      this.store.dispatch(closeLoadingDialog());
      if (res.ok) {
        this.messageService.add({
          severity: 'success',
          summary: 'Successful',
          detail: $localize`Sub Merchant Created Successfully`,
          life: 3000,
        });
        this.hideDialog();
        this.getCreatedSubMerchant();
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
}
