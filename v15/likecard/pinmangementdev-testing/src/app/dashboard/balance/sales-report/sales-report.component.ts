import { Product } from 'src/models/Product/models';
import { Package } from 'src/models/package/models';
import { Merchant } from './../../../../models/Merchant/models';
import { WalletService } from './../../../services/wallet/wallet.service';
import { BaseResponse } from './../../../../models/responses/base-response.model';
import { FilterSelectionData } from './../../../../models/balance/models';
import { ActivatedRoute } from '@angular/router';
import { ExcelService } from './../../../services/excel.service';
import { BalanceService } from 'src/app/services/Balance/balance.servicec';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { GetListResponse } from './../../../../models/responses/get-response.model';
import { environment } from './../../../../environments/environment';
import { Component } from '@angular/core';
import { SalesReport } from 'src/models/balance/models';
import data from 'src/assets/Sales_Report_MOCK.json';

@Component({
  selector: 'app-sales-report',
  templateUrl: './sales-report.component.html',
  styleUrls: ['./sales-report.component.scss'],
  providers: [MessageService],
})
export class SalesReportComponent {
  pageSize: number = 10;
  items: GetListResponse<SalesReport> = { data: [], totalCount: 0 };
  loading: boolean = false;
  lastFilter: LazyLoadEvent = { filter: {}, first: 0 } as LazyLoadEvent;
  filter: string = '';
  dialogVisible = false;
  selectedItems: SalesReport[] = [];
  merchants: Merchant[] = [];
  packages: Package[] = [];
  products: Product[] = [];
  userCurrency: string = (localStorage.getItem(environment.CURRENCY_SYMBOL)|| 'null')


  readonly minDate = new Date(new Date().setDate(new Date().getDate() + 1));
  readonly EXCEL_FILE_TYPES = environment.EXCEL_FILE_TYPES;

  // DummyData

  // END DummyData
  filterSelectionData: FilterSelectionData = {
    products: [],
    packages: [],
    merchants: [],
  };
  totalRecords: number;
  constructor(
    private service: BalanceService,
    private walletService: WalletService,
    private excelService: ExcelService,
    private messageService: MessageService,
    private activatedRoute: ActivatedRoute
  ) {}
  ngOnInit(): void {
    /* this.service
      .getFilterData()
      .subscribe((res: BaseResponse<FilterSelectionData>) => {
        this.merchants = res.result.merchants;
        this.packages = res.result.packages;
        this.products = res.result.products;
      });
 */    this.loadList(this.lastFilter);
  }
  loadList(event: LazyLoadEvent) {
    this.loading = true;
    this.lastFilter = event;
    this.service
      .list({
        limit: this.pageSize,
        offset: event.first as number,
        merchants: this.filterSelectionData.merchants,
        packages: this.filterSelectionData.packages,
        products: this.filterSelectionData.products,
      })
      .subscribe((res) => {
        if (res.ok) {
          this.items.data = res.result.data;
          this.items.totalCount = res.result.totalCount;
          this.loading = false;
        } else {
          this.messageService.add({
            severity: 'error',
            summary: $localize`Loading Balance Failed`,
            detail: res.message,
            life: 3000,
          });
        }
      });
  }
  columnFilter(event: any, column: string) {
    if (column == 'product') {
      this.filterSelectionData.products = event.value.map((res: Product) => {
        return res.id;
      });
    }
    if (column == 'package') {
      this.filterSelectionData.packages = event.value.map((res: Package) => {
        return res.id;
      });
    }
    if (column == 'merchant') {
      this.filterSelectionData.merchants = event.value.map((res: Merchant) => {
        return res.id;
      });
    }
    this.loadList(this.lastFilter);
  }
}
