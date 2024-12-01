import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { BaseResponse } from 'src/models/responses/base-response.model';

@Injectable({
  providedIn: 'root',
})
export class UserService {
  constructor(private http: HttpClient) {}

  getUserByReference(params: {
    reference: string;
  }): Observable<BaseResponse<{ name: string }>> {
    const body = {
      params,
    };
    return this.http.post<BaseResponse<{ name: string }>>(
      `${environment.API_URL}/exposed/get_user_by_reference`,
      body
    );
  }
}
