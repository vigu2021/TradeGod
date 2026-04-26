import axios from "axios"
import {env} from "@/lib/env"

export const authClient = axios.create({
    baseURL: env.apiUrl,
    timeout: 5000,
    withCredentials: true,
    headers: {
        "Content-Type": "application/json",
        Accept: "application/json"
    },
});
