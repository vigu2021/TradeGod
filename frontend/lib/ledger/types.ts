export enum AccountType {
  CASH = "cash",
  BANK = "bank",
  BROKERAGE = "brokerage",
  CRYPTO_EXCHANGE = "crypto_exchange",
  WALLET = "wallet",
}

export type Account = {
  id: number;
  account_type: AccountType;
  name: string;
  provider: string | null;
  created_at: string;
  updated_at: string;
};
