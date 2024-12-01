import { CreateSalesReport } from '../../../../models/Reports/models';
import { ReportsService } from '../../../services/reports/reports.service';
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
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';
import { MerchantsService } from 'src/app/services/merchants/merchants.service';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { MerchantsInviteList } from 'src/models/invites/invites.model';
import { accessRightFeature } from 'src/store/accessRightSlice';
import { createSelector } from '@ngrx/store';
import { MessageService } from 'primeng/api';
import { UserService } from 'src/app/services/User/user.service';
import { ProductService } from 'src/app/services/Product';
import { DatePipe } from '@angular/common';

type RequestFormType = {
  date: FormControl<Date[] | null>;
  productId: string;
  selectedMerchant: any;
};

@Component({
  selector: 'app-create-report',
  templateUrl: './create-sales-report.component.html',
  styleUrls: ['./create-sales-report.component.scss'],
})
export class CreateSalesReportComponent implements OnInit {
  salesReportForm = this.formBuilder.group<RequestFormType>({
    date: new FormControl<Date[]>(
      [],
      [Validators.required, this.isDateArrayValidator]
    ), // Set initial value and validators
    productId: '',
    selectedMerchant: '',
  });
  minDate: Date = new Date();
  maxDate: Date = new Date();

  merchants: GetListResponse<MerchantsInviteList>;
  options: { name: string; reference: string; id: any }[] = [
    { name: $localize`All`, reference: '', id: null },
  ];
  theUserRole: string = '';
  accessRole$ = this.store.select(
    createSelector(accessRightFeature, (state) => state.role)
  );

  selectedDates: Date[];
  maxRangeDate: Date;
  fetchingMerchant: boolean = false;
  fetchingProduct: boolean = false;
  merchantInfo: {
    found: boolean;
    name: string;
  } = {
    found: false,
    name: $localize`Please enter a reference`,
  };
  productInfo: {
    found: boolean;
    name: string;
  } = {
    found: false,
    name: $localize`Please enter a product ID`,
  };

  constructor(
    private router: Router,
    private formBuilder: FormBuilder,
    private store: Store,
    private reportsService: ReportsService,
    private merchantsService: MerchantsService,
    private messageService: MessageService,
    private userService: UserService,
    private productService: ProductService
  ) {
    this.selectedDates = [];
    this.maxRangeDate = new Date();
  }

  ngOnInit() {
    this.minDate.setDate(this.minDate.getDate() - 90);
    this.maxDate.setDate(this.maxDate.getDate());

    this.accessRole$.subscribe((roles) => {
      this.theUserRole = roles[0];
      if (this.theUserRole === 'service_provider') {
        this.merchantsService.getInvitesList().subscribe((res) => {
          if (res.ok) {
            this.merchants = res.result;
            this.merchants.data.forEach((merchant) => {
              this.options.push({
                name: merchant.name!,
                reference: merchant.reference!,
                id: merchant.id!,
              });
            });
          }
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
    let fromDate = this.salesReportForm.value.date![0];
    const datepipe: DatePipe = new DatePipe('en-US');
    let from_date = datepipe.transform(fromDate, 'yyyy-MM-dd');

    let toDate = this.salesReportForm.value.date![1];
    let to_date = datepipe.transform(toDate, 'yyyy-MM-dd');
    return [from_date, to_date];
  }

  onCheckDate() {
    let startDate = this.salesReportForm.value.date![0];
    let endDate = this.salesReportForm.value.date![1];
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
        // this.salesReportForm.value.date![1].setMonth(startDate.getMonth() + 1)
        // this.salesReportForm.value.date![1].setDate(startDate.getDate())
        // this.salesReportForm.reset();

        this.salesReportForm.patchValue({
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
    const requestBody: CreateSalesReport = {
      from_date: from,
      to_date: to,
      product: this.salesReportForm.value.productId
        ? parseInt(this.salesReportForm.value.productId)
        : undefined,
      merchant_filter: this.salesReportForm.value.selectedMerchant
        ? this.salesReportForm.value.selectedMerchant
        : undefined,
    };
    this.reportsService.createSalesReport(requestBody).subscribe((res: any) => {
      this.store.dispatch(closeLoadingDialog());
      if (res.ok) {
        this.router.navigate(['/dashboard/reports/list-sales-reports']);
      }
    });
  }

  getMerchantInfo(event: any): void {
    console.log(event);
    if (event.target.value) {
      this.fetchingMerchant = true;
      this.salesReportForm.controls.selectedMerchant.disable();
      this.userService
        .getUserByReference({ reference: event.target.value })
        .subscribe((res) => {
          setTimeout(() => {}, 1000);
          if (!res.ok) {
            this.merchantInfo.found = false;
            this.merchantInfo.name = $localize`Please enter a correct reference`;
            setTimeout(() => {
              this.salesReportForm.controls.selectedMerchant.setErrors({
                notFound: true,
              });
            }, 0);
          } else {
            this.merchantInfo.found = true;
            this.merchantInfo.name = res.result.name;
          }

          this.fetchingMerchant = false;
          this.salesReportForm.controls.selectedMerchant.enable();
        });
    } else {
      this.merchantInfo.name = $localize`Please enter a reference`;
    }
  }
  getProductInfo(event: any): void {
    if (event.target.value) {
      this.fetchingProduct = true;
      this.salesReportForm.controls.productId.disable();
      this.productService
        .getProductNameById(parseInt(event.target.value))
        .subscribe((res) => {
          setTimeout(() => {}, 1000);
          if (!res.ok) {
            this.productInfo.found = false;
            this.productInfo.name = $localize`Please enter a correct ID`;
            setTimeout(() => {
              this.salesReportForm.controls.productId.setErrors({
                notFound: true,
              });
            }, 0);
          } else {
            this.productInfo.found = true;
            this.productInfo.name = res.result;
          }

          this.fetchingProduct = false;
          this.salesReportForm.controls.productId.enable();
        });
    } else {
      this.productInfo.name = $localize`Please enter a product id`;
    }
  }
}
