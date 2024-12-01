export interface CreateTax {
  name: string;
  amount_type: string;
  amount: number;
}

export interface RequestReport {
  offset: any;
  limit: any;
}
