import { useQuery } from "@tanstack/react-query";
import { Account } from "../types";
import { ApiError } from "@/lib/core/error/api-error";
import { listAccounts } from "../api";

export const useAccounts = () => {
  return useQuery<Account[], ApiError>({
    queryKey: ["accounts"],
    queryFn: listAccounts,
  });
};
