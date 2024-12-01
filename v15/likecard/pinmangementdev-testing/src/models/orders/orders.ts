import { Serial } from './../serial/model'
export interface Order {
    id: number;
    name: string;
    date: string;
    pulled_serials: Serial[];
    product_name:string;
    amount_total: number


}
export interface orderFilter {
    offset: number | undefined;
    limit: number | undefined;
    name: string | undefined;
    sorting: string | undefined;
    product_name:string | undefined;
    order_date:string | undefined
}