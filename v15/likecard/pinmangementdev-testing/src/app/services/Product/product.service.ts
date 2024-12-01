import { GetListResponse } from './../../../models/responses/get-response.model';
import {
  CreateProduct,
  EditProduct,
  Product,
  ProductBatch,
  ProductBatchFilter,
  ProductFilter,
  netDragonParentCategory,
  shortProduct,
  stockHistory,
  stockHistoryFilter,
} from './../../../models/Product/models';
import { VoucherType } from 'src/models/Product/models';
import { Injectable, Inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { Observable } from 'rxjs';
import { InsertedBatchSerial } from 'src/models/serial/model';
import { environment } from 'src/environments/environment';
import { Country } from 'src/models/country/model';
@Injectable({
  providedIn: 'root',
})
export class ProductService {
  constructor(
    private http: HttpClient,
    @Inject('BASE_URL') private baseurl: string
  ) {}

  getVoucherTypeList(): Observable<BaseResponse<VoucherType[]>> {
    return this.http.post<BaseResponse<VoucherType[]>>(
      this.baseurl + '/exposed/get_voucher_types',
      {}
    );
  }
  createProduct(item: CreateProduct): Observable<BaseResponse<any>> {
    const body = {
      params: item,
    };

    return this.http.post<BaseResponse<any>>(
      this.baseurl + '/exposed/create_product',
      body
    );
  }
  editProduct(item: EditProduct): Observable<BaseResponse<any>> {
    const body = {
      params: item,
    };
    return this.http.post<BaseResponse<any>>(
      this.baseurl + '/exposed/edit_product',
      body
    );
  }
  getProductList(
    input: ProductFilter
  ): Observable<BaseResponse<GetListResponse<Product>>> {
    const body = {
      params: input,
    };
    return this.http.post<BaseResponse<GetListResponse<Product>>>(
      this.baseurl + '/exposed/list_products',
      body
    );
  }
  getProductBatches(
    input: ProductBatchFilter
  ): Observable<BaseResponse<GetListResponse<ProductBatch>>> {
    const body = {
      params: input,
    };
    return this.http.post<BaseResponse<GetListResponse<ProductBatch>>>(
      this.baseurl + '/exposed/get_product_batches',
      body
    );
  }
  delete(id: number): Observable<BaseResponse<any>> {
    const body = {
      params: { id: id },
    };
    return this.http.post<BaseResponse<any>>(
      this.baseurl + '/exposed/archive_product',
      body
    );
  }
  getProductDetails(
    id: number
  ): Observable<BaseResponse<GetListResponse<Product>>> {
    const body = {
      params: { product_id: id },
    };
    return this.http.post<BaseResponse<GetListResponse<Product>>>(
      this.baseurl + '/exposed/list_products',
      body
    );
  }
  getProductNameById(id: number): Observable<BaseResponse<string>> {
    const body = {
      params: { product_id: id },
    };
    return this.http.post<BaseResponse<string>>(
      this.baseurl + '/exposed/get_product_name_by_id',
      body
    );
  }
  insertSerials(params: InsertedBatchSerial): Observable<BaseResponse<{}>> {
    const body = {
      params,
    };
    return this.http.post<BaseResponse<{}>>(
      `${environment.API_URL}/exposed/insert_product_serials`,
      body
    );
  }
  freezeBatch(params: { id: number }): Observable<BaseResponse<{}>> {
    return this.http.post<BaseResponse<{}>>(
      `${environment.API_URL}/exposed/freeze_batch`,
      { params }
    );
  }

  unfreezeBatch(params: { id: number }): Observable<BaseResponse<{}>> {
    return this.http.post<BaseResponse<{}>>(
      `${environment.API_URL}/exposed/unfreeze_batch`,
      { params }
    );
  }

  getProductStockHistory(
    input: stockHistoryFilter
  ): Observable<BaseResponse<GetListResponse<stockHistory>>> {
    const body = {
      params: input,
    };
    return this.http.post<BaseResponse<GetListResponse<stockHistory>>>(
      this.baseurl + '/exposed/stock_history',
      body
    );
  }
  getProductsNotInvitedToMerchant(
    merchant_id: number
  ): Observable<BaseResponse<GetListResponse<shortProduct>>> {
    const body = {
      params: { merchant_id: merchant_id },
    };
    return this.http.post<BaseResponse<GetListResponse<shortProduct>>>(
      this.baseurl + '/exposed/get_product_not_invited_to_merchant',
      body
    );
  }

  getNetdragonProductCategory(
    sp_hash: string
  ): Observable<BaseResponse<GetListResponse<netDragonParentCategory>>> {
    const body = {
      params: { sp_hash: sp_hash },
    };
    return this.http.post<
      BaseResponse<GetListResponse<netDragonParentCategory>>
    >(this.baseurl + '/net_dragon/get_product_category', body);
  }
  getCountries(): Observable<BaseResponse<GetListResponse<Country>>> {
    return this.http.post<BaseResponse<GetListResponse<Country>>>(
      this.baseurl + '/exposed/get_countries',
      {}
    );
  }
}
