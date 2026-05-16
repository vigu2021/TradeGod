import { apiClient } from "../core/api/client";
import { AccountCreateRequest } from "./schemas";
import { Account } from "./types";

export const listAccounts = async () => {
  const response = await apiClient.get<Account[]>("/accounts");
  return response.data;
};

export const createAccount = async (payload: AccountCreateRequest) => {
  const response = await apiClient.post<Account>("/accounts", payload);
  return response.data;
};

export const archiveAccount = async (accountId: number) => {
  await apiClient.post(`/accounts/${accountId}/archive`);
};
