 "use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { getToken } from "../util/auth";

/**
 * 受保护页面通用布局
 *
 * - 统一在客户端检查登录态（Cookie 中是否有 token）
 * - 未登录时跳转到 /login?redirect=当前完整路径（含 query）
 * - 已登录才渲染 children，避免未登录状态下内容闪现
 */
export default function ProtectedLayout({ children }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [checked, setChecked] = useState(false);
  const [allowed, setAllowed] = useState(false);

  useEffect(() => {
    const token = getToken();

    if (!token) {
      // 组装当前完整路径作为 redirect 参数，包含 query
      const search = searchParams?.toString();
      const currentFullPath = search ? `${pathname}?${search}` : pathname;

      router.replace(
        `/login?redirect=${encodeURIComponent(currentFullPath || "/view/home")}`,
      );
      setAllowed(false);
      setChecked(true);
      return;
    }

    setAllowed(true);
    setChecked(true);
  }, [pathname, router, searchParams]);

  // 登录态尚未检查完毕时不渲染内容，避免闪烁
  if (!checked) {
    return null;
  }

  if (!allowed) {
    return null;
  }

  return children;
}

