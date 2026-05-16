import { ApiError } from "@/lib/core/error/api-error";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createAccount } from "../api";
import { Account } from "../types";
import { AccountCreateRequest } from "../schemas";

export const useCreateAccount = () => {
  const queryClient = useQueryClient();

  return useMutation<Account, ApiError, AccountCreateRequest>({
    mutationFn: createAccount,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["accounts"] });
    },
  });
};
