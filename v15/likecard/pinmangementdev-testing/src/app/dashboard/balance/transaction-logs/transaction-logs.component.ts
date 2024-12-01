import { ExcelService } from './../../../services/excel.service';
import { GetListResponse } from './../../../../models/responses/get-response.model';
import { environment } from './../../../../environments/environment';
import { Component } from '@angular/core';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { BalanceService } from 'src/app/services/Balance/balance.servicec';
import { TransactionLog } from 'src/models/balance/models';
import { Store, createSelector } from '@ngrx/store';
import { accessRightFeature } from 'src/store/accessRightSlice';

@Component({
  selector: 'app-transaction-logs',
  templateUrl: './transaction-logs.component.html',
  styleUrls: ['./transaction-logs.component.scss'],
  providers: [MessageService],
})
export class TransactionLogsComponent {
  pageSize: number = environment.PAGE_SIZE;
  items: GetListResponse<TransactionLog>;
  loading: boolean = false;
  lastFilter: LazyLoadEvent = { filter: {}, first: 0 } as LazyLoadEvent;
  filter: string = '';
  dialogVisible = false;
  selectedTransaction: TransactionLog = {} as TransactionLog;
  readonly minDate = new Date(new Date().setDate(new Date().getDate() + 1));
  readonly EXCEL_FILE_TYPES = environment.EXCEL_FILE_TYPES;
  role$ = this.store.select(
    createSelector(accessRightFeature, (state) => state.role)
  );
  userCurrency: string = (localStorage.getItem(environment.CURRENCY_SYMBOL)|| 'null')

  constructor(
    private service: BalanceService,
    private excelService: ExcelService,
    private messageService: MessageService,
    private store: Store
  ) {}
  ngOnInit(): void {
    this.loadList(this.lastFilter);
  }

  loadList(event: LazyLoadEvent) {
    // this.loading = true;
    this.lastFilter = event;
    this.role$.subscribe((roles) => {
      if (roles.includes('service_provider')) {
        this.items = {
          data: [
            {
              id: '9aead4f0-844b-43be-9ac4-ce48c7129b7d',
              amount: 600,
              create_date: '15/12/2022',
              description: $localize`Package Sales`,
            },
            {
              id: 'de66c683-49b5-491b-abb0-fc2ea5798d11',
              amount: -400,
              create_date: '27/11/2022',
              description: $localize`Creating Package`,
            },
            {
              id: '1b821685-5065-4a12-879b-9dcd2e7ac2cf',
              amount: 1000,
              create_date: '20/11/2022',
              description: $localize`Recharge Wallet`,
            },
          ],
          totalCount: 3,
        };
      } else {
        this.items = {
          data: [
            {
              id: '9aead4f0-844b-43be-9ac4-ce48c7129b7d',
              amount: -600,
              create_date: '15/12/2022',
              description: $localize`Pulling Codes`,
            },
            {
              id: '1b821685-5065-4a12-879b-9dcd2e7ac2cf',
              amount: 2600,
              create_date: '28/11/2022',
              description: $localize`Recharge Wallet`,
            },
          ],
          totalCount: 3,
        };
      }
    });
    // this.service
    //   .list({
    //     limit: this.pageSize,
    //     offset: event.first as number,
    //     description: this.filter,
    //     sorting: event.sortField
    //       ? `${event.sortField} ${event.sortOrder === 1 ? 'asc' : 'desc'}`
    //       : '',
    //   })
    //   .subscribe((res) => {
    //     if (res.ok) {
    //       this.items.data = res.result.data;
    //       this.items.totalCount = res.result.totalCount;
    //       this.loading = false;
    //     } else {
    //       this.messageService.add({
    //         severity: 'error',
    //         summary: $localize`Loading Failed`,
    //         detail: res.message,
    //         life: 3000,
    //       });
    //     }
    //   });
  }
  applyFilter(event: any) {
    this.filter = event.target.value;
    let ev: LazyLoadEvent = {};
    ev.first = 0;
    ev.sortField = '';
    this.loadList(ev);
  }
}
