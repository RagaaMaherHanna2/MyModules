import { WalletService } from './../../../services/wallet/wallet.service';
import { BankDetails } from './../../../../models/wallet/models';
import { Component, OnInit } from '@angular/core';
import { MessageService } from 'primeng/api';
import { FormBuilder, Validators } from '@angular/forms';
import { PermissionService } from 'src/app/services/permission/permission.service';

@Component({
  selector: 'app-bank-list',
  templateUrl: './bank-list.component.html',
  styleUrls: ['./bank-list.component.scss'],
})
export class BankListComponent implements OnInit {
  items: BankDetails[] = [];
  item: BankDetails = {
    acc_number: '',
    account_class: '',
    account_type: '',
    adib_swift_code: '',
    bank_name: '',
    bic: '',
    iban: '',
    id: 0,
  };
  submitted = false;
  dialog: boolean = false;
  loading: boolean = false;
  showEditAddModal: boolean = false;
  bankDetailsForm = this.formBuilder.group({
    bank_name: ['', [Validators.required]],
    bic: ['', [Validators.required]],
    acc_number: ['', [Validators.required]],
    account_type: ['', [Validators.required]],
    account_class: ['', [Validators.required]],
    iban: ['', [Validators.required]],
    adib_swift_code: ['', [Validators.required]],
  });
  constructor(
    private service: WalletService,
    private messageService: MessageService,
    private formBuilder: FormBuilder,
  ) {}

  ngOnInit(): void {
    this.loadList();
  }

  openNew() {
    this.item = {
      acc_number: '',
      account_class: '',
      account_type: '',
      adib_swift_code: '',
      bank_name: '',
      bic: '',
      iban: '',
      id: 0,
    } as BankDetails;
    this.submitted = false;
    this.showEditAddModal = true;
  }
  hideDialog() {
    this.showEditAddModal = false;
    this.submitted = false;
  }
  submit() {
    if (this.item.id ?? 0 > 0) {
      this.service.editBankInformation(this.item).subscribe((res) => {
        if (res.ok) {
          this.messageService.add({
            summary: $localize`Success`,
            detail: $localize`Bank Account Edited Successfully`,
            life: 3000,   icon: 'pi pi-check-circle',
            severity: 'success',
          });
          this.hideDialog();
          this.loadList();
        } else {
          this.messageService.add({
            severity: 'error',
            summary: $localize`Editing Bank Account Failed`,
            detail: res.message,
            life: 3000,
          });
        }
      });
    } else {
      this.service.addBankInformation(this.item).subscribe((res) => {
        if (res.ok) {
          this.messageService.add({
            severity: 'success',
            summary: $localize`Success`,
            detail: $localize`Bank Account Added Successfully`,
            life: 3000,
          });
          this.hideDialog();
          this.loadList();
        } else {
          this.messageService.add({
            severity: 'error',
            summary: $localize`Adding Bank Account Failed`,
            detail: res.message,
            life: 3000,
          });
        }
      });
    }
  }
  edit(item: BankDetails) {
    this.item = item;
    this.showEditAddModal = true;
  }
  loadList() {
    this.loading = true;
    this.service.getBankList().subscribe((res) => {
      if (res.ok) {
        if (
          !res.result ||
          Object.keys(res.result).length === 0 ||
          Object.getPrototypeOf(res.result) === Object.prototype
        ) {
          this.items = [];
        } else {
          this.items = res.result;
        }

        this.loading = false;
      }
    });
  }

}
