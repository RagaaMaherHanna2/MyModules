import { BaseResponse } from './../../../../models/responses/base-response.model';
import { WalletService } from './../../../services/wallet/wallet.service';
import {
  BankTransfer,
  BankDetails,
  CREDIT_TYPE,
} from './../../../../models/wallet/models';

import { Router } from '@angular/router';
import { MessageService, ConfirmationService } from 'primeng/api';
import { Component, OnInit } from '@angular/core';
import { environment } from 'src/environments/environment';
import { FormBuilder, Validators } from '@angular/forms';

@Component({
  selector: 'app-credit-wallet',
  templateUrl: './credit-wallet.component.html',
  styleUrls: ['./credit-wallet.component.scss'],
})
export class CreditWalletComponent implements OnInit {
  companyBankDetails: BankDetails = {} as BankDetails;
  item: BankTransfer = {} as BankTransfer;
  bankAccounts: any = {};
  selectedFile: any[] = [];
  toBankSelected: any;
  maxFileSize = environment.MAX_UPLOADED_FILE_SIZE;
  chargeWalletForm = this.formBuilder.group({
    bank: [null, [Validators.required]],
    amount: [null, [Validators.required, Validators.min(1)]],
  });

  constructor(
    private walletService: WalletService,
    private messageService: MessageService,
    private route: Router,
    private formBuilder: FormBuilder
  ) {}

  ngOnInit(): void {
    this.walletService
      .getBankList()
      .subscribe((res: BaseResponse<BankDetails[]>) => {
        this.bankAccounts = res.result.map((res: BankDetails) => {
          return {
            label: res.bank_name + ': Account: ' + res.acc_number,
            value: res.id,
          };
        });
      });
  }

  isSubmitButtonDisabled(): boolean {
    if (!this.toBankSelected || this.toBankSelected === 0) {
      return true;
    }
    if (
      !this.item.transferAmount ||
      this.item.transferAmount === 0 ||
      isNaN(this.item.transferAmount)
    ) {
      return true;
    }
    return false;
  }
  submit() {
    this.item.toBank = this.toBankSelected;
    this.item.type = CREDIT_TYPE;
    this.walletService.addBankTransfer(this.item).subscribe((res: any) => {
      if (res.ok) {
        this.messageService.add({
          severity: 'success',
          summary: 'Successful',
          detail:
            'Your request is submitted successfully, we will review it and confirm it ASAP',
          life: 3000,
        });
        this.route.navigate(['dashboard/wallet/view-credit-request']);
      }
    });
  }
}
