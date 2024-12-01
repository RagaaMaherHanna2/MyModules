import { Component, Inject, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { TaxesService } from '../../../services/taxes/taxes.service';
import { ACTION_STATE } from 'src/app/shared/utils/constants';
import { environment } from 'src/environments/environment';
import { CreateTax, RequestReport } from '../../../../models/Taxes/models';
import { GetListResponse } from 'src/models/responses/get-response.model';
import { MessageService } from 'primeng/api';
import { LOCALE_ID } from '@angular/core';

@Component({
  selector: 'app-list-taxes',
  templateUrl: './list-taxes.component.html',
  styleUrls: ['./list-taxes.component.scss'],
})
export class ListTaxesComponent {
  taxes: GetListResponse<RequestReport> = { data: [], totalCount: 0 };
  pageSize = environment.PAGE_SIZE;
  loading: boolean = false;
  actionState = ACTION_STATE;
  locale = $localize.locale;
  page: number = 0;

  currentLanguage: String = this.localeId;

  constructor(
    private taxesService: TaxesService,
    private store: Store,
    private messageService: MessageService,
    @Inject(LOCALE_ID) private localeId: string
  ) {}

  loadList() {
    this.loading = true;
    this.taxesService
      .listTaxes({
        limit: this.pageSize,
        offset: this.page * this.pageSize,
      })
      .subscribe((res) => {
        if (res.ok) {
          this.taxes = res.result;
          this.loading = false;
        } else {
          this.messageService.add({
            severity: 'error',
            summary: $localize`Loading Orders Failed`,
            detail: res.message,
            life: 3000,
          });
        }
      });
  }

  getTaxes(): void {
    this.loading = true;
    this.taxesService
      .listTaxes({ offset: this.page * this.pageSize, limit: this.pageSize })
      .subscribe((res) => {
        this.taxes = res.result;
        this.loading = false;
      });
  }
  changePage(event: { first: number; rows: number }) {
    this.page = event.first / this.pageSize ?? this.page;
    this.getTaxes();
  }
  getTaxAmountFormated(tax: CreateTax) {
    return (
      tax.amount +
      (tax.amount_type === 'percent'
        ? '%'
        : localStorage.getItem(environment.CURRENCY_SYMBOL) || 'null')
    );
  }
}
