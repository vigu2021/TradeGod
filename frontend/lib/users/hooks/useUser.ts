import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError } from "@/lib/core/error/api-error";
import { getUser } from "../api";
import { User } from "../types";

export const useUser = () => {
  return useQuery<User, ApiError>({
    queryKey: ["user"],
    queryFn: getUser,
  });
};
