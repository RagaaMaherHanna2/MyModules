import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { Password } from 'primeng/password';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import {
  FoodicsLoginBody,
  FoodicsLoginResponse,
  FoodicsNewBody,
  FoodicsPreinstallResponse,
} from 'src/models/Foodics/models';
import { BaseResponse } from 'src/models/responses/base-response.model';

@Injectable({
  providedIn: 'root',
})
export class FoodicsService {
  constructor(private httpService: HttpClient, private router: Router) {}
  foodicsLogin(
    foodicsLoginBody: FoodicsLoginBody
  ): Observable<BaseResponse<FoodicsLoginResponse>> {
    const body = {
      params: {
        login: foodicsLoginBody.login,
        password: foodicsLoginBody.password,
      },
    };

    return this.httpService.post<BaseResponse<FoodicsLoginResponse>>(
      `${environment.API_URL}/foodics/authenticate`,
      body
    );
  }
  preInstall(): Observable<BaseResponse<FoodicsPreinstallResponse>> {
    return this.httpService.post<BaseResponse<FoodicsPreinstallResponse>>(
      `${environment.API_URL}/exposed/foodics/preinstall`,
      {}
    );
  }
  foodicsNew(foodicsNewBody: FoodicsNewBody): Observable<BaseResponse<any>> {
    const body = {
      params: {
        code: foodicsNewBody.code,
        state: foodicsNewBody.state,
      },
    };
    return this.httpService.post<BaseResponse<any>>(
      `${environment.API_URL}/exposed/foodics/foodics-new`,
      body
    );
  }
}
