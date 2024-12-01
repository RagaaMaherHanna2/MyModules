import { Component, OnInit } from '@angular/core';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';
import {
  AbstractControl,
  FormBuilder,
  FormControl,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import {
  CreateFeesReportBody,
  FeesRequestFormType,
} from 'src/models/Reports/models';
import { Store } from '@ngrx/store';
import { ReportsService } from 'src/app/services/reports';
import { DatePipe } from '@angular/common';
import { MerchantsService } from 'src/app/services/merchants/merchants.service';
import { BehaviorSubject } from 'rxjs';
@Component({
  selector: 'app-create-fees-report',
  templateUrl: './create-fees-report.component.html',
  styleUrls: ['./create-fees-report.component.scss'],
})
export class CreateFeesReportComponent {
  constructor(
    private router: Router,
    private formBuilder: FormBuilder,
    private store: Store,
    private reportsService: ReportsService,
    private merchantsService: MerchantsService
  ) {}

  offset: number = 0;
  loadingMerchants = new BehaviorSubject(false);
  feesReportForm = this.formBuilder.group<FeesRequestFormType>({
    sp: new FormControl<number | null>(null, [Validators.required]),
    merchant: new FormControl<number | null>(null, [Validators.required]),
    date: new FormControl<Date | null>(null, [Validators.required]),
  });

  maxDate: Date;
  merchants: { name: string; id: number }[] = [];
  SPs: { name: string; id: number }[] = [];

  ngOnInit() {
    const today = new Date();
    const lastDayOfMonth = new Date(
      today.getFullYear(),
      today.getMonth() + 1,
      0
    );
    this.maxDate = lastDayOfMonth;
    this.merchantsService.getAccountantManagerSPs().subscribe((res) => {
      this.store.dispatch(closeLoadingDialog());
      if (res.ok) {
        let serviceProviders = res.result.data;
        serviceProviders.forEach((sp) => {
          this.SPs.push(sp);
        });
      }
    });
  }
  getMerchants(sp: number) {
    this.merchants = [];
    this.loadingMerchants.next(true);
    this.merchantsService
      .getInvitesList(this.offset, 1000, sp)
      .subscribe((res) => {
        if (res.ok) {
          this.loadingMerchants.next(false);
          res.result.data.forEach((merchant) => {
            this.merchants.push({
              name: merchant.name!,
              id: merchant.id!,
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

  submit(): void {
    this.store.dispatch(openLoadingDialog());
    const [from, to] = this.fixDateShift();

    const requestBody: CreateFeesReportBody = {
      from_date: from,
      to_date: to,
      sp: this.feesReportForm.value.sp!,
      merchant: this.feesReportForm.value.merchant!,
    };
    this.reportsService.createFeesReport(requestBody).subscribe((res: any) => {
      this.store.dispatch(closeLoadingDialog());
      if (res.ok) {
        this.router.navigate(['/dashboard/reports/fees-reports']);
      }
    });
  }

  fixDateShift(): any {
    let fromDate = this.feesReportForm.value.date!;
    const datepipe: DatePipe = new DatePipe('en-US');
    let from_date = datepipe.transform(fromDate, 'yyyy-MM-dd');
    // Calculate the toDate
    let toDate = new Date(); // Start with today's date

    if (
      toDate.getFullYear() === fromDate.getFullYear() &&
      toDate.getMonth() === fromDate.getMonth()
    ) {
      // If fromDate is in the current month, set toDate to today
      toDate = new Date();
    } else {
      // Otherwise, calculate the last day of fromDate's month
      toDate = new Date(fromDate.getFullYear(), fromDate.getMonth() + 1, 0);
    }

    let to_date = datepipe.transform(toDate, 'yyyy-MM-dd');
    return [from_date, to_date];
  }
}
