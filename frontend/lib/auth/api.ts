import { apiClient } from "@/lib/core/api/client";
import type { AuthResponse } from "@/lib/auth/types";
import type { LoginRequest, RegisterRequest } from "@/lib/auth/schemas";

export const registerUser = async (payload: RegisterRequest): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>("/auth/register", payload);
  return response.data;
};

export const loginUser = async (payload: LoginRequest): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>("/auth/login", payload);
  return response.data;
};
