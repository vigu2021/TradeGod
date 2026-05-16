export enum AccountType {
  CASH = "cash",
  BANK = "bank",
  BROKERAGE = "brokerage",
  CRYPTO_EXCHANGE = "crypto_exchange",
  WALLET = "wallet",
}

export type Account = {
  id: number;
  accountType: AccountType;
  name: string;
  provider: string | null;
  createdAt: string;
  updatedAt: string;
};
