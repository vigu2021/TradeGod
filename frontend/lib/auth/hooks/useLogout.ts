import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ApiError } from "next/dist/server/api-utils";
import { useRouter } from "next/router";
import { logoutUser } from "../api";
import { setAccessToken } from "@/lib/core/api/client";

export const useLogout = () => {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation<void, ApiError>({
    mutationFn: logoutUser,
    onSettled: () => {
      queryClient.clear();
      setAccessToken(null);
      router.replace("/login");
    },
  });
};
