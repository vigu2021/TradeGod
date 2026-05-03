"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { type RegisterRequest, registerSchema } from "@/lib/auth/schemas";
import { useRegister } from "../hooks/useRegister";
import { messageFor } from "@/lib/core/error/messages";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";

export const RegisterForm = () => {
  const form = useForm<RegisterRequest>({
    resolver: zodResolver(registerSchema),
    defaultValues: { username: "", email: "", password: "" },
  });
  const { mutate, isPending, error: submitError } = useRegister();

  const onSubmit = (data: RegisterRequest) => {
    mutate(data);
  };

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="bg-card w-full max-w-md space-y-8 rounded-xl border p-10 shadow-sm"
      >
        <div className="space-y-2 text-center">
          <h1 className="text-3xl font-semibold tracking-tight">Create an account</h1>
          <p className="text-muted-foreground text-base">Enter your details to get started.</p>
        </div>

        <div className="space-y-5">
          <FormField
            control={form.control}
            name="username"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-base">Username</FormLabel>
                <FormControl>
                  <Input placeholder="yourname" className="h-12 text-base" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-base">Email</FormLabel>
                <FormControl>
                  <Input type="email" placeholder="you@example.com" className="h-12 text-base" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-base">Password</FormLabel>
                <FormControl>
                  <Input type="password" placeholder="At least 8 characters" className="h-12 text-base" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="space-y-3">
          <Button type="submit" disabled={isPending} size="lg" className="h-12 w-full text-base">
            {isPending ? "Creating account..." : "Create account"}
          </Button>
          {submitError && <p className="text-destructive text-center text-sm">{messageFor(submitError.code)}</p>}
        </div>
      </form>
    </Form>
  );
};
