export interface spWebsiteKey {
  id: number;
  name: string;
  website_redeemly_api_key: string;
}
export interface WebsiteName {
  website_name: string | null | undefined;
}
export interface WebsiteApiKeysBody {
  limit: number;
  offset: number;
  website_name: string;
}
