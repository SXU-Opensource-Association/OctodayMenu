"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getToken } from "../util/auth";

export default function RootPage() {
  const router = useRouter();

  useEffect(() => {
    // 如果已登录，重定向到首页；否则重定向到登录页
    if (getToken()) {
      router.replace("/view/home");
    } else {
      router.replace("/login");
    }
  }, [router]);

  // 重定向期间显示空白或加载状态
  return null;
}
