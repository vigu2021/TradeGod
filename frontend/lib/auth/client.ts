import axios, { AxiosError } from "axios";
import { env } from "@/lib/core/env";
import { ApiError } from "@/lib/core/api-error";

// globalToken state
let accessToken: string | null = null;

// Actions, should be reserved for only auth actions
export const setAccessToken = (token: string | null) => {
  accessToken = token;
};
export const getAccessToken = () => accessToken;

type ApiErrorPayload = {
  code: string;
  detail?: string;
};

export const authApi = axios.create({
  baseURL: env.apiUrl,
  timeout: 5000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

authApi.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorPayload>) => {
    if (error.response) {
      throw new ApiError(
        error.response.data?.code ?? "internal_error",
        error.response.status,
        error.response.data?.detail,
      );
    }
    // network error, timeout, no response
    throw new ApiError("internal_error", 0, error.message);
  },
);
