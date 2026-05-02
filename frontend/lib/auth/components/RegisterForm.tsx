"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { type RegisterRequest, registerSchema } from "@/lib/auth/schemas";
import { useRegister } from "../hooks/useRegister";
import { messageFor } from "@/lib/core/error-messages";

export const RegisterForm = () => {
  const {
    register,
    handleSubmit,
    formState: { errors: fieldError, isSubmitting },
  } = useForm<RegisterRequest>({
    resolver: zodResolver(registerSchema),
  });
  const { mutate, isPending, error: submitError } = useRegister();

  const onSubmit = (data: RegisterRequest) => {
    mutate(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <label htmlFor="username">Username</label>
      <input id="username" {...register("username")} placeholder="Type your username here..." />
      {fieldError.username && <span>{fieldError.username.message}</span>}

      <label htmlFor="email">Email</label>
      <input id="email" {...register("email")} placeholder="Type your email here..." />
      {fieldError.email && <span>{fieldError.email.message}</span>}

      <label htmlFor="password">Password</label>
      <input id="password" {...register("password")} placeholder="Type your password here..." />
      {fieldError.password && <span>{fieldError.password.message}</span>}

      <button type="submit" disabled={isPending}>
        {isPending ? "Registering..." : "Register"}
      </button>

      {submitError && messageFor(submitError.code)}
    </form>
  );
};
