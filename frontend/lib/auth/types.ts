import type { User } from "@/lib/users/types";

export type AccessToken = {
  accessToken: string;
  tokenType: "bearer";
};

export type AuthResponse = {
  user: User;
  tokens: AccessToken;
};
