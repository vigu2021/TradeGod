import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PUBLIC_ROUTES = new Set(["/login", "/register", "/"]);

export function proxy(request: NextRequest) {
  const path = request.nextUrl.pathname;
  if (PUBLIC_ROUTES.has(path)) return NextResponse.next();

  if (!request.cookies.has("refresh_token")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
