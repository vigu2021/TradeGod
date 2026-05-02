import axios from "axios"
import {env} from "@/lib/core/env"

// globalToken state
let accessToken: string | null = null;

// Actions, should be reserved for only auth actions
export const setAccessToken = (token: string| null) => {accessToken = token};
export const getAccessToken = () => accessToken;


export const authApi= axios.create({
    baseURL: env.apiUrl,
    timeout: 5000,
    withCredentials: true,
    headers: {
        "Content-Type": "application/json",
        Accept: "application/json"
    },
});
