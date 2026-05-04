import { useMutation, useQueryClient } from "@tanstack/react-query";
import { logoutUser } from "../api";
import { setAccessToken } from "@/lib/core/api/client";
import { ApiError } from "@/lib/core/error/api-error";

export const useLogout = () => {
  const queryClient = useQueryClient();

  return useMutation<void, ApiError>({
    mutationFn: logoutUser,
    onSettled: () => {
      queryClient.clear();
      setAccessToken(null);
    },
  });
};
