export interface Vendor {
  id: number;
  name: string;
}
export interface GetVendorsBody {
  limit: number | undefined;
  offset: number | undefined;
  name: string | undefined;
}
