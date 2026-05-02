import { useMutation, useQueryClient } from "@tanstack/react-query";
import { loginUser } from "../api";
import { setAccessToken } from "../client";
import { ApiError } from "@/lib/core/api-error";
import type { AuthResponse } from "../types";
import type { LoginRequest } from "../schemas";

export const useLogin = () => {
  const queryClient = useQueryClient();

  return useMutation<AuthResponse, ApiError, LoginRequest>({
    mutationFn: loginUser,
    onSuccess: (data) => {
      setAccessToken(data.tokens.accessToken);
      queryClient.setQueryData(["user"], data.user);
    },
  });
};
