import { NextResponse } from "next/server";

// This middleware used to redirect to /login based on whether an
// access_token cookie was present on the request. That only works
// when the frontend and backend share a domain (e.g. both on
// localhost in dev). In a real deployment the backend is on its own
// domain (e.g. Railway) and the frontend on its own (e.g. Vercel) --
// the cookie the backend sets is scoped to *its* domain and is never
// sent on a request to the frontend's own pages, so this check always
// saw "no cookie" and redirected every single visitor, logged in or
// not, straight back to /login on every protected page. That's not a
// partial bug, it's total: nobody could ever reach /dashboard or any
// other protected route post-deploy.
//
// There is no reliable way to check auth state from this middleware
// without an extra network round-trip to the backend on every
// navigation (defeating the point of a "fast" check) or restructuring
// the whole auth flow around a same-domain session cookie. Given each
// page already does its own correct, working check via useAuth()
// (which calls the backend with credentials: "include" and so
// correctly carries the cross-origin cookie), this middleware is
// removed entirely rather than patched -- a same-domain-only
// optimization that silently breaks the real, cross-domain deployment
// is worse than no optimization at all.
export function middleware() {
  return NextResponse.next();
}

export const config = {
  matcher: [],
};
