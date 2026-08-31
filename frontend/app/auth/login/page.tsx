import { Suspense } from "react";

import { AuthForm } from "@/components/auth-form";

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="auth-loading">正在建立安全连接...</div>}>
      <AuthForm mode="login" />
    </Suspense>
  );
}
