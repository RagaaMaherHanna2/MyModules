import { DatePipe } from '@angular/common';
import { Component, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { Table } from 'primeng/table';
import { ProductService } from 'src/app/services/Product';
import { ExcelService } from 'src/app/services/excel.service';
import { SerialsBatchesService } from 'src/app/services/serials-batches/serials-batches.service';
import { environment } from 'src/environments/environment';
import { Product, ProductBatch, stockHistory } from 'src/models/Product/models';
import { Country } from 'src/models/country/model';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-product-details',
  templateUrl: './product-details.component.html',
  styleUrls: ['./product-details.component.scss'],
})
export class ProductDetailsComponent {
  loading: boolean = false;
  product: Product;
  productBatches: GetListResponse<ProductBatch> = {
    data: [],
    totalCount: 0,
  };
  locale = $localize.locale;
  baseURL: string = environment.API_URL;
  chartData: object;
  chartOptions: object;
  showStockHistoryChart: boolean = false;
  stockHistory: stockHistory[];
  dialogVisible: boolean = false;
  userCurrency: string =
    localStorage.getItem(environment.CURRENCY_SYMBOL) || 'null';

  codesAdditionalValues: any = localStorage.getItem(
    environment.CODES_ADDITIONAL_VALUE
  );
  batchesPageSize: number = 4;
  countries: GetListResponse<Country>;
  countriesOptions: Country[] =
    localStorage.getItem(environment.COUNTRIES) != undefined
      ? JSON.parse(localStorage.getItem(environment.COUNTRIES) || '')
      : this.getCountries();
  stopLoading: boolean = false;
  @ViewChild('batchesTable') batchesTable: Table;

  constructor(
    private activatedRout: ActivatedRoute,
    private productService: ProductService,
    private messageService: MessageService,
    private router: Router,
    private store: Store,
    private excelService: ExcelService,
    private serialsBatchesService: SerialsBatchesService
  ) {}

  ngOnInit(): void {
    this.activatedRout.params.subscribe((params) => {
      this.loadInfo(+params['id']);
    });
  }

  callProductBatchesAPI(offset: number) {
    this.loading = true;
    this.productService
      .getProductBatches({
        limit: this.batchesPageSize,
        offset: offset,
        product_id: this.product.id,
      })
      .subscribe((res) => {
        this.loading = false;
        if (res.ok) {
          this.productBatches = res.result;
        }
      });
  }
  loadInfo(product_id: number, event: LazyLoadEvent = {}): void {
    this.productService.getProductDetails(product_id).subscribe((res) => {
      if (res.ok) {
        if (res.result.data && res.result.data.length > 0) {
          this.product = res.result.data[0];
          if (
            !this.product.is_prepaid &&
            !this.product.serials_auto_generated
          ) {
            this.callProductBatchesAPI(event.first as number);
          }
        } else {
          this.stopLoading = true;
          this.messageService.add({
            severity: 'warn',
            summary: $localize`Product Not Found`,
            detail: $localize`This product may have been deleted or is unavailable.`,
            life: 3000,
          });
        }
      }
    });
  }

  edit(): void {
    this.router.navigate(['/dashboard/product/edit-product/', this.product.id]);
  }

  uploadSerials(): void {
    this.dialogVisible = true;
  }

  downloadSerialsTemplate(): void {
    this.excelService.exportSerialTemplate(this.product);
  }
  getProdutType(product: Product) {
    if (product.is_prepaid) return $localize`Prepaid Card`;
    else return $localize`Voucher`;
  }
  freezeBatch(item: ProductBatch): void {
    this.store.dispatch(openLoadingDialog());
    this.productService.freezeBatch({ id: item.id }).subscribe((res) => {
      if (res.ok) {
        this.messageService.add({
          severity: 'success',
          summary: $localize`Success`,
          detail: $localize`The batch has been holded successfully`,
        });

        this.loadInfo(this.product.id);
        this.batchesTable.reset();
        this.store.dispatch(closeLoadingDialog());
      }
    });
  }
  enableBatch(item: ProductBatch): void {
    this.store.dispatch(openLoadingDialog());
    this.productService.unfreezeBatch({ id: item.id }).subscribe((res) => {
      if (res.ok) {
        this.messageService.add({
          severity: 'success',
          summary: $localize`Success`,
          detail: $localize`The batch has been unholded successfully`,
        });
        this.loadInfo(this.product.id);
        this.batchesTable.reset();
        this.store.dispatch(closeLoadingDialog());
      }
    });
  }

