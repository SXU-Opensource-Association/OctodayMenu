import { Suspense } from "react";

import { AuthForm } from "@/components/auth-form";

export default function RegisterPage() {
  return (
    <Suspense fallback={<div className="auth-loading">正在建立安全连接...</div>}>
      <AuthForm mode="register" />
    </Suspense>
  );
}
