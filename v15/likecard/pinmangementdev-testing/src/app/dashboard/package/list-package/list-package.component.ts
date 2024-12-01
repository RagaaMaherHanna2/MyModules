import { BaseResponse } from './../../../../models/responses/base-response.model';
import { Router } from '@angular/router';
import { PackageService } from './../../../services/Package/package.service';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { environment } from './../../../../environments/environment.staging';
import { GetListResponse } from './../../../../models/responses/get-response.model';
import { CreatePackage, Package } from './../../../../models/package/models';
import { Component } from '@angular/core';

@Component({
  selector: 'app-list-package',
  templateUrl: './list-package.component.html',
  styleUrls: ['./list-package.component.scss'],
  providers: [MessageService],
})
export class ListPackageComponent {
  items: GetListResponse<CreatePackage> = {
    data: [],
    totalCount: 0,
  };
  loading: boolean = false;
  pageSize: number = environment.PAGE_SIZE;
  lastFilter: LazyLoadEvent = { filter: {}, first: 0 } as LazyLoadEvent;
  filter: string = '';
  constructor(
    private service: PackageService,
    private messageService: MessageService,
    private router: Router
  ) { }
  ngOnInit(): void {
    this.loadList(this.lastFilter);
  }
  gotToCreate() {
    this.router.navigate(['dashboard/package/create-package']);
  }
  loadList(event: LazyLoadEvent) {
    this.loading = true;
    this.lastFilter = event;
    this.service
      .list({
        limit: this.pageSize,
        offset: event.first as number,
        name: this.filter,
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
    ev.first = 0;
    ev.sortField = '';
    this.loadList(ev);
  }
  goToDetails(item: Package) {
    this.router.navigate(['dashboard/package/details', item.reference]);
  }
  delete(item: Package) {
    this.service.delete(item.id ?? 0).subscribe((res: BaseResponse<any>) => {
      if (res.ok) {
        this.messageService.add({
          severity: 'success',
          summary: item.package_name,
          detail: res.message ?? $localize`Package Deleted Sucessfully`,
          life: 3000,
        });
        let event: LazyLoadEvent = {};
        event.first = 0;
        event.sortField = '';
        this.loadList(event);
      }
    });
  }
}
