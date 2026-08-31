export const AUTH_CHANGED_EVENT = "sxuwhateat-auth-changed";

export function notifyAuthChanged() {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event(AUTH_CHANGED_EVENT));
}
