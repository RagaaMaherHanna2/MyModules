import { BaseResponse } from './../../../../models/responses/base-response.model';
import { WalletService } from './../../../services/wallet/wallet.service';
import { openLoadingDialog, closeLoadingDialog } from 'src/store/loadingSlice';
import {
  BankTransfer,
  BankDetails,
  DEPOSIT_TYPE,
} from './../../../../models/wallet/models';

import { Router } from '@angular/router';
import { MessageService, ConfirmationService } from 'primeng/api';
import { Component, OnInit } from '@angular/core';
import { environment } from 'src/environments/environment';
import { FormBuilder, Validators } from '@angular/forms';
import { Store } from '@ngrx/store';
@Component({
  selector: 'app-charge-wallet',
  templateUrl: './charge-wallet.component.html',
  styleUrls: ['./charge-wallet.component.scss'],
  providers: [ConfirmationService, MessageService],
})
export class ChargeWalletComponent implements OnInit {
  companyBankDetails: BankDetails = {} as BankDetails;
  item: BankTransfer = {} as BankTransfer;
  serviceProviderBanks: any = {};
  serviceProviderBanksList: any = {};
  bankAccounts: any = {};
  file: any | undefined;
  fileUploaded: boolean = false;
  selectedFile: any[] = [];
  toBankSelected: any;
  fromBankSelected: any;
  maxFileSize = environment.MAX_UPLOADED_FILE_SIZE;
  chargeWalletForm = this.formBuilder.group({
    bank: ['', [Validators.required]],
    toBanks: [null, [Validators.required]],
    amount: [null, [Validators.required, Validators.min(1)]],
  });

  constructor(
    private walletService: WalletService,
    private messageService: MessageService,
    private route: Router,
    private formBuilder: FormBuilder,
    private readonly store: Store<{}>
  ) {}

  ngOnInit(): void {
    this.walletService.getServiceProviderBankList().subscribe((res) => {
      if (res.ok) {
        if (!res.result || Object.keys(res.result).length === 0) {
          this.serviceProviderBanksList = [];
        } else {
          this.serviceProviderBanksList = res.result;
        }
      }
      this.serviceProviderBanks = this.serviceProviderBanksList.map(
        (res: BankDetails) => {
          return {
            label: res.bank_name + ': Account: ' + res.acc_number,
            value: res.id,
          };
        }
      );
    });

    this.walletService
      .getBankList()
      .subscribe((res: BaseResponse<BankDetails[]>) => {
        if (res.ok) {
          if (!res.result || Object.keys(res.result).length === 0) {
            this.bankAccounts = [];
          } else {
            this.bankAccounts = res.result;
          }
        }
        this.bankAccounts = this.bankAccounts.map((res: BankDetails) => {
          return {
            label: res.bank_name + ': Account: ' + res.acc_number,
            value: res.id,
          };
        });
      });
  }
  onUpload(event: any) {
    let me = this;
    this.item.bankTransferImage = undefined;
    let file = event.files[0];
    let reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function () {
      let f = reader.result as string;
      let solution = f.split('base64,');
      let obj = { file: solution[1] };
      me.item.bankTransferImage = obj;
      me.fileUploaded = true;
    };
  }
  onClear() {
    this.item.bankTransferImage = null;
    this.fileUploaded = false;
  }
  submit() {
    this.item.toBank = this.toBankSelected;
    this.item.bank = this.fromBankSelected;
    this.item.type = DEPOSIT_TYPE;
    this.store.dispatch(openLoadingDialog());
    this.walletService.addBankTransfer(this.item).subscribe((res: any) => {
      this.store.dispatch(closeLoadingDialog());
      if (res.ok) {
        this.messageService.add({
          severity: 'success',
          summary: 'Successful',
          detail:
            'Your request is submitted successfully, we will review it and confirm it ASAP',
          life: 3000,
        });
        this.route.navigate(['dashboard/wallet/view-charge-request']);
      }
    });
  }
  updateBankDetails(bankId: number) {
    console.log(this.serviceProviderBanks);
    this.companyBankDetails = this.serviceProviderBanksList.filter(
      (item: { id: number }) => item.id === bankId
    )[0];
  }
}
