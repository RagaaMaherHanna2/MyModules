export interface RequestInvoiceBody {
  merchant_reference: string;
  from_date: string;
  to_date: string;
}

export interface RequestInvoice {
  failure_reason: string;
  from_date: string;
  id: number;
  image: string;
  merchant: {
    name: string;
    reference: string;
  };
  state: string;
  to_date: string;
}

export interface BillLine {
  name: 'pull' | 'redeem';
  price_unit: number,
}
export interface Bill {
  id: number;
  invoice_date: string;
  lines: BillLine[];
  state: 'paid' | 'not_paid';
  total: number;
  payment_request_id: number[];
  bank_transfer_state: string[];
}
