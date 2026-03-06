"use client";

import LoginView from "../../component/Login.jsx";
import { getToken } from "../../util/auth";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect } from "react";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirect = searchParams.get("redirect") || "/view/home";

  // 已登录访问 /login，直接跳回业务页
  useEffect(() => {
    if (getToken()) {
      router.replace(redirect);
    }
  }, [redirect, router]);

  return (
    <LoginView
      onLoginSuccess={() => {
        router.replace(redirect);
      }}
    />
  );
}