import { CreateTax } from '../Taxes/models';
import { Merchant } from './../Merchant/models';
import { Product } from './../Product/models';
export interface CreatePackage {
  package_name: string;
  package_name_ar: string;
  expiry_date: string;
  code_type: CodeType;
  code_separator: CodeSeparator;
  code_days_duration: number;
  code_hours_duration: number;
}
export interface Package {
  id: number;
  package_name: string;
  package_name_ar: string;
  reference: string;
  expiry_date: string;
  state: string;
  code_type: CodeType;
  code_separator: CodeSeparator;
  code_days_duration: number;
  code_hours_duration: number;
  generation_requests: GenerationRequest[] | [];
}
export interface PackageCode {
  pin_code: string;
  code: string;
  creation_date: string;
  product: {
    id: number;
    name: string;
    name_ar: string;
  };
  package: {
    id: number;
    package_name: string;
    package_name_ar: string;
  };
  redemption_date: string;
  expiry_date: string;
  pull_date: string;
  reference_user_id: string;
  status: string;
  pulled_by: {
    id: number;
    name: string;
  };
}

export interface RedeemResult extends PackageCode {
  redeem_result: {
    name: string;
    package_name: string;
    pin_code: string;
    image: string;
    voucher_type: string;
    voucher_secret: {
      SERIAL?: string;
    };
    how_to_use: string;
    how_to_user_ar: string;
    is_redeemed: boolean;
    redeemed_at: string;
    vendor: string;
    name_ar: string;
    package_name_ar: string;
  };
}
export interface PackageFilter {
  offset: number | undefined;
  limit: number | undefined;
  name: string | undefined;
  sorting: string | undefined;
}
export interface CodeFilter {
  reference: string | undefined;
  offset: number | undefined;
  limit: number | undefined;
  name: string | undefined;
  sorting: string | undefined;
  status: string[] | undefined;
  product: number[] | undefined;
  from: string | undefined;
  to: string | undefined;
}
export interface MerchantInvitation {
  merchant_name: string | undefined;
  merchant: {
    id: number | undefined;
    reference: string;
    name: string;
  };
  package: string | undefined;
  price: number | undefined;
  limit: number | undefined;
  expiry_date: string | undefined;
  enabled: boolean | undefined;
}
export interface inviteMerchantToProduct {
  merchant: string;
  product: string;
  price: number;
  limit: number;
  unlimited: boolean;
  tax_id: CreateTax
}
export interface MerchantInvitationFilter {
  offset: number | undefined;
  limit: number | undefined;
  name: string | undefined;
  sorting: string | undefined;
  package: string | undefined;
}

export interface GenerationRequest {
  create_date: string | undefined;
  start_time: string | undefined;
  end_time: string | undefined;
  state: string;
  lines: GenerationRequestLines | undefined;
}
export interface GenerationRequestLines {
  product: Product | undefined;
  quantity: number | undefined;
}
export enum CodeType {
  alphanumeric = 'alphanumeric',
  numeric = 'numeric',
  alpha = 'alpha',
}
export enum CodeSeparator {
  dash = '-',
  nothing = '',
}

export interface PackageProductLine {
  product: number;
  quantity: number;
}

export interface EditMerchantInvitation {
  enabled?: boolean;
  quantity?: number;
  id: number;
  price?: number;
  unlimited?: boolean;
}
