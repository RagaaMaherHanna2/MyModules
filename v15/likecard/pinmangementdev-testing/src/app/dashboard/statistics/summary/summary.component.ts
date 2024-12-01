import { CurrencyPipe, DatePipe, DecimalPipe } from '@angular/common';
import { Component } from '@angular/core';
import { createSelector, resultMemoize, Store } from '@ngrx/store';
import { AuthService } from 'src/app/services/auth.service';
import { StatisticsService } from 'src/app/services/statistics/statistics.service';
import { getFormattedDate, getISODate } from 'src/app/shared/utils/date';
import { environment } from 'src/environments/environment';
import { ChartItem, statisticsFilter } from 'src/models/statistics/statistics';
import {
  accessRightFeature,
  setAccessRights,
  setUser,
} from 'src/store/accessRightSlice';
import { balanceFeature } from 'src/store/balanceSlice';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

type StatCard = {
  title: string;
  value: string | null;
  isMidCard: boolean;
  icon: string;
};
@Component({
  selector: 'app-summary',
  templateUrl: './summary.component.html',
  styleUrls: ['./summary.component.scss'],
})
export class SummaryComponent {
  summaryData: StatCard[];
  // merchantData: { [key: string]: { title: string; value: string } };

  access$ = this.store.select(
    createSelector(accessRightFeature, (state) => state)
  );
  balance$ = this.store.select(
    createSelector(balanceFeature, (state) => state.balance)
  );

  summaryPeriods = [
    { name: 'last_day', label: $localize`Last Day` },
    { name: 'last7days', label: $localize`Last 7 Days` },
    { name: 'last_month', label: $localize`Last Month` },
  ];

  selectedPeriod: string = 'last_day';
  isServiceProvider: boolean = false;
  statisticsFilter: statisticsFilter = {} as statisticsFilter;
  averageOrderChartData: any;
  averageOrderChartOptions: any;
  constructor(
    private store: Store,
    private statisticsService: StatisticsService,
    private authService: AuthService,
    private datePipe: DatePipe,
    private decimalPipe: DecimalPipe,
    private currencyPipe: CurrencyPipe
  ) {}
  ngOnInit(): void {
    this.statisticsFilter.from_date = this.getYesterdayDate();
    this.store.dispatch(openLoadingDialog());
    this.authService.whoAmI().subscribe((res) => {
      if (res.ok) {
        localStorage.setItem(
          environment.CODES_ADDITIONAL_VALUE,
          res.result.codes_additional_value
        );
        localStorage.setItem(
          environment.USER_ROLES_KEY,
          JSON.stringify(res.result.roles)
        );

        localStorage.setItem(environment.USER_KEY, JSON.stringify(res.result));
        localStorage.setItem(environment.BALANCE_KEY, '0');
        localStorage.setItem(
          environment.CURRENCY_SYMBOL,
          res.result.currency_symbol
        );

        this.store.dispatch(setAccessRights({ role: res.result.roles }));
        this.store.dispatch(setUser({ user: res.result }));

        this.access$.subscribe((access) => {
          if (
            access.role.includes('accountant Manager') ||
            access.role.includes('sp_finance')
          ) {
            this.store.dispatch(closeLoadingDialog());
          } else if (access.role.includes('service_provider')) {
            this.isServiceProvider = true;
            this.statisticsService
              .getServiceProviderSummary(this.statisticsFilter)
              .subscribe((res) => {
                this.store.dispatch(closeLoadingDialog());
                if (res.ok) {
                  this.fillServiceProviderSummaryData(access, res);
                  this.fillAverageOrderChart(res.result.chart);
                }
              });
          } else {
            this.statisticsService
              .getMerchantSummary(this.statisticsFilter)
              .subscribe((res) => {
                this.store.dispatch(closeLoadingDialog());
                if (res.ok) {
                  this.fillMerchantSummaryData(access, res);
                }
              });
          }
        });
      }
    });
  }

