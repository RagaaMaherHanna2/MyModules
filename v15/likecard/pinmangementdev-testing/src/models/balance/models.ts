import { Package } from 'src/models/package/models';
import { Merchant } from './../Merchant/models';
import { Product } from './../Product/models';
export interface TransactionLog {
  id: string | undefined;
  create_date: string | undefined;
  amount: number | undefined;
  description: string | undefined;
}
export interface TransactionLogFilter {
  offset: number | undefined;
  limit: number | undefined;
  description: string | undefined;
  sorting: string | undefined;
}
export interface SalesReport {
  id: string | undefined;
  created_date: string | Date | undefined;
  ref: string;
  amount: number | undefined;
  merchant: string;
  package_name: string;
  package_name_ar: string;
  product: string;
  description: string;
}
export interface SalesReportFilter {
  offset: number | undefined;
  limit: number | undefined;
  products: Product[] | [];
  merchants: Merchant[] | [];
  packages: Package[] | [];
}
export interface FilterSelectionData {
  products: Product[] | [];
  packages: Package[] | [];
  merchants: Merchant[] | [];
}
