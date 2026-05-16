import { z } from "zod";
import { AccountType } from "./types";

export const accountCreateSchema = z.object({
  accountType: z.enum(AccountType),
  name: z.string().min(1, "Name is required").max(100, "Name must be 100 characters or fewer"),
  provider: z.string().nullish(),
});

export type AccountCreateRequest = z.infer<typeof accountCreateSchema>;