  sendViaEmail(productBatch: ProductBatch): void {
    this.store.dispatch(openLoadingDialog());
    this.serialsBatchesService
      .sendBatchSerialViaEmail(productBatch.id)
      .subscribe((res) => {
        if (res.ok) {
          this.messageService.add({
            severity: 'success',
            summary: $localize`Email Sent Successfully`,
            detail: res.message,
            life: 3000,
          });
          this.store.dispatch(closeLoadingDialog());
        } else {
          this.store.dispatch(closeLoadingDialog());
          this.messageService.add({
            severity: 'error',
            summary: $localize`Sending Email Failed`,
            detail: res.message,
            life: 3000,
          });
        }
      });
  }

  generatePerfix(type: string) {
    return type === 'percent' ? '%' : '$';
  }

  openStockHistoryChart() {
    this.showStockHistoryChart = true;
    this.productService
      .getProductStockHistory({
        product_id: this.product.id,
      })
      .subscribe((res) => {
        this.stockHistory = res.result.data.reverse();
        const datepipe: DatePipe = new DatePipe('en-US');
        this.chartData = {
          labels: this.stockHistory.map(function (stockElement) {
            return datepipe.transform(
              new Date(stockElement.history_date),
              'MM/dd/yyyy, hh:mm a'
            );
          }),
          datasets: [
            {
              label: $localize`Total`,
              data: this.stockHistory.map(function (a) {
                return a.total;
              }),
              fill: false,
              tension: 0.4,
              borderColor: 'rgb(0, 119, 182)',
              backgroundColor: 'rgb(173, 232, 244)',
            },
            {
              label: $localize`Available`,
              data: this.stockHistory.map(function (a) {
                return a.available;
              }),
              fill: false,
              tension: 0.4,
              borderColor: 'rgb(82, 183, 136)',
              backgroundColor: 'rgb(216, 243, 220)',
            },
            {
              label: $localize`Frozen`,
              data: this.stockHistory.map(function (a) {
                return a.frozen;
              }),
              fill: false,
              tension: 0.4,
              borderColor: 'rgb(186, 24, 27)',
              backgroundColor: 'rgb(252, 213, 206)',
            },
            {
              label: $localize`Sold`,
              data: this.stockHistory.map(function (a) {
                return a.pulled;
              }),
              fill: false,
              tension: 0.4,
              borderColor: 'rgb(255, 195, 0)',
              backgroundColor: 'rgb(251, 248, 204)',
            },
          ],
        };

        this.chartOptions = {
          maintainAspectRatio: false,
          aspectRatio: 0.6,
        };
      });
  }
  getProductExpiryPeriodValue(expiry_period: any) {
    if (expiry_period > 0) {
      return expiry_period;
    } else if (expiry_period === 0) {
      return 'unlimited';
    }
  }
  getFoodicsDiscountType(discountTypeId: string) {
    if (discountTypeId === '1') return $localize`Order Level`;
    else return $localize`Product Level`;
  }

  getCountries() {
    let unspecified_option: Country[] = [
      {
        country_id: 0,
        country_name: 'Not Specified',
        country_currency_id: '',
        country_currency_name: '',
        country_currency_unit: '',
      },
    ];
    this.productService.getCountries().subscribe((res) => {
      if (res.ok) {
        this.countries = res.result;

        this.countriesOptions = unspecified_option.concat(res.result.data);
        localStorage.setItem(
          environment.COUNTRIES,
          JSON.stringify(this.countriesOptions)
        );
      }
      return this.countriesOptions;
    });
  }
}
