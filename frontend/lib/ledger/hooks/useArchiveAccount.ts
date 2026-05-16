import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ApiError } from "@/lib/core/error/api-error";
import { archiveAccount } from "../api";

export const useArchiveAccount = () => {
  const queryClient = useQueryClient();

  return useMutation<void, ApiError, number>({
    mutationFn: archiveAccount,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["accounts"] });
    },
    onError: (error) => {
      // stale list: account was already deleted/archived elsewhere; refetch so the row disappears
      if (error.code === "not_found") {
        void queryClient.invalidateQueries({ queryKey: ["accounts"] });
      }
    },
  });
};
