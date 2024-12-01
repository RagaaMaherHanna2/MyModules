import { Serial } from '../serial/model';
import { Product } from './../Product/models';
export interface MerchantPackage {
  reference: string | undefined;
  price: number | undefined;
  limit: number | undefined;
  package_name: string | undefined;
  package_name_ar: string | undefined;
  products: Product[] | [];
  pulled_codes_count: number;
  redeemed_codes_count: number;
}
export interface MerchantProduct {
  id: number;
  merchant: Merchant;
  product: string;
  price: number;
  unlimited: boolean;
  limit: number;
  pulled_serials_count: number;
  remaining_qty: 20;
  enabled: true;
}

export interface MerchantProductDetails extends MerchantProduct {
  tax_id: {
    amount: number | undefined;
    amount_type: string | undefined;
    name: string | undefined;
  };
  product_details: Product;
  is_prepaid: boolean;
}

export interface MerchantProductFilter {
  offset?: number;
  limit?: number;
  id?: number;
  name?: string;
  sorting?: string;
}
export interface PulledCodes {
  pin_code: string | undefined;
  code: string | undefined;
}
export interface MerchantPackageFilter {
  offset: number | undefined;
  limit: number | undefined;
  reference: string | undefined;
  name: string | undefined;
  sorting: string | undefined;
}
export interface PullCodeRequest {
  product: number;
  quantity: number;
}
export interface PrepaidPullCodeRequest {
  product: number;
  quantity: number;
  email_id: string | undefined;
}

export interface Merchant {
  id: number;
  reference: string;
  name: string | undefined;
  email?: string | undefined;
}
export interface PullCodesResponse {
  order: string;
  pulled_serials: Serial[];
}

export interface IdName {
  id: number;
  name: string;
}
