import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { env } from "@/lib/core/env";
import { ApiError } from "@/lib/core/error/api-error";
import { ERROR_CODES } from "../error/codes";
import type { AccessToken } from "@/lib/auth/types";

let accessToken: string | null = null;

export const setAccessToken = (token: string | null) => {
  accessToken = token;
};
export const getAccessToken = () => accessToken;
type ApiErrorPayload = { code: string; detail?: string };
type RetriableRequestConfig = InternalAxiosRequestConfig & {
  _retry?: boolean;
};

export const apiClient = axios.create({
  baseURL: env.apiUrl,
  timeout: 5000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// Attach accessToken to every request
apiClient.interceptors.request.use((config) => {
  const accessToken = getAccessToken();
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Bare axios so a 401 from /refresh doesn't loop back through this interceptor
const refreshAccessToken = async (): Promise<string> => {
  const { data } = await axios.post<{ tokens: AccessToken }>(`${env.apiUrl}/auth/refresh`, null, {
    withCredentials: true,
  });
  return data.tokens.accessToken;
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiErrorPayload>) => {
    if (!error.response) {
      throw new ApiError("internal_error", 0, error.message);
    }

    const errorCode = error.response.data?.code ?? "internal_error";
    const status = error.response.status;
    const detail = error.response.data?.detail;
    const originalRequest = error.config as RetriableRequestConfig | undefined;

    if (!originalRequest) {
      throw new ApiError(errorCode, status, detail);
    }

    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const newToken = await refreshAccessToken();
        setAccessToken(newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      } catch {
        // refresh dead, drop the token and clear the stale cookie so the proxy stops bouncing /login back to /
        setAccessToken(null);
        await axios.post(`${env.apiUrl}/auth/logout`, null, { withCredentials: true }).catch(() => {});
        throw new ApiError(ERROR_CODES.UNAUTHENTICATED, 401, "Session expired");
      }
    }

    throw new ApiError(errorCode, status, detail);
  },
);
