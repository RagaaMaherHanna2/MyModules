import { FormControl } from '@angular/forms';

export interface CreateSalesReport {
  from_date: string;
  to_date: string;
  merchant_filter: any;
  product: any;
}

export interface RequestSaleReport {
  failure_reason: string;
  from_date: string;
  id: number;
  image: string;
  file: string;
  merchant_filter: {
    id: number;
    name: string;
  };
  state: string;
  to_date: string;
  product: string;
}
export interface IncomeReport {
  from_date: string;
  report_url: string;
  to_date: string;
}
export interface FeesReport {
  from_date: string;
  report_url: string;
  to_date: string;
}
export type IncomeRequestFormType = {
  date: FormControl<Date[] | null>;
};
export type FeesRequestFormType = {
  sp: FormControl<number | null>;
  merchant: FormControl<number | null>;
  date: FormControl<Date | null>;
};
export type DailyFeesRequestFormType = {
  sp: FormControl<number | null>;
  merchant: FormControl<number | null>;
};
export type CreateIncomeReportBody = {
  from_date: string;
  to_date: string;
};

export type CreateFeesReportBody = {
  from_date: string;
  to_date: string;
  sp: number;
  merchant: number;
};

export type DailyFeesReportbody = {
  service_provider_id: number;
  merchant_id: number;
  limit: number;
  offset: number;
};
export type DailyFees = {
  service_provider_name: string;
  merchant_name: string;
  pull_fees_count: number;
  pull_fees_total: number;
  redeem_fees_count: number;
  redeem_fees_total: number;
  report_date: string;
};
