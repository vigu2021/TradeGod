import { apiClient } from "../core/api/client";
import { User } from "./types";

export const getUser = async () => {
  const response = await apiClient.get<User>("/users/me");
  return response.data;
};