  fillServiceProviderSummaryData(access: any, res: any) {
    this.summaryData = [
      // {
      //   title: $localize`Welcome Back`,
      //   value: access.user.name,
      //   isMidCard: true,
      //   icon: '',
      // },

      {
        title: $localize`Total No. of Merchants`,
        value: this.decimalPipe.transform(
          res.result.total_merchant_count,
          '1.0'
        ),
        isMidCard: false,
        icon: 'pi-check-circle',
      },
      {
        title: $localize`Total Sales`,
        value: this.currencyPipe.transform(
          res.result.chart.reduce((accumulator: any, chartItem: ChartItem) => {
            return accumulator + chartItem.sales_value;
          }, 0),
          localStorage.getItem(environment.CURRENCY_SYMBOL) || 'null'
        ),
        isMidCard: false,
        icon: 'pi-money-bill',
      },
      {
        title: $localize`Total Sales Orders`,
        value: res.result.chart.reduce(
          (accumulator: any, chartItem: ChartItem) => {
            return accumulator + chartItem.sales_count;
          },
          0
        ),
        isMidCard: false,
        icon: 'pi-file',
      },
    ];
  }
  fillMerchantSummaryData(access: any, res: any) {
    this.summaryData = [
      // {
      //   title: $localize`Welcome Back`,
      //   value: access.user.name,
      //   isMidCard: true,
      //   icon: '',
      // },
      {
        title: $localize`Wallet Balance`,
        value:
          res.result.wallet_balance +
            localStorage.getItem(environment.CURRENCY_SYMBOL) || '',
        isMidCard: false,
        icon: 'pi-wallet',
      },
      {
        title: $localize`Invitations`,
        value: this.decimalPipe.transform(res.result.merchant_invites, '1.0'),
        isMidCard: false,
        icon: 'pi-envelope',
      },

      {
        title: $localize`Purchase Value`,
        value: this.currencyPipe.transform(
          res.result.sold_total,
          localStorage.getItem(environment.CURRENCY_SYMBOL) || 'null'
        ),
        isMidCard: false,
        icon: 'pi-money-bill',
      },
      {
        title: $localize`Last Pulled Code`,
        value:
          res.result.last_pull_date[0] !== null
            ? this.datePipe.transform(res.result.last_pull_date[0], 'longDate')
            : $localize`No codes Pulled Yet`,
        isMidCard: false,
        icon: 'pi-history',
      },
    ];
  }
  fillAverageOrderChart(chart: ChartItem[]) {
    const datepipe: DatePipe = new DatePipe('en-US');
    chart.sort((a, b) => Date.parse(b.date) - Date.parse(a.date)).reverse();
    chart = this.addMissingDatesToChart(chart);

    this.averageOrderChartData = {
      labels: chart.map(function (elem) {
        return datepipe.transform(new Date(elem.date), 'MM/dd/yyyy');
      }),
      datasets: [
        {
          label: $localize`Average Order Value`,
          data: chart.map(function (elem) {
            return elem.sales_count === 0
              ? 0
              : elem.sales_value / elem.sales_count;
          }),
          fill: false,
          tension: 0.4,
          borderColor: 'rgb(56, 82, 173)',
          backgroundColor: 'rgb(197, 206, 236)', // Set background color to transparent
        },
      ],
    };

    this.averageOrderChartOptions = {
      responsive: true,
    };
  }
  onPeriodChange(event: any): void {
    if (event.value === 'last_day')
      this.statisticsFilter.from_date = this.getYesterdayDate();
    else if (event.value === 'last7days')
      this.statisticsFilter.from_date = this.getLastWeek();
    else this.statisticsFilter.from_date = this.getLastMonth();
    this.store.dispatch(openLoadingDialog());
    this.access$.subscribe((access) => {
      if (this.isServiceProvider) {
        this.statisticsService
          .getServiceProviderSummary(this.statisticsFilter)
          .subscribe((res) => {
            this.store.dispatch(closeLoadingDialog());
            if (res.ok) {
              this.fillServiceProviderSummaryData(access, res);
              this.fillAverageOrderChart(res.result.chart);
            }
          });
      } else {
        this.statisticsService
          .getMerchantSummary(this.statisticsFilter)
          .subscribe((res) => {
            this.store.dispatch(closeLoadingDialog());
            if (res.ok) {
              this.fillMerchantSummaryData(access, res);
            }
          });
      }
    });
  }
  getYesterdayDate(): string {
    var now = new Date();
    return new Date(now.setDate(now.getDate() - 1)).toLocaleDateString('sv-SE');
  }
  getLastWeek(): string {
    const now = new Date();
    return new Date(now.setDate(now.getDate() - 7)).toLocaleDateString('sv-SE');
  }
  getLastMonth() {
    const now = new Date();
    const year =
      now.getMonth() === 0 ? now.getFullYear() - 1 : now.getFullYear();
    const month = now.getMonth() === 0 ? 11 : now.getMonth() - 1;
    const lastMonthDate = new Date(year, month, now.getDate());
    return new Date(lastMonthDate).toLocaleDateString('sv-SE');
  }
  addMissingDatesToChart(chartData: ChartItem[]) {
    const datepipe: DatePipe = new DatePipe('en-US');
    let from_date = datepipe.transform(
      this.statisticsFilter.from_date,
      'yyyy-MM-dd'
    );
    let to_date = datepipe.transform(new Date(), 'yyyy-MM-dd');

    if (!chartData.find((e) => e.date === from_date)) {
      chartData = [
        { sales_count: 0, sales_value: 0, date: from_date! },
        ...chartData,
      ];
    }
    if (!chartData.find((e) => e.date === to_date)) {
      chartData = [
        ...chartData,
        { sales_count: 0, sales_value: 0, date: to_date! },
      ];
    }

    let chartDataWithMissings = chartData.slice();
    for (let i = 0; i < chartDataWithMissings.length; i++) {
      if (i + 1 < chartDataWithMissings.length) {
        var date1 = new Date(chartDataWithMissings[i].date);
        var date2 = new Date(chartDataWithMissings[i + 1].date);
        // Set date1 to the beginning of the day by setting the hours, minutes, seconds, and milliseconds to zero
        date1.setHours(0, 0, 0, 0);

        // Set date2 to the beginning of the day by setting the hours, minutes, seconds, and milliseconds to zero
        date2.setHours(0, 0, 0, 0);

        // Add one day (24 hours) to date1
        date1.setDate(date1.getDate() + 1);

        if (date1.getTime() !== date2.getTime()) {
          //add the label
          chartDataWithMissings.splice(i + 1, 0, {
            sales_value: 0,
            sales_count: 0,
            date: datepipe.transform(date1.getTime(), 'yyyy-MM-dd')!,
          });
        }
      }
    }
    return chartDataWithMissings;
  }
}
