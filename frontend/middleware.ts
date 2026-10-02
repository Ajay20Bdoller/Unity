import { NextRequest, NextResponse } from "next/server";

// Lightweight, cookie-presence-only check (not validity -- an expired
// or tampered token still passes this and gets caught properly by the
// API's real auth check, which is what actually protects every piece
// of data). This middleware only exists to redirect faster and avoid
// a flash of "loading..." before each page's own client-side useAuth()
// check would otherwise catch it -- it is not the security boundary.
const PROTECTED_PREFIXES = [
  "/dashboard",
  "/settings",
  "/student",
  "/parent",
  "/mentor",
  "/school",
  "/admin",
];

export function middleware(request: NextRequest) {
  const isProtected = PROTECTED_PREFIXES.some((prefix) =>
    request.nextUrl.pathname.startsWith(prefix)
  );
  if (!isProtected) return NextResponse.next();

  const token = request.cookies.get("access_token");
  if (!token) {
    const loginUrl = new URL("/login", request.url);
    return NextResponse.redirect(loginUrl);
  }
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/settings/:path*",
    "/student/:path*",
    "/parent/:path*",
    "/mentor/:path*",
    "/school/:path*",
    "/admin/:path*",
  ],
};
