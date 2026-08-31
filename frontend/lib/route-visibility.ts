const AUTH_ROUTES = new Set(["/auth/login", "/auth/register"]);

export function shouldShowSiteNav(pathname: string) {
  return !AUTH_ROUTES.has(pathname);
}
