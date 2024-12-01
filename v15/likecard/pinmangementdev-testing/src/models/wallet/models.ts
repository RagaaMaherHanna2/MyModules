export const DEPOSIT_TYPE: string = 'deposit';
export const CREDIT_TYPE: string = 'credit';
export const INVOICE_PAYMENT_TYPE: string = 'invoice_payment';

export class BankDetails {
  id: number | undefined;
  bank_name: string | undefined;
  bic: string | undefined;
  acc_number: string | undefined;
  account_class: string | undefined;
  account_type: string | undefined;
  iban: string | undefined;
  adib_swift_code: string | undefined;
}

export class BankTransfer {
  bank: number | undefined;
  toBank: number | undefined;
  transferAmount: number | undefined;
  bankTransferImage: any | undefined;
  state: string | undefined;
  note: string | undefined;
  type: string | undefined;
  invoice_id: number | undefined
}
export class BankTransferFilter {
  offset: number | undefined;
  limit: number | undefined;
  filter: string | undefined;
  type: string | undefined;
  sorting: string | undefined;
}
export interface BankTransferRequest {
  bank_name: string;
  date: string;
  id: number;
  image: string;
  merchant: string;
  note: string;
  state: string;
  to_bank: string;
  transfer_amount: string;
  type: string;
}
