import { Merchant } from '../Merchant/models';
import { CreateTax } from '../Taxes/models';
import { Currency } from '../User';

export type CreateFormType = {
  name: any;
  name_ar: any;
  country_id: any;
  standard_price: any;
  purchase_currency_id: any;
  how_to_use: any;
  how_to_use_ar: any;
  direct_redeem_link: any;
  SKU: any;
  type: any;
  specific_attribute: any;
  expiry_date?: any;
  expiry_period?: any;
  serials_auto_generated?: any;
  value?: any;
  amount?: any;
  netdragon_product_category?: any;
  netdragon_product_description?: any;
  currency?: any;
  use_skarla_portal: any;
  product_attributes: any;
  foodics_discount_type?: any;
  foodics_discount_amount?: any;
  foodics_is_percent?: any;
  foodics_business_reference?: any;
  foodics_max_discount_amount?: any;
  foodics_include_modifiers?: any;
  foodics_allowed_products?: any;
  foodics_is_discount_taxable?: any;
  category_id?: any;
};
export interface CreateProduct {
  SKU: string;
  expiry_date: string;
  expiry_period: number | undefined;
  direct_redeem_link: string;
  how_to_use: string | undefined;
  how_to_use_ar: string | undefined;
  id: number;
  image: any | undefined;
  name: string;
  name_ar: string;
  country_id: string;
  standard_price: number;
  purchase_currency_id: number;
  price: number | undefined;
  is_prepaid: boolean;
  value: number | undefined;
  use_skarla_portal: boolean;
  serials_auto_generated: boolean;
  product_attributes: ProductAttribute[];
  enable_stock_history: boolean;
  product_specific_attribute: string | undefined;
  product_amount: number | undefined;
  netdragon_product_category: string | undefined;
  netdragon_product_description: string | undefined;
  product_currency: number | undefined;
  foodics_discount_type: string | undefined;
  foodics_discount_amount: number | undefined;
  foodics_is_percent: boolean | undefined;
  foodics_business_reference: string | undefined;
  foodics_max_discount_amount: number | undefined;
  foodics_include_modifiers: boolean | undefined;
  foodics_allowed_products: FoodicsAllowedProducts[] | undefined;
  foodics_is_discount_taxable: boolean | undefined;
  categ_id: number | undefined;
}
export interface EditProduct {
  SKU: string;
  expiry_date: string;
  expiry_period: number | undefined;
  direct_redeem_link: string;
  how_to_use: string | undefined;
  how_to_use_ar: string | undefined;
  id: number;
  image: any | undefined;
  name: string;
  name_ar: string;
  country_id: number | undefined;
  standard_price: number;
  purchase_currency_id: number;
  price: number | undefined;
  is_prepaid: boolean;
  value: number | undefined;
  use_skarla_portal: boolean;
  serials_auto_generated: boolean;
  product_attributes: ProductAttribute[];
  enable_stock_history: boolean;
  product_specific_attribute: string | undefined;
  product_amount: number | undefined;
  netdragon_product_category: number | undefined;
  netdragon_product_description: string | undefined;
  product_currency: number | undefined;
  foodics_discount_type: string | undefined;
  foodics_discount_amount: number | undefined;
  foodics_is_percent: boolean | undefined;
  foodics_business_reference: string | undefined;
  foodics_max_discount_amount: number | undefined;
  foodics_include_modifiers: boolean | undefined;
  foodics_allowed_products: FoodicsAllowedProducts[] | undefined;
  foodics_is_discount_taxable: boolean | undefined;
  categ_id: number | undefined;
}
export type FoodicsAllowedProducts = {
  product_id: string;
};

export type ProductAttribute = {
  id: number;
  name: string;
  type: string;
  required: boolean;
};

export type ProductAttributeValue = {
  id: number;
  value: any;
};

export type MerchantProductInvitation = {
  id: number;
  limit: number;
  price: number;
  product: string;
  pulled_serials_count: number;
  remaining_qty: number;
  merchant: Merchant;
  unlimited: boolean;
  enabled: boolean;
  tax_id: CreateTax;
  product_details: Product;
};
export type ProductBatch = {
  available_count: number;
  batch_count: number;
  batch_file: string;
  batch_sequence: string;
  create_date: string;
  id: number;
  redeemed_count: number;
  state: string;
};
export interface ProductBatchFilter {
  offset: number | undefined;
  limit: number | undefined;
  product_id: number | undefined;
}
export interface Product {
  SKU: string;
  direct_redeem_link: string;
  use_skarla_portal: boolean;
  how_to_use: string | undefined;
  how_to_use_ar: string | undefined;
  id: number;
  image: any | undefined;
  name: string;
  name_ar: string;
  country_id: number;
  standard_price: number;
  is_prepaid: boolean;
  value: number | undefined;
  expiry_date: string;
  expiry_period: number;
  price: number | undefined;
  product_serials_stock: number;
  inventory_status: {
    available_count: number;
    redeemed_count: number;
    expired_count: number;
    frozen_serial_count: number;
  };
  invited_merchant: MerchantProductInvitation[];
  batches: ProductBatch[];
  serials_auto_generated: boolean;
  product_attributes: ProductAttribute[];
  enable_stock_history: boolean;
  product_specific_attribute: string;
  product_amount: number;
  product_currency: Currency;
  netdragon_product_description: string;
  netdragon_product_category: netDragonParentCategory;
  foodics_discount_type: string;
  foodics_discount_amount: number;
  foodics_is_percent: boolean;
  foodics_business_reference: string;
  foodics_max_discount_amount: number;
  foodics_include_modifiers: boolean;
  foodics_allowed_products: FoodicsAllowedProducts[];
  foodics_is_discount_taxable: boolean;
  purchase_currency_id: Currency;
  purchase_cost: string;
  categ_id: number;
  categ_name: string;
}
export interface Permission {
  category: string;
  id: number;
  enabled: boolean;
  name_arabic: string;
  name_english: string;
  code: string;
}
export interface VoucherType {
  id: number | undefined;
  name: string | undefined;
  fields: ProductTypeField[] | undefined;
}

export interface ProductFilter {
  offset: number | undefined;
  limit: number | undefined;
  name: string | undefined;
  category_name: string | undefined;
}

export interface ProductTypeField {
  id: number;
  name: string | '';
  type: FieldType[] | {};
  required: boolean | undefined;
}

export enum FieldType {
  text = '1',
  number = '2',
  Boolean = '3',
}
export interface stockHistoryFilter {
  product_id: number | undefined;
}
export type stockHistory = {
  history_date: string;
  qty: string;
  total: number;
  available: number;
  pulled: number;
  frozen: number;
};
export type shortProduct = {
  id: string;
  name: string;
  purchase_cost: number;
};
export type netDragonParentCategory = {
  id: number;
  name: string;
};

export type SecretCode = {
  code: string;
  secret: string;
};
export interface RedeemOperation {
  id: number;
  date: string;
  value: number;
  user_id: string;
  transaction_id: string;
  product: {
    id: number;
    name: string;
    serial_number: string;
    is_prepaid: boolean;
    use_skarla_portal: boolean;
  };
  product_attributes_value: ProductAttributesWithValues[];
  website_name: string;
}
export type ProductAttributesWithValues = {
  id: number;
  name: string;
  type: string;
  required: boolean;
  value: any;
};
