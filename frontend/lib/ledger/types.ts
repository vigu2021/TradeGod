export enum AccountType {
  CASH = "cash",
  BANK = "bank",
  BROKERAGE = "brokerage",
  CRYPTO_EXCHANGE = "crypto_exchange",
  WALLET = "wallet",
}

export const ACCOUNT_TYPE_LABELS: Record<AccountType, string> = {
  [AccountType.CASH]: "Cash",
  [AccountType.BANK]: "Bank",
  [AccountType.BROKERAGE]: "Brokerage",
  [AccountType.CRYPTO_EXCHANGE]: "Crypto exchange",
  [AccountType.WALLET]: "Wallet",
};

export type Account = {
  id: number;
  accountType: AccountType;
  name: string;
  provider: string | null;
  createdAt: string;
  updatedAt: string;
};
