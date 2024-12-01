import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { ExcelService } from 'src/app/services/excel.service';
import { OrdersService } from 'src/app/services/orders/orders.service';
import { environment } from 'src/environments/environment';
import { Order } from 'src/models/orders/orders';
import { GetListResponse } from 'src/models/responses/get-response.model';

@Component({
  selector: 'app-orders',
  templateUrl: './orders.component.html',
  styleUrls: ['./orders.component.scss'],
})
export class OrdersComponent {
  items: GetListResponse<Order> = {
    data: [],
    totalCount: 0,
  };
  loading: boolean = false;
  pageSize: number = environment.PAGE_SIZE;
  lastFilter: LazyLoadEvent = { filter: {}, first: 0 } as LazyLoadEvent;
  filter: string = '';
  dateFilter: string = '';
  selectedProduct: any;
  products: any[] = [{ product: $localize`All`, id: 0 }];

  constructor(
    private orderService: OrdersService,
    private router: Router,
    private messageService: MessageService,
    private excelService: ExcelService
  ) {}
  ngOnInit(): void {
    this.loadList(this.lastFilter);
  }

  loadList(event: LazyLoadEvent) {
    this.loading = true;
    this.lastFilter = event;
    this.orderService
      .getOrdersList({
        limit: this.pageSize,
        offset: event.first as number,
        name: this.filter,
        sorting: event.sortField
          ? `${event.sortField} ${event.sortOrder === 1 ? 'asc' : 'desc'}`
          : '',
        product_name:
          this.selectedProduct !== undefined ? this.selectedProduct : '',
        order_date:
          this.dateFilter !== '' && this.dateFilter !== null
            ? new Date(this.dateFilter).toLocaleDateString('en-CA')
            : '',
      })
      .subscribe((res) => {
        if (res.ok) {
          this.items.data = res.result.data;
          this.items.totalCount = res.result.totalCount;
          this.loading = false;
        } else {
          this.messageService.add({
            severity: 'error',
            summary: $localize`Loading Orders Failed`,
            detail: res.message,
            life: 3000,
          });
        }
      });
  }
  applyFilter(event: any) {
    this.filter = event.target.value;
    let ev: LazyLoadEvent = {};
    ev.first = 0;
    ev.sortField = '';
    this.loadList(ev);
  }
  goToDetails(item: Order) {
    this.router.navigate(['dashboard/orders/details', item.id]);
  }
  exportExcel() {
    this.orderService
      .getOrdersList({
        offset: 0,
        limit: this.items.totalCount,
        name: this.filter,
        sorting: '',
        product_name:
          this.selectedProduct !== undefined
            ? this.selectedProduct.product
            : '',
        order_date:
          this.dateFilter !== ''
            ? new Date(this.dateFilter).toLocaleDateString('en-CA')
            : '',
      })
      .subscribe((res: any) => {
        const data = res.result.data;
        data.map((r: any) => {
          delete r.image;
        });
        this.excelService.convertJSONtoExcel(
          data,
          [
            $localize`Order Name`,
            $localize`ID`,
            $localize`Order Date`,
            $localize`Product ID`,
            $localize`Product Name`,
            $localize`Price`,
          ],
          $localize`Purchase Orders`
        );
      });
  }
}
