import { HttpClient } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { BaseResponse } from 'src/models/responses/base-response.model';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { SerialFilter, SerialsBatch } from 'src/models/serial/model';

@Injectable({
  providedIn: 'root',
})
export class SerialsBatchesService {
  constructor(
    private http: HttpClient,
    @Inject('BASE_URL') private baseurl: string
  ) {}
  getBatchesList(
    input: SerialFilter
  ): Observable<BaseResponse<GetListResponse<SerialsBatch>>> {
    const body = {
      params: input,
    };
    return this.http.post<BaseResponse<GetListResponse<SerialsBatch>>>(
      this.baseurl + '/exposed/batch_serial_list',
      body
    );
  }
  sendBatchSerialViaEmail(id: number) {
    const body = {
      params: { id: id },
    };
    return this.http.post<BaseResponse<GetListResponse<SerialsBatch>>>(
      this.baseurl + '/exposed/send_batch_serial_via_email',
      body
    );
  }
}
