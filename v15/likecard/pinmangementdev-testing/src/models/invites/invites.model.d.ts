import { Merchant } from '../Merchant/models';
import { MerchantProductInvitation, Product } from '../Product/models';

interface MerchantInvitationOfListMerchants extends MerchantProductInvitation {
  balance: number;
  product_details: Product;
}

export type GetMerchantsBody = {
  limit: number | undefined;
  offset: number | undefined;
  id: number | undefined;
  name: string | undefined;
};
export interface MerchantsInviteList extends Merchant {
  all_merchant_invitations: MerchantInvitationOfListMerchants[];
}

export type MerchantInvite = {
  name: string | undefined;
  email: string | undefined;
  password: string | undefined;
};
export type MerchantInviteResponse = {
  name: string | undefined;
  email: string | undefined;
  password: string | undefined;
  id: number | undefined;
};
