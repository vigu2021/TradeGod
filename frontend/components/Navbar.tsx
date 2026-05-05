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
    <nav className="bg-background/80 sticky top-0 z-40 border-b backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-14 items-center gap-8 px-6">
        <Link href="/dashboard" className="group flex items-center gap-2.5">
          <div className="bg-foreground text-background flex h-7 w-7 items-center justify-center rounded-md text-sm font-bold tracking-tight">
            T
          </div>
          <span className="text-[15px] font-semibold tracking-tight transition-opacity group-hover:opacity-70">
            TradeGod
          </span>
        </Link>

        <div className="flex items-center gap-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-muted text-foreground"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted/60"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </div>

        <div className="ml-auto flex items-center gap-3">
          {user && (
            <div className="hidden items-center gap-2.5 sm:flex">
              <div className="from-foreground to-foreground/70 text-background flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br text-xs font-semibold uppercase">
                {user.username.charAt(0)}
              </div>
              <div className="flex flex-col leading-tight">
                <span className="text-foreground text-sm font-medium">{user.username}</span>
                <span className="text-muted-foreground text-[11px]">{user.email}</span>
              </div>
            </div>
          )}
          <div className="bg-border mx-1 hidden h-6 w-px sm:block" />
          <Button
            onClick={handleLogout}
            disabled={isPending}
            variant="ghost"
            size="sm"
            className="text-muted-foreground hover:text-foreground"
          >
            {isPending ? "..." : "Log out"}
          </Button>
        </div>
      </div>
    </nav>
  );
}
