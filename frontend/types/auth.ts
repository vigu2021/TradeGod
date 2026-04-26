import type { User } from "@/types/user";

export type AccessToken = {
  accessToken: string;
  tokenType: "bearer";
};

export type AuthResponse = {
  user: User;
  tokens: AccessToken;
};
