import { CreateAccountForm } from "@/lib/ledger/components/CreateAccountForm";
import { AccountList } from "@/lib/ledger/components/AccountList";

export default function AccountsPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-8 p-8">
      <CreateAccountForm />
      <AccountList />
    </div>
  );
}
