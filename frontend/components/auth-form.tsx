"use client";

import { FormEvent, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { ArrowRight, AtSign, Eye, EyeOff, KeyRound, MailCheck, ShieldCheck, UserRound } from "lucide-react";

import { ApiError, api, setStoredToken } from "@/lib/api";

type Mode = "login" | "register";

export function AuthForm({ mode }: { mode: Mode }) {
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [displayName, setDisplayName] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [verificationHint, setVerificationHint] = useState("");
  const [adminMfaRequired, setAdminMfaRequired] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [sendingCode, setSendingCode] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (mode === "register" && password !== confirmPassword) {
      setError("两次输入的密码不一致");
      return;
    }
    setLoading(true);
    try {
      const result =
        mode === "login"
          ? await api.login({ email, password, verification_code: adminMfaRequired ? verificationCode : undefined })
          : await api.register({
              email,
              password,
              display_name: displayName || undefined,
              verification_code: verificationCode
            });
      if ("mfa_required" in result) {
        setAdminMfaRequired(true);
        setVerificationHint(result.dev_code ? `测试环境管理员验证码：${result.dev_code}` : result.message);
        return;
      }
      setStoredToken(result.access_token);
      const next = safeNextPath(searchParams.get("next"));
      window.location.assign(next || (result.user.role === "USER" ? "/" : "/admin"));
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "提交失败");
    } finally {
      setLoading(false);
    }
  }

  const isLogin = mode === "login";

  async function sendVerificationCode() {
    setSendingCode(true);
    setError("");
    setVerificationHint("");
    try {
      const result = await api.sendEmailVerification({ email });
      setVerificationHint(result.dev_code ? `开发环境验证码：${result.dev_code}` : "验证码已发送，请查看邮箱。");
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "验证码发送失败");
    } finally {
      setSendingCode(false);
    }
  }

  return (
    <section className="auth-shell">
      <div className="auth-ambient-code auth-ambient-code-left" aria-hidden="true">
        AUTH_NODE_07 · 10101101 · SECURE
      </div>
      <div className="auth-ambient-code auth-ambient-code-right" aria-hidden="true">
        OPEN_SOURCE · ENCRYPTED · SXU_OSA
      </div>

      <form
        onSubmit={onSubmit}
        className="auth-card"
        aria-busy={loading}
        autoComplete={isLogin ? "off" : "on"}
      >
        <header className="auth-brand">
          <div className="auth-brand-marks">
            <span className="auth-brand-logo">
              <Image
                src="/brand/sxu-open-source-association.png"
                alt="山西大学开源软件协会社徽"
                width={96}
                height={78}
                priority
              />
            </span>
            <span className="auth-brand-connector" aria-hidden="true" />
            <span className="auth-product-logo">
              <Image
                src="/brand/today-eat-icon.png"
                alt="今天吃什么图标"
                width={72}
                height={72}
                priority
                unoptimized
              />
            </span>
          </div>
          <p className="auth-brand-code">OPEN SOURCE · AUTH GATEWAY</p>
          <h1>
            SXU<span>·</span>今天吃什么
          </h1>
          <p className="auth-brand-copy">{isLogin ? "登录\"今天吃什么\"账号" : "创建\"今天吃什么\"用户账号"}</p>
        </header>

        <label className="auth-field-group">
          <span className="auth-field-label">
            邮箱 <code>IDENTITY</code>
          </span>
          <span className="auth-input-wrap">
            <AtSign size={17} aria-hidden="true" />
            <input
              className="auth-input"
              type="email"
              value={email}
              onChange={(event) => {
                setEmail(event.target.value);
                if (isLogin && adminMfaRequired) {
                  setAdminMfaRequired(false);
                  setVerificationCode("");
                  setVerificationHint("");
                }
              }}
              placeholder="请输入邮箱地址"
              autoComplete={isLogin ? "off" : "email"}
              required
            />
          </span>
        </label>

        <label className="auth-field-group">
          <span className="auth-field-label">
            密码 <code>ENCRYPTED</code>
          </span>
          <span className="auth-input-wrap">
            <KeyRound size={17} aria-hidden="true" />
            <input
              className="auth-input"
              type={showPassword ? "text" : "password"}
              minLength={8}
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
                if (isLogin && adminMfaRequired) {
                  setAdminMfaRequired(false);
                  setVerificationCode("");
                  setVerificationHint("");
                }
              }}
              placeholder="至少 8 位密码"
              autoComplete={isLogin ? "off" : "new-password"}
              required
            />
            <button
              className="auth-password-toggle"
              type="button"
              onClick={() => setShowPassword((current) => !current)}
              aria-label={showPassword ? "隐藏密码" : "显示密码"}
              aria-pressed={showPassword}
            >
              {showPassword ? <EyeOff size={17} aria-hidden="true" /> : <Eye size={17} aria-hidden="true" />}
            </button>
          </span>
        </label>

        {!isLogin && (
          <>
            <label className="auth-field-group">
              <span className="auth-field-label">
                确认密码 <code>CONFIRM</code>
              </span>
              <span className="auth-input-wrap">
                <KeyRound size={17} aria-hidden="true" />
                <input
                  className="auth-input"
                  type={showConfirmPassword ? "text" : "password"}
                  minLength={8}
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  placeholder="请再次输入密码"
                  autoComplete="new-password"
                  required
                />
                <button
                  className="auth-password-toggle"
                  type="button"
                  onClick={() => setShowConfirmPassword((current) => !current)}
                  aria-label={showConfirmPassword ? "隐藏确认密码" : "显示确认密码"}
                  aria-pressed={showConfirmPassword}
                >
                  {showConfirmPassword ? <EyeOff size={17} aria-hidden="true" /> : <Eye size={17} aria-hidden="true" />}
                </button>
              </span>
            </label>

            <label className="auth-field-group">
              <span className="auth-field-label">
                昵称 <code>OPTIONAL</code>
              </span>
              <span className="auth-input-wrap">
                <UserRound size={17} aria-hidden="true" />
                <input
                  className="auth-input"
                  value={displayName}
                  onChange={(event) => setDisplayName(event.target.value)}
                  placeholder="怎么称呼你"
                  autoComplete="nickname"
                />
              </span>
            </label>

            <div className="auth-field-group">
              <span className="auth-field-label">
                邮箱验证码 <code>VERIFY</code>
              </span>
              <div className="auth-verification-row">
                <span className="auth-input-wrap">
                  <MailCheck size={17} aria-hidden="true" />
                  <input
                    className="auth-input"
                    inputMode="numeric"
                    maxLength={6}
                    placeholder="6 位验证码"
                    value={verificationCode}
                    onChange={(event) => setVerificationCode(event.target.value.replace(/\D/g, "").slice(0, 6))}
                    required
                  />
                </span>
                <button
                  className="auth-secondary-button"
                  type="button"
                  onClick={sendVerificationCode}
                  disabled={sendingCode || !email}
                >
                  {sendingCode ? "发送中" : "发送验证码"}
                </button>
              </div>
              {verificationHint && <p className="auth-verification-hint">{verificationHint}</p>}
            </div>
          </>
        )}

        {isLogin && adminMfaRequired && (
          <div className="auth-field-group">
            <span className="auth-field-label">
              管理员验证码 <code>MFA</code>
            </span>
            <span className="auth-input-wrap">
              <MailCheck size={17} aria-hidden="true" />
              <input
                className="auth-input"
                inputMode="numeric"
                maxLength={6}
                placeholder="邮箱中的 6 位验证码"
                value={verificationCode}
                onChange={(event) => setVerificationCode(event.target.value.replace(/\D/g, "").slice(0, 6))}
                required
              />
            </span>
            {verificationHint && <p className="auth-verification-hint">{verificationHint}</p>}
          </div>
        )}

        {error && (
          <p className="auth-error" role="alert">
            {error}
          </p>
        )}

        <button className="auth-submit-button" type="submit" disabled={loading}>
          {isLogin ? <ShieldCheck size={17} aria-hidden="true" /> : <UserRound size={17} aria-hidden="true" />}
          {loading ? "提交中..." : isLogin ? "安全登录" : "创建账号"}
          {!loading && <ArrowRight size={17} aria-hidden="true" />}
        </button>

        <p className="auth-switch">
          {isLogin ? "还没有账号？" : "已有账号？"}
          <Link
            href={{
              pathname: isLogin ? "/auth/register" : "/auth/login",
              query: searchParams.get("next") ? { next: searchParams.get("next") } : undefined
            }}
          >
            {isLogin ? "去注册" : "去登录"}
          </Link>
        </p>
      </form>
    </section>
  );
}

function safeNextPath(value: string | null) {
  if (!value || !value.startsWith("/") || value.startsWith("//")) return null;
  return value;
}
