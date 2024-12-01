export interface serviceProviderSummary {
    total_merchant_count: string;
    chart: ChartItem[]; 

}
export interface ChartItem{
    sales_count: number,
    sales_value: number,
    date: string
}


export interface merchantSummary {
    wallet_balance: string;
    merchant_invites: string;
    sold_total: string;
    pulled_quantity: string;
    last_pull_date: string;
}
export interface statisticsFilter{
    from_date: string;
}