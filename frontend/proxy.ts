import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const AUTH_ROUTES = new Set(["/login", "/register"]);

export function proxy(request: NextRequest) {
  const refreshToken = request.cookies.has("refresh_token");
  const isAuthRoute = AUTH_ROUTES.has(request.nextUrl.pathname);

  // Logged in users should not see the auth routes, redirect them
  if (refreshToken && isAuthRoute) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  // Public auth routes allowed for logged out users
  if (isAuthRoute) {
    return NextResponse.next();
  }

  // Everything else requires auth
  if (!refreshToken) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
