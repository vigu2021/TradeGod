"use client";

import { Button } from "@/components/ui/button";
import { messageFor } from "@/lib/core/error/messages";
import { useAccounts } from "../hooks/useAccounts";
import { ACCOUNT_TYPE_LABELS } from "../types";
import { useState } from "react";
import { useArchiveAccount } from "../hooks/useArchiveAccount";
import { toast } from "sonner";

export const AccountList = () => {
  const { data: accounts, isPending, isError, error, refetch } = useAccounts();
  const [archivingId, setArchivingId] = useState<number | null>(null);
  const archive = useArchiveAccount();

  const archiveAccount = (accountId: number) => {
    setArchivingId(accountId);
    archive.mutate(accountId, {
      onSettled: () => setArchivingId(null),
      onSuccess: () => toast.success("Account archived"),
      onError: (error) => {
        if (error.code === "not_found") {
          toast.error("Account no longer exists.");
        } else {
          toast.error(messageFor(error.code));
        }
      },
    });
  };

  if (isPending) {
    return <p className="text-muted-foreground text-sm">Loading accounts...</p>;
  }

  if (isError) {
    return (
      <div className="space-y-2">
        <p className="text-destructive text-sm">{messageFor(error.code)}</p>
        <Button variant="outline" size="sm" onClick={() => void refetch()}>
          Try again
        </Button>
      </div>
    );
  }

  if (accounts.length === 0) {
    return <p className="text-muted-foreground text-sm">No accounts yet. Create one above.</p>;
  }

  return (
    <ul className="divide-border divide-y rounded-md border">
      {accounts.map((account) => (
        <li key={account.id} className="flex items-center justify-between px-4 py-3">
          <div className="space-y-0.5">
            <p className="font-medium">{account.name}</p>
            <p className="text-muted-foreground text-xs">
              {ACCOUNT_TYPE_LABELS[account.accountType]}
              {account.provider ? ` · ${account.provider}` : ""}
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => archiveAccount(account.id)}
            disabled={archivingId === account.id}
          >
            {archivingId === account.id ? "Archiving..." : "Archive"}
          </Button>
        </li>
      ))}
    </ul>
  );
};
