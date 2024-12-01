import { ProductAttributeValue } from '../Product/models';

export type prepaidCheckBalanceRequest = {
  lines: prepaidCheckBalanceRequestCode[];
  language: string;
};
export type prepaidCheckBalanceRequestCode = {
  code: string;
  pin_code: string;
};
export interface PrepaidCode {
  found: boolean | undefined;
  expired: boolean | undefined;
  code: string | undefined;
  pin_code: string | undefined;
  email_id: string | undefined;
  balance: string | undefined;
  vendor: string | undefined;
  name: string | undefined;
  history: any;
  serial: any;
}

export type PrepaidHistoryOperation = {
  id: number;
  value: number;
  user_id: string;
  transaction_id: string;
  date: string;
};

export class PrepaidHistoryFilter {
  limit: number | undefined;
  code: string | undefined;
  offset: number | undefined;
}
export type PrepaidRedeemBodyWithHash = {
  code: string | undefined;
  pin_code: string | undefined;
  user_id: string | undefined;
  transaction_id: string | undefined;
  deduct_value: number | undefined;
  sp_hash: string | undefined;
  product_type: string | undefined;
  language: string;
  is_prepaid: boolean;
  secret: string | undefined;
  product_attribute_values: ProductAttributeValue[];
};
export interface RedeemPrepaidCodeRequest {
  code: string;
  user_id: string;
  language: string;
  deduct_value: number;
  transaction_id: string;
  pin_code: string;
  is_prepaid: true;
}

export interface RedeemPrepaidCodeResponse {
  name: string;
  product_name: string;
  pin_code: string;
  image: string;
  voucher_type: string;
  voucher_secret: any;
  how_to_use: string;
  how_to_use_ar: string;
  is_redeemed: boolean;
  vendor: string;
  'Original Value': number;
  value: number;
  remaining_value: number;
}
