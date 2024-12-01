import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { MessageService } from 'primeng/api';
import { InvoicesService } from 'src/app/services/invoices/invoices.service';
import { WalletService } from 'src/app/services/wallet/wallet.service';
import { environment } from 'src/environments/environment';
import { Bill } from 'src/models/invoices/invoices.model';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { BankDetails, BankTransfer, BankTransferRequest, DEPOSIT_TYPE, INVOICE_PAYMENT_TYPE } from 'src/models/wallet/models';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-bank-transfer-pay',
  templateUrl: './bank-transfer-pay.component.html',
  styleUrls: ['./bank-transfer-pay.component.scss']
})
export class BankTransferPayComponent {
  companyBankDetails: BankDetails = {} as BankDetails;
  item: BankTransfer = {} as BankTransfer;
  serviceProviderBanks: any = {};
  serviceProviderBanksList: any = {};
  bankAccounts: any = {};
  bankAccountsList: any = {};
  file: any | undefined;
  fileUploaded: boolean = false;
  selectedFile: any[] = [];
  toBankSelected: any;
  fromBankSelected: any;
  maxFileSize = environment.MAX_UPLOADED_FILE_SIZE;
  chargeWalletForm = this.formBuilder.group({
    bank: ['', [Validators.required]],
    toBanks: [null, [Validators.required]],
  });
  bill: Bill;
  constructor(
    private invoicesService: InvoicesService,
    private walletService: WalletService,
    private messageService: MessageService,
    private route: Router,
    private formBuilder: FormBuilder,
    private readonly store: Store<{}>,
    private activatedRoute: ActivatedRoute
  ) { }

  ngOnInit(): void {
      this.activatedRoute.params.subscribe((params) => {
        this.invoicesService.getBills(0, 0, Number(params['id'])).subscribe((res) => {
          if (res.ok) {
            this.bill = res.result.data[0];
          }
        });
      });
    
    this.walletService.getBankList().subscribe((res) => {
      if (res.ok) {
        if (!res.result || Object.keys(res.result).length === 0) {
          this.serviceProviderBanksList = [];
        } else {
          this.serviceProviderBanksList = res.result;
        }
  }
  this.serviceProviderBanks = this.serviceProviderBanksList.map((res: BankDetails) => {
    return {
      label: res.bank_name + ': Account: ' + res.acc_number,
      value: res.id,
    };
  });
});

    this.walletService
      .getCompanyBankList()
      .subscribe((res: BaseResponse<BankDetails[]>) => {
        if (res.ok) {
          if (!res.result || Object.keys(res.result).length === 0) {
            this.bankAccountsList = [];
          } else {
            this.bankAccountsList = res.result;
          }
        }
        this.bankAccounts = this.bankAccountsList.map((res: BankDetails) => {
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

  isSubmitButtonDisabled(): boolean {
    if (!this.toBankSelected || this.toBankSelected === 0) {
      return true;
    }
    if (!this.fromBankSelected || this.fromBankSelected === 0) {
      return true;
    }
    if (
      !this.item.bankTransferImage?.file ||
      this.item.bankTransferImage?.file === ''
    ) {
      return true;
    }

    // if (
    //   !this.item.transferAmount ||
    //   this.item.transferAmount === 0 ||
    //   isNaN(this.item.transferAmount)
    // ) {
    //   return true;
    // }
    return false;
  }
  submit() {
    this.item.toBank = this.toBankSelected;
    this.item.bank = this.fromBankSelected;
    this.item.type = INVOICE_PAYMENT_TYPE;
    this.item.transferAmount = this.bill.total;
    this.item.invoice_id  = this.bill.id
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
        this.route.navigate(['dashboard/invoices/bills']);
      }
    });
  }
  updateBankDetails(bankId: number){
    console.log(this.bankAccountsList)
    this.companyBankDetails = this.bankAccountsList.filter((item: { id: number; }) => item.id === bankId)[0];
  }
}
