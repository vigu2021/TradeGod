import { ApiError } from "@/lib/core/error/api-error";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createAccount } from "../api";
import { Account } from "../types";
import { AccountCreateRequest } from "../schemas";
import { toast } from "sonner";
import { messageFor } from "@/lib/core/error/messages";

export const useCreateAccount = () => {
  const queryClient = useQueryClient();

  return useMutation<Account, ApiError, AccountCreateRequest>({
    mutationFn: createAccount,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["accounts"] });
      toast.success("Account created");
    },
    onError: (error) => {
      toast.error(messageFor(error.code));
    },
  });
};
