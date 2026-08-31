"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LogOut, ShieldCheck } from "lucide-react";

import { api, clearStoredToken } from "@/lib/api";
import { AUTH_CHANGED_EVENT } from "@/lib/auth-events";
import { shouldShowSiteNav } from "@/lib/route-visibility";
import type { User } from "@/lib/types";

export function SiteNav() {
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    function loadUser() {
      api
        .me()
        .then(setUser)
        .catch(() => {
          setUser(null);
        });
    }

    loadUser();
    window.addEventListener(AUTH_CHANGED_EVENT, loadUser);
    window.addEventListener("storage", loadUser);
    return () => {
      window.removeEventListener(AUTH_CHANGED_EVENT, loadUser);
      window.removeEventListener("storage", loadUser);
    };
  }, []);

  const canSeeAdmin = user?.role === "ADMIN" || user?.role === "SUPER_ADMIN";
  const navigation = [
    { href: "/draw", label: "每日抽签" },
    { href: "/canteens", label: "食堂窗口" },
    { href: "/personalize", label: "个性筛选" }
  ];

  if (!shouldShowSiteNav(pathname)) return null;

  return (
    <header className="border-b border-ink/10 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-2 px-4 py-3">
        <Link href="/" className="flex min-w-0 items-center gap-2 text-sm font-semibold text-black sm:text-base">
          <span className="flex h-9 w-9 shrink-0 items-center justify-center sm:h-10 sm:w-10">
            <Image
              className="h-full w-full object-contain"
              src="/brand/today-eat-icon.png"
              alt=""
              width={40}
              height={40}
              priority
              unoptimized
              aria-hidden="true"
            />
          </span>
          <span className="whitespace-nowrap">今天吃什么</span>
        </Link>
        <nav className="flex max-w-full items-center gap-2 overflow-x-auto pb-1 text-sm sm:pb-0" aria-label="主导航">
          {navigation.map((item) => {
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                className={`btn whitespace-nowrap ${active ? "bg-leaf text-white" : "btn-ghost"}`}
                href={item.href}
                aria-current={active ? "page" : undefined}
              >
                {item.label}
              </Link>
            );
          })}
          {user ? (
            <span className="hidden max-w-[180px] truncate text-sm font-medium text-soy sm:inline">
              {user.display_name ?? user.email}
            </span>
          ) : (
            <Link className="btn btn-ghost" href="/auth/login">
              登录
            </Link>
          )}
          {user && (
            <button className="btn btn-ghost" type="button" onClick={() => clearStoredToken().finally(() => window.location.assign("/auth/login"))} title="退出登录">
              <LogOut size={16} />
              退出
            </button>
          )}
          {canSeeAdmin && (
            <Link className={`btn whitespace-nowrap ${pathname === "/admin" ? "bg-leaf text-white" : "btn-primary"}`} href="/admin" aria-current={pathname === "/admin" ? "page" : undefined}>
              <ShieldCheck size={16} />
              管理端
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
