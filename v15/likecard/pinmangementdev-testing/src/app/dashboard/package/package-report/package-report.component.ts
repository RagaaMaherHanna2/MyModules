import { filter } from 'rxjs';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { Router, ActivatedRoute } from '@angular/router';
import { PackageService } from './../../../services/Package/package.service';
import { Product } from './../../../../models/Product/models';
import { environment } from 'src/environments/environment';
import { PackageCode, CodeFilter } from './../../../../models/package/models';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-package-report',
  templateUrl: './package-report.component.html',
  styleUrls: ['./package-report.component.scss'],
})
export class PackageReportComponent implements OnInit {
  codes: PackageCode[] = [];
  selectedCodes: PackageCode[] = [];
  totalRecords: number;
  pageSize: number = environment.PAGE_SIZE;
  products: Product[] = [];
  loading: boolean = false;
  package_Reference: string;
  filterDate: string;
  NOT_YET = $localize`Not Yet`;
  NO = $localize`No`;
  constructor(
    private service: PackageService,
    private router: Router,
    private activatedRoute: ActivatedRoute
  ) {}
  filter: CodeFilter = {
    reference: '',
    from: '',
    limit: this.pageSize,
    name: '',
    offset: 0,
    product: [],
    sorting: '',
    status: [],
    to: '',
  };
  ngOnInit(): void {
    this.activatedRoute.params.subscribe((id) => {
      this.package_Reference = id['reference'];
      this.filter.reference = this.package_Reference;
      this.service
        .getProductPackage({ reference: this.package_Reference })
        .subscribe((res: BaseResponse<GetListResponse<Product>>) => {
          this.products = res.result.data;
        });
    });
    this.loadlist({
      filters: { status: null, offset: 0, limit: 10},
    });
  }

  onPage(event: any): void {
    this.filter.offset = event.first;
    this.loadlist({ filters: this.filter });
  }
  loadlist(event: any): void {
    let filter: CodeFilter = {} as CodeFilter;
    filter.offset = event.filters.offset;
    filter.reference = this.package_Reference;
    filter.status =
      event.filters.status == null || event.filters.status.value == null
        ? []
        : event.filters.status.value.map((res: any) => {
            return res.value;
          });
    filter.product =
      event.filters['product.name'] == null ||
      event.filters['product.name'].value == null
        ? []
        : event.filters['product.name'].value.map((res: any) => {
            return res.id;
          });
    filter.from = event.filters['date_filter'];
    this.service
      .listCode(filter)
      .subscribe((res: BaseResponse<GetListResponse<PackageCode>>) => {
        this.codes = res.result.data;
        this.totalRecords = res.result.totalCount;
      });
  }
  onSelectionChange(value = []) {
    this.selectedCodes = value;
  }
  get_all_code_status() {
    return [
      { name: 'generated', value: 'generated' },
      { name: 'pulled', value: 'pulled' },
      { name: 'redeemed', value: 'redeemed' },
      { name: 'expired', value: 'expired' },
    ];
  }
  getStatusClass(status: string): string {
    if (status === 'pulled') {
      return 'warning';
    } else if (status === 'redeemed') {
      return 'success';
    } else if (status === 'expired') {
      return 'danger';
    }
    return '';
  }
}
