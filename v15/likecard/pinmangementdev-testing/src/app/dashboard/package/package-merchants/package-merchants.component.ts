import { MerchantInvitation } from './../../../../models/package/models';
import { Router, ActivatedRoute } from '@angular/router';
import { PackageService } from './../../../services/Package/package.service';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { environment } from 'src/environments/environment';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { Component } from '@angular/core';

@Component({
  selector: 'app-package-merchants',
  templateUrl: './package-merchants.component.html',
  styleUrls: ['./package-merchants.component.scss'],
  providers: [MessageService],
})
export class PackageMerchantsComponent {
  userCurrency: string = (localStorage.getItem(environment.CURRENCY_SYMBOL)|| 'null')

  items: GetListResponse<MerchantInvitation> = {
    data: [],
    totalCount: 0,
  };
  loading: boolean = false;
  pageSize: number = environment.PAGE_SIZE;
  lastFilter: LazyLoadEvent = { filter: {}, first: 0 } as LazyLoadEvent;
  filter: string = '';
  package_reference: string;
  constructor(
    private service: PackageService,
    private messageService: MessageService,
    private router: Router,
    private activatedRoute: ActivatedRoute
  ) {}
  ngOnInit(): void {
    this.activatedRoute.params.subscribe((id) => {
      this.package_reference = id['reference'];
      this.loadList(this.lastFilter);
    });
  }
  loadList(event: LazyLoadEvent) {
    this.loading = true;
    this.lastFilter = event;
    this.service
      .merchantList({
        limit: this.pageSize,
        offset: event.first as number,
        name: this.filter,
        package: this.package_reference,
        sorting: event.sortField
          ? `${event.sortField} ${event.sortOrder === 1 ? 'asc' : 'desc'}`
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
            summary: $localize`Loading Merchant Failed`,
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
}
