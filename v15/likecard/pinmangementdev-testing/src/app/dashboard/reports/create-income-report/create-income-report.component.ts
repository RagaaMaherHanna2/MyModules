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
  CreateIncomeReportBody,
  IncomeRequestFormType,
} from 'src/models/Reports/models';
import { MessageService } from 'primeng/api';
import { createSelector, Store } from '@ngrx/store';
import { ReportsService } from 'src/app/services/reports';
import { DatePipe } from '@angular/common';
import { accessRightFeature } from 'src/store/accessRightSlice';
import { MerchantsService } from 'src/app/services/merchants/merchants.service';
import { BehaviorSubject } from 'rxjs';
@Component({
  selector: 'app-create-income-report',
  templateUrl: './create-income-report.component.html',
  styleUrls: ['./create-income-report.component.scss'],
})
export class CreateIncomeReportComponent implements OnInit {
  constructor(
    private router: Router,
    private formBuilder: FormBuilder,
    private messageService: MessageService,
    private store: Store,
    private reportsService: ReportsService,
    private merchantsService: MerchantsService
  ) {}
  role$ = this.store.select(
    createSelector(accessRightFeature, (state) => state.role)
  );
  isAcountManager: boolean = false;
  offset: number = 0;
  loadingMerchants = new BehaviorSubject(false);
  incomeReportForm = this.formBuilder.group<IncomeRequestFormType>({
    date: new FormControl<Date[]>(
      [],
      [Validators.required, this.isDateArrayValidator]
    ),
  });
  minDate: Date = new Date();
  maxDate: Date = new Date();
  merchants: { name: string; id: number }[] = [];
  SPs: { name: string; id: number }[] = [];

  ngOnInit() {
    this.minDate.setDate(this.minDate.getDate() - 90);
    this.maxDate.setDate(this.maxDate.getDate());
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

  onCheckDate() {
    let startDate = this.incomeReportForm.value.date![0];
    let endDate = this.incomeReportForm.value.date![1];
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

        this.incomeReportForm.patchValue({
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

  submit(): void {
    this.store.dispatch(openLoadingDialog());
    const [from, to] = this.fixDateShift();

    const requestBody: CreateIncomeReportBody = {
      from_date: from,
      to_date: to,
    };
    this.reportsService
      .createIncomeReport(requestBody)
      .subscribe((res: any) => {
        this.store.dispatch(closeLoadingDialog());
        if (res.ok) {
          this.router.navigate(['/dashboard/reports/income-reports']);
        }
      });
  }

  fixDateShift(): any {
    let fromDate = this.incomeReportForm.value.date![0];
    const datepipe: DatePipe = new DatePipe('en-US');
    let from_date = datepipe.transform(fromDate, 'yyyy-MM-dd');

    let toDate = this.incomeReportForm.value.date![1];
    let to_date = datepipe.transform(toDate, 'yyyy-MM-dd');
    return [from_date, to_date];
  }
}
