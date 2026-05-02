import { useMutation, useQueryClient } from "@tanstack/react-query";
import { registerUser } from "../api";
import { setAccessToken } from "../client";
import { ApiError } from "@/lib/core/error/api-error";
import type { AuthResponse } from "../types";
import type { RegisterRequest } from "../schemas";

export const useRegister = () => {
  const queryClient = useQueryClient();

  return useMutation<AuthResponse, ApiError, RegisterRequest>({
    mutationFn: registerUser,
    onSuccess: (data) => {
      setAccessToken(data.tokens.accessToken);
      queryClient.setQueryData(["user"], data.user);
    },
  });
};
