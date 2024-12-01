import { BaseResponse } from '../../../../models/responses/base-response.model';
import { ActivatedRoute, Router } from '@angular/router';
import { ProductService } from '../../../services/Product/product.service';
import { environment } from '../../../../environments/environment.staging';
import { GetListResponse } from '../../../../models/responses/get-response.model';
import { Product } from '../../../../models/Product/models';
import { Component, OnInit } from '@angular/core';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { ExcelService } from 'src/app/services/excel.service';
import { createSelector, Store } from '@ngrx/store';
import { confirmAction } from 'src/store/confirmationSlice';
import { Country } from 'src/models/country/model';
import { accessRightFeature } from 'src/store/accessRightSlice';

@Component({
  selector: 'app-list-products',
  templateUrl: './list-products.component.html',
  styleUrls: ['./list-products.component.scss'],
  providers: [MessageService],
})
export class ListProductsComponent implements OnInit {
  items: GetListResponse<Product> = {
    data: [],
    totalCount: 0,
  };
  loading: boolean = false;
  pageSize: number = environment.PAGE_SIZE;
  lastFilter: LazyLoadEvent = { filter: {}, first: 0 } as LazyLoadEvent;
  locale = $localize.locale;

  dialogVisible = false;
  selectedProduct: Product = {} as Product;
  countries: GetListResponse<Country>;
  countriesOptions: Country[] =
    localStorage.getItem(environment.COUNTRIES) != undefined
      ? JSON.parse(localStorage.getItem(environment.COUNTRIES) || '')
      : this.getCountries();
  userRole: string;
  accessRole$ = this.store.select(
    createSelector(accessRightFeature, (state) => state.role)
  );
  category_id: string;
  product_name_filter: string = '';
  category_name_filter: string = '';

  constructor(
    private service: ProductService,
    private messageService: MessageService,
    private router: Router,
    private excelService: ExcelService,
    private store: Store,
    private route: ActivatedRoute
  ) {}
  ngOnInit(): void {
    this.accessRole$.subscribe((roles) => {
      this.userRole = roles[0];
    });
    this.category_id = this.route.snapshot.paramMap.get('categoryId')!;
  }

  loadList(event: LazyLoadEvent) {
    this.loading = true;
    this.service
      .getProductList({
        limit: this.pageSize,
        offset: event.first as number,
        name: this.product_name_filter,
        category_name: this.category_name_filter,
      })
      .subscribe((res) => {
        if (res.ok) {
          this.items.data = res.result.data;
          this.items.totalCount = res.result.totalCount;
          this.loading = false;
        } else {
          this.messageService.add({
            severity: 'error',
            summary: $localize`Loading Product Failed`,
            detail: res.message,
            life: 3000,
          });
        }
      });
  }
  applyFilter() {
    let ev: LazyLoadEvent = {};
    ev.first = 0;
    ev.sortField = '';
    this.loadList(ev);
  }

  delete(item: Product) {
    this.store.dispatch(
      confirmAction({
        message: $localize`Are you sure you want to delete this product?`,
        callbackFunction: () => {
          this.service.delete(item.id).subscribe((res: BaseResponse<any>) => {
            if (res.ok) {
              this.messageService.add({
                severity: 'success',
                summary: item.name,
                detail: res.message ?? $localize`Product Deleted Successfully`,
                life: 3000,
              });
              let event: LazyLoadEvent = {};
              event.first = 0;
              event.sortField = '';
              this.loadList(event);
            }
          });
        },
      })
    );
  }
  exportExcel() {
    this.service
      .getProductList({
        offset: 0,
        limit: this.items.totalCount,
        name: this.product_name_filter,
        category_name: this.category_name_filter,
      })
      .subscribe((res: any) => {
        const data = res.result.data;
        data.map((r: any) => {
          delete r.image;
        });
        this.excelService.convertJSONtoExcel(
          data,
          [
            $localize`ID`,
            $localize`Name [EN]`,
            $localize`Name [AR]`,
            $localize`Category Name [EN]`,
            $localize`How To Use [EN]`,
            $localize`How To Use [AR]`,
            $localize`Total Vouchers Stock`,
            $localize`Available Vouchers Stock`,
          ],
          $localize`Products`
        );
      });
  }

  goToDetails(product: Product): void {
    this.router.navigate(['/dashboard/product/details/', product.id]);
  }
  getProdutType(item: any) {
    if (item.is_prepaid) return $localize`Prepaid Card`;
    else return $localize`Voucher`;
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
    this.service.getCountries().subscribe((res) => {
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
  navigateToCreateProductPage() {
    this.router.navigate(['dashboard/product/create-product']);
  }
}
