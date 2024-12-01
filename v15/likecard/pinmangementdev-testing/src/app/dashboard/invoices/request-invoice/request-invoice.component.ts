import { Component, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormBuilder,
  FormControl,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { MerchantsService } from 'src/app/services/merchants/merchants.service';
import { InvoicesService } from 'src/app/services/invoices/invoices.service';
import { MerchantsInviteList } from 'src/models/invites/invites.model';
import { RequestInvoiceBody } from 'src/models/invoices/invoices.model';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';
import { DatePipe } from '@angular/common';
import { MessageService } from 'primeng/api';

type RequestFormType = {
  merchant: FormControl<string | null>;
  date: FormControl<Date[] | null>;
};
@Component({
  selector: 'app-request-invoice',
  templateUrl: './request-invoice.component.html',
  styleUrls: ['./request-invoice.component.scss'],
})
export class RequestInvoiceComponent implements OnInit {
  invoiceRequestForm = this.formBuilder.group<RequestFormType>({
    merchant: new FormControl<string>('', [
      Validators.required,
      Validators.minLength(1),
    ]), // Set initial value and validators
    date: new FormControl<Date[]>(
      [],
      [Validators.required, this.isDateArrayValidator]
    ), // Set initial value and validators
  });
  minDate: Date = new Date();
  maxDate: Date = new Date();
  merchants: GetListResponse<MerchantsInviteList>;
  options: { name: string; reference: string }[] = [];

  constructor(
    private router: Router,
    private formBuilder: FormBuilder,
    private merchantsService: MerchantsService,
    private store: Store,
    private invoicesService: InvoicesService,
    private messageService: MessageService
  ) {}

  ngOnInit() {
    this.minDate.setDate(this.minDate.getDate() - 90);
    this.maxDate.setDate(this.maxDate.getDate() - 1);
    this.merchantsService.getInvitesList().subscribe((res) => {
      if (res.ok) {
        this.merchants = res.result;
        this.merchants.data.forEach((merchant) => {
          this.options.push({
            name: merchant.name!,
            reference: merchant.reference!,
          });
        });
      }
    });
  }

  isDateArrayValidator(control: AbstractControl): ValidationErrors | null {
    const value = control.value;
    if (value instanceof Array && value.length === 2) {
      for (let i = 0; i < 2; i++) {
        if (!(value[i] instanceof Date)) {
          return { isDateArray: false };
        }
      }
      return null;
    }
    return { isDateArray: false };
  }

  fixDateShift(): any {
    let fromDate = this.invoiceRequestForm.value.date![0];
    const datepipe: DatePipe = new DatePipe('en-US');
    let from_date = datepipe.transform(fromDate, 'yyyy-MM-dd');

    let toDate = this.invoiceRequestForm.value.date![1];
    let to_date = datepipe.transform(toDate, 'yyyy-MM-dd');
    return [from_date, to_date];
  }

  submit(): void {
    this.store.dispatch(openLoadingDialog());
    const [from, to] = this.fixDateShift();
    const requestBody: RequestInvoiceBody = {
      merchant_reference: this.invoiceRequestForm.value.merchant!,
      from_date: from,
      to_date: to,
    };
    this.invoicesService.requestInvoice(requestBody).subscribe((res) => {
      this.store.dispatch(closeLoadingDialog());
      if (res.ok) {
        this.router.navigate(['/dashboard/invoices/list']);
      }
    });
  }
  onCheckDate() {
    let startDate = this.invoiceRequestForm.value.date![0];
    let endDate = this.invoiceRequestForm.value.date![1];
    const oneDay: number = 24 * 60 * 60 * 1000;
    const start: Date = new Date(
      startDate.getFullYear(),
      startDate.getMonth(),
      startDate.getDate()
    );
    if (endDate) {
      const end: Date = new Date(
        endDate?.getFullYear(),
        endDate.getMonth(),
        endDate.getDate()
      );
      const diff: number = Math.round(
        Math.abs((start.getTime() - end.getTime()) / oneDay)
      );
      if (diff > 30) {
        // this.incomeReportForm.value.date![1].setMonth(startDate.getMonth() + 1)
        // this.incomeReportForm.value.date![1].setDate(startDate.getDate())
        // this.incomeReportForm.reset();

        this.invoiceRequestForm.patchValue({
          date: [], // Set the end date to null to reset it
        });

        this.messageService.add({
          severity: 'warn',
          summary: $localize`Set Reporting Period Failed`,
          detail: $localize`The maximum reporting period is one month`,
          life: 3000,
        });
      }
    }
  }
}
