import { ProductAttributeValue } from '../Product/models';

export interface Serial {
  serial_code: string;
  expiry_date?: string;
  product_id: number;
  product_name: string | undefined;
  SKU: string;
  serial_number?: string;
  state: string | undefined;
}

export interface code {
  serial: string | undefined;
  found: boolean | undefined;
  expired: boolean | undefined;
  expiry_date: string | undefined;
  pulled_by_reference: string | undefined;
  pulled_by_name: string | undefined;
  pull_date: string | undefined;
  name: string | undefined;
  image: string;
  how_to_use: string | undefined;
  product_type: string;
}

export type SerialsBatch = {
  id: number;
  batch_sequence: string | undefined;
  state: number | undefined;
  batch_file: string | undefined;
  batch_count: number | undefined;
  available_count: number | undefined;
  redeemed_count: number | undefined;
  create_date: string | undefined;
  product_id: number | undefined;
  product_name: string | undefined;
  vendor_name: string | undefined;
  product_purchase_price: number | undefined;
  notes: string | undefined;
  invoice_ref: string | undefined;
  batch_currency_name: string | undefined;
};

export interface SerialFilter {
  offset: number | undefined;
  limit: number | undefined;
  id: number | undefined;
  sorting: string | undefined;
  batch_sequence: string | undefined;
  create_date: string | undefined;
  product_name: string | undefined;
  vendor_name: string | undefined;
  invoice_ref: string | undefined;
  category_name: string | undefined;
  state: string | undefined;
}
export type SerialRedeemBodyWithHash = {
  code: string;
  sp_hash: string;
  product_type: string | undefined;
  product_attribute_values: ProductAttributeValue[];
  secret: string | undefined;
};
export interface InsertedBatchSerial {
  batch_sequence: string | undefined;
  product_id: number | undefined;
  batch_file: string | undefined;
  vendor_name: string | undefined;
  product_purchase_price: number | undefined;
  notes: string | undefined;
}
