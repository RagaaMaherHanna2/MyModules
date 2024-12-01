import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { VendorsService } from 'src/app/services/vendors/vendors.service';
import { environment } from 'src/environments/environment';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { GetVendorsBody, Vendor } from 'src/models/vendors/vendor';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-vendors',
  templateUrl: './vendors.component.html',
  styleUrls: ['./vendors.component.scss'],
})
export class VendorsComponent {
  vendors: GetListResponse<Vendor> = {
    totalCount: 0,
    data: [],
  };
  pageSize: number = environment.PAGE_SIZE;
  loading: boolean = true;
  offset: number = 0;
  dialog: boolean = false;
  showAddModal: boolean = false;
  vendorForm = this.formBuilder.group({
    name: ['', [Validators.required]],
  });
  item: Vendor = {} as Vendor;
  filter: string = '';

  constructor(
    private vendorsService: VendorsService,
    private router: Router,
    private formBuilder: FormBuilder,
    private messageService: MessageService,
    private store: Store
  ) {}

  changePage(event: { first: number; rows: number }): void {
    this.offset = event.first;
    this.getVendors();
  }

  openNewVendorDialog() {
    this.item = {} as Vendor;
    this.dialog = true;
    this.showAddModal = true;
  }

  hideDialog() {
    this.showAddModal = false;
  }

  submit(): void {
    this.store.dispatch(openLoadingDialog());
    this.vendorsService.createVendor(this.item.name).subscribe((res) => {
      this.store.dispatch(closeLoadingDialog());
      if (res.ok) {
        this.messageService.add({
          severity: 'success',
          summary: 'Successful',
          detail: $localize`Vendor Created Successfully`,
          life: 3000,
        });
        this.hideDialog();
        this.getVendors();
      } else {
        this.messageService.add({
          severity: 'error',
          summary: $localize`Adding Vendor Failed`,
          detail: res.message,
          life: 3000,
        });
      }
    });
  }
  reinitVendorForm() {
    this.vendorForm = this.formBuilder.group({
      name: ['', [Validators.required]],
    });
  }
  applyFilter(event: any) {
    this.filter = event.target.value;
    let ev: LazyLoadEvent = {};
    ev.first = 0;
    ev.sortField = '';
    this.getVendors();
  }

  getVendors(): void {
    this.loading = true;
    let body: GetVendorsBody = {
      limit: environment.PAGE_SIZE,
      offset: this.offset,
      name: this.filter,
    };

    this.vendorsService.getVendors(body).subscribe((res) => {
      if (res.ok) {
        this.vendors = res.result;
      }
      this.loading = false;
    });
  }
}
