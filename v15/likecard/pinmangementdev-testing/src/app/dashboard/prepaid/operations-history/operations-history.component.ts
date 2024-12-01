import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { LazyLoadEvent, MessageService } from 'primeng/api';
import { CodeService } from 'src/app/services/Code/code.service';
import { environment } from 'src/environments/environment';
import { PrepaidCode } from 'src/models/prepaid/models';
import { GetListResponse } from 'src/models/responses/get-response.model';

@Component({
  selector: 'app-operations-history',
  templateUrl: './operations-history.component.html',
  styleUrls: ['./operations-history.component.scss']
})
export class OperationsHistoryComponent {

  items: GetListResponse<PrepaidCode> = {
    data: [],
    totalCount: 0,
  };
  productData: any;

  lastFilter: LazyLoadEvent = { filter: {}, first: 0 } as LazyLoadEvent;
  filter: string = '';
  pageSize: number = environment.PAGE_SIZE;
  code: string;
  constructor(private service: CodeService,
    private activatedRoute: ActivatedRoute,
    private messageService: MessageService) {

  }
  ngOnInit(): void {
    this.activatedRoute.params.subscribe((params) => {
      this.code = params['code']
      this.loadHistory(this.lastFilter);
    })
  }

  loadHistory(event: LazyLoadEvent) {

    this.lastFilter = event;
    this.service
      .getPrepaidRedeemHistory({
        limit: this.pageSize,
        offset: event.first as number,
        code: this.code,
      }
      )
      .subscribe((res) => {
        if (res.ok) {
          this.productData = res.result.serial;
          this.items.data = res.result.history.data;
          this.items.totalCount = res.result.history.totalCount;

        } else {
          this.messageService.add({
            severity: 'error',
            summary: $localize`Loading Operations History Failed`,
            detail: res.message,
            life: 3000,
          });
        }
      });
  }
  exportExcel() {

  }

}
