"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useLogout } from "@/lib/auth/hooks/useLogout";
import { useUser } from "@/lib/users/hooks/useUser";
import { Button } from "@/components/ui/button";

type NavItem = {
  label: string;
  href: string;
};

const navItems: NavItem[] = [{ label: "Dashboard", href: "/dashboard" }];

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { data: user } = useUser();
  const { mutate: logout, isPending } = useLogout();

  const handleLogout = () => {
    logout(undefined, {
      onSettled: () => router.push("/login"),
    });
  };

  return (
    <nav className="bg-background sticky top-0 z-40 border-b">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between gap-6 px-6">
        <Link href="/dashboard" className="text-lg font-semibold tracking-tight">
          TradeGod
        </Link>

        <div className="flex flex-1 items-center justify-center gap-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-md px-3 py-2 text-sm transition-colors ${
                  isActive
                    ? "bg-accent text-accent-foreground font-medium"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </div>

        <div className="flex items-center gap-3">
          {user && <span className="text-muted-foreground hidden text-sm sm:inline">{user.username}</span>}
          <Button onClick={handleLogout} disabled={isPending} variant="outline" size="sm">
            {isPending ? "Logging out..." : "Log out"}
          </Button>
        </div>
      </div>
    </nav>
  );
}
