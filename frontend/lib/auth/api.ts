import {authApi} from "@/lib/auth/client";
import type { AuthResponse, RegisterRequest } from "@/lib/auth/types";

export const registerUser = async (payload: RegisterRequest): Promise<AuthResponse> => {
    const response = await authApi.post<AuthResponse>("/auth/register", payload)
    return response.data;
}

