import type { ErrorCode } from "@/lib/core/error/codes";

const ERROR_MESSAGES = {
  internal_error: "Something went wrong. Please try again.",
  validation_failed: "Please check your input.",
  not_found: "Not found.",
  method_not_allowed: "Action not allowed.",
  already_exists: "That account already exists.",
  unauthenticated: "Please log in.",
  forbidden: "You don't have permission for that.",
  invalid_credentials: "Invalid email or password.",
  token_expired: "Your session expired. Please log in again.",
  invalid_token: "Your session is invalid. Please log in again.",
} as const satisfies Record<ErrorCode, string>;

export function messageFor(code: string | undefined): string {
  if (!code) return ERROR_MESSAGES.internal_error;
  return ERROR_MESSAGES[code as ErrorCode] ?? ERROR_MESSAGES.internal_error;
}
