import { HttpClient } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { CategoriesFilters, Category } from 'src/models/category/model';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { GetListResponse } from 'src/models/responses/get-response.model';
@Injectable({
  providedIn: 'root',
})
export class CategoryService {
  constructor(
    private http: HttpClient,
    @Inject('BASE_URL') private baseurl: string
  ) {}

  getCategoryList(
    input: CategoriesFilters
  ): Observable<BaseResponse<GetListResponse<Category>>> {
    const body = {
      params: input,
    };
    return this.http.post<BaseResponse<GetListResponse<Category>>>(
      this.baseurl + '/exposed/get_categories',
      body
    );
  }
  createCategory(item: Category): Observable<BaseResponse<any>> {
    const body = {
      params: item,
    };

    return this.http.post<BaseResponse<any>>(
      this.baseurl + '/exposed/create_category',
      body
    );
  }
  editCategory(item: Category): Observable<BaseResponse<any>> {
    const body = {
      params: item,
    };

    return this.http.post<BaseResponse<any>>(
      this.baseurl + '/exposed/edit_category',
      body
    );
  }
  deleteCategory(id: number): Observable<BaseResponse<any>> {
    const body = {
      params: { id: id },
    };
    return this.http.post<BaseResponse<any>>(
      this.baseurl + '/exposed/archive_category',
      body
    );
  }
}
