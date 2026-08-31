import { NextResponse, type NextRequest } from "next/server";

const AUTH_COOKIE = "sxuwhateat_auth";
const PUBLIC_PREFIXES = ["/auth/login", "/auth/register", "/_next", "/favicon.ico"];

export function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  const isPublic =
    PUBLIC_PREFIXES.some((prefix) => pathname.startsWith(prefix)) ||
    /\.[a-zA-Z0-9]+$/.test(pathname);

  if (isPublic) return NextResponse.next();
  if (request.cookies.get(AUTH_COOKIE)?.value) return NextResponse.next();

  const loginUrl = request.nextUrl.clone();
  loginUrl.pathname = "/auth/login";
  loginUrl.search = "";
  loginUrl.searchParams.set("next", `${pathname}${search}`);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: ["/((?!api).*)"]
};
