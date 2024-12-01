import { ProductAttribute } from '../Product/models';

export interface DashboardUser {
  email: string;
  name: string;
  roles: string[];
  reference?: string;
  redeemly_api_key?: string;
  sp_hash?: string;
  totp_enabled: Boolean;
  user: object;
  permissions: any[];
  currency_symbol: string;
  codes_additional_value: string;
  default_categ_id: number;
}

export type AuthenticateResponse = {
  token: string;
  first_login: string;
  is_2factor: string;
  key: string;
};
export type TwoFactorAuthentication = {
  qrcode: string;
  secret: string;
};

export type ProfileResponse = {
  token: string;
  first_login: string;
};

export type ServiceProviderProfile = {
  codes_additional_value: string;
  user: SPdata;
  product_attributes: ProductAttribute[][];
};
export type SPdata = {
  name: string;
  email: string;
  logo: string;
  portal_welcome_text: string;
};

export class SPNotificationsSettings {
  stock_limit: number;
  enable_low_stock_notification: boolean;
  stock_notification_to_email: string;
}

export class merchantNotificationsSettings {
  balance_limit: number;
  enable_low_balance_notification: boolean;
  balance_notification_to_email: string;
}

export class Currency {
  id: number;
  symbol: string;
}
