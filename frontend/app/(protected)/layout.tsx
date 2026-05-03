"use client";

import { useUser } from "@/lib/users/hooks/useUser";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { data: user, isLoading, isError } = useUser();

  useEffect(() => {
    if (!isLoading && (isError || !user)) {
      router.replace("/login");
    }
  }, [user, isError, isLoading, router]);

  if (isLoading) {
    return <div> Loading.... </div>;
  }

  if (isError || !user) {
    return null;
  }

  return children;
}
