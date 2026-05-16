"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { messageFor } from "@/lib/core/error/messages";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { accountCreateSchema } from "../schemas";
import { ACCOUNT_TYPE_LABELS, AccountType } from "../types";
import { toast } from "sonner";
import { useCreateAccount } from "../hooks/useCreateAccount";

type Input = z.input<typeof accountCreateSchema>;
type Output = z.output<typeof accountCreateSchema>;

export const CreateAccountForm = () => {
  const form = useForm<Input, unknown, Output>({
    resolver: zodResolver(accountCreateSchema),
    defaultValues: { accountType: undefined, name: "", provider: "" },
  });
  const { mutate, isPending } = useCreateAccount();

  const onSubmit = (data: Output) => {
    mutate(data, {
      onSuccess: () => {
        toast.success("Account created");
        form.reset();
      },
      onError: (err) => {
        toast.error(messageFor(err.code));
      },
    });
  };

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="bg-card w-full max-w-md space-y-6 rounded-xl border p-8 shadow-sm"
      >
        <div className="space-y-1">
          <h2 className="text-2xl font-semibold tracking-tight">New account</h2>
          <p className="text-muted-foreground text-sm">Track a place where you hold money or assets.</p>
        </div>

        <div className="space-y-4">
          <FormField
            control={form.control}
            name="accountType"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Type</FormLabel>
                <FormControl>
                  <select
                    {...field}
                    value={field.value ?? ""}
                    className="border-input bg-background focus-visible:ring-ring h-10 w-full rounded-md border px-3 text-sm focus-visible:ring-2 focus-visible:outline-none"
                  >
                    <option value="" disabled>
                      Select a type...
                    </option>
                    {Object.values(AccountType).map((type) => (
                      <option key={type} value={type}>
                        {ACCOUNT_TYPE_LABELS[type]}
                      </option>
                    ))}
                  </select>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Name</FormLabel>
                <FormControl>
                  <Input placeholder="Main checking" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="provider"
            render={({ field }) => (
              <FormItem>
                <FormLabel>
                  Provider <span className="text-muted-foreground font-normal">(optional)</span>
                </FormLabel>
                <FormControl>
                  <Input placeholder="Binance, Coinbase, ..." {...field} value={field.value ?? ""} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <Button type="submit" disabled={isPending} className="w-full">
          {isPending ? "Creating..." : "Create account"}
        </Button>
      </form>
    </Form>
  );
};
