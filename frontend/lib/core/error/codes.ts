export const ERROR_CODES = {
  INTERNAL_ERROR: "internal_error",
  VALIDATION_FAILED: "validation_failed",
  NOT_FOUND: "not_found",
  METHOD_NOT_ALLOWED: "method_not_allowed",
  ALREADY_EXISTS: "already_exists",
  UNAUTHENTICATED: "unauthenticated",
  FORBIDDEN: "forbidden",
  INVALID_CREDENTIALS: "invalid_credentials",
  TOKEN_EXPIRED: "token_expired",
  INVALID_TOKEN: "invalid_token",
} as const;

export type ErrorCode = (typeof ERROR_CODES)[keyof typeof ERROR_CODES];
