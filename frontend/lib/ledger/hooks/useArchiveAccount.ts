import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ApiError } from "@/lib/core/error/api-error";
import { archiveAccount } from "../api";
import { toast } from "sonner";
import { messageFor } from "@/lib/core/error/messages";

export const useArchiveAccounts = () => {
  const queryClient = useQueryClient();

  return useMutation<void, ApiError, number>({
    mutationFn: archiveAccount,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["accounts"] });
      toast.success("Archived account");
    },
    onError: (error) => {
      if (error.code === "not_found") {
        // stale list: account was already deleted/archived elsewhere; refresh
        toast.error("Account no longer exists.");
        void queryClient.invalidateQueries({ queryKey: ["accounts"] });
        return;
      }
      toast.error(messageFor(error.code));
    },
  });
};
