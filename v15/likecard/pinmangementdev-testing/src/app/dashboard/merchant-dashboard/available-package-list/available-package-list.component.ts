import { MerchantProduct } from './../../../../models/Merchant/models';
import { Package } from 'src/models/package/models';
import { Router } from '@angular/router';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { environment } from './../../../../environments/environment';
import { GetListResponse } from './../../../../models/responses/get-response.model';
import { Component } from '@angular/core';
import { MerchantService } from 'src/app/services/Merchant/merchant.service';

@Component({
  selector: 'app-available-package-list',
  templateUrl: './available-package-list.component.html',
  styleUrls: ['./available-package-list.component.scss'],
  providers: [MessageService],
})
export class AvailablePackageListComponent {
  items: GetListResponse<MerchantProduct> = {
    data: [],
    totalCount: 0,
  };
  loading: boolean = false;
  pageSize: number = environment.PAGE_SIZE;
  lastFilter: LazyLoadEvent = { filter: {}, first: 0 } as LazyLoadEvent;
  filter: string = '';
  locale = $localize.locale;
  offset: number = 0;
  userCurrency: string = (localStorage.getItem(environment.CURRENCY_SYMBOL)|| 'null')

  constructor(
    private service: MerchantService,
    private messageService: MessageService,
    private router: Router
  ) {}
  ngOnInit(): void {
    this.loadList();
  }
  loadList() {
    this.loading = true;
    this.service
      .list({
        offset: this.offset,
        limit: this.pageSize,
        name: this.filter === '' ? undefined : this.filter,
      })
      .subscribe((res) => {
        if (res.ok) {
          this.items.data = res.result.data;
          this.items.totalCount = res.result.totalCount;
          this.loading = false;
        } else {
          this.messageService.add({
            severity: 'error',
            summary: $localize`Loading Packages Failed`,
            detail: res.message,
            life: 3000,
          });
        }
      });
  }
  applyFilter(event: any) {
    this.filter = event.target.value;
    let ev: LazyLoadEvent = {};
    this.offset = 0;
    ev.first = 0;
    ev.sortField = '';
    this.loadList();
  }
  changePage(event: { first: number; row: number }) {
    this.offset = event.first;
    this.loadList();
  }
  goToDetails(item: Package) {
    this.router.navigate(['dashboard/merchant/product/details', item.id]);
  }
  getProdutType(item:any){
    if (item.is_prepaid)
      return $localize`Prepaid Card`
      else
      return $localize`Voucher`
  }


  generatePerfix(type: string) {
    return type === 'percent' ? '%' : '$'
  }
}
