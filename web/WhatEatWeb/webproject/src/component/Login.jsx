import { useState } from "react";
import { setToken, setUserInfo } from "../util/auth";
import { login, register } from "../api/login";

export default function Login({ onLoginSuccess }) {
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // 注册模式下校验必填字段
    if (mode === "register") {
      if (!phone.trim()) {
        setError("请输入联系电话");
        return;
      }
    }

    setLoading(true);
    try {
      let res;
      if (mode === "login") {
        // 登录：仅 username / password
        res = await login({
          username,
          password,
        });
      } else {
        // 注册：username / password / phone(必填) / email(选填)
        res = await register({
          username,
          password,
          phone,
          email: email || undefined,
        });
      }

      // 兼容两种常见返回：{ code, data: { token } } 或 { code, token }
      const token = res?.data?.token || res?.token;

      // 注册：如果接口不返回 token，则提示成功并切回登录
      if (mode === "register" && !token) {
        setMode("login");
        setError("注册成功，请登录");
        setLoading(false);
        return;
      }

      if (!token) throw new Error("接口返回数据不包含 token");

      // 写入 token
      setToken(token);

      // 从返回中抽出用户信息并做"全局"存储
      const userData = res?.data || res;
      setUserInfo(userData);

      // 登录成功，触发跳转回调
      // 使用 setTimeout 确保状态更新完成后再跳转，提升用户体验
      setTimeout(() => {
        onLoginSuccess?.();
      }, 100);
    } catch (err) {
      setError(err.message || "登录失败");
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-glow" />
        <h1 className="login-title">SXU · 开源社团</h1>
        <p className="login-subtitle">蓝紫流光 · 智能推荐你的下一顿</p>

        <div className="login-mode">
          <button
            type="button"
            className={`login-mode-btn ${mode === "login" ? "is-active" : ""}`}
            onClick={() => setMode("login")}
          >
            登录
          </button>
          <button
            type="button"
            className={`login-mode-btn ${mode === "register" ? "is-active" : ""}`}
            onClick={() => setMode("register")}
          >
            注册
          </button>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <label className="login-label">
            <span>用户名</span>
            <input
              className="login-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="请输入学号 / 账号"
            />
          </label>

          <label className="login-label">
            <span>密码</span>
            <input
              type="password"
              className="login-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="请输入密码"
            />
          </label>

          {mode === "register" && (
            <>
              <label className="login-label">
                <span>联系电话（必填）</span>
                <input
                  className="login-input"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="请输入手机号 / 联系电话"
                />
              </label>

              <label className="login-label">
                <span>邮箱（选填）</span>
                <input
                  className="login-input"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="请输入邮箱（可不填）"
                />
              </label>
            </>
          )}

          {error && <div className="login-error">{error}</div>}

          <button className="login-btn" type="submit" disabled={loading}>
            {loading ? "处理中..." : mode === "login" ? "登 录" : "注 册"}
          </button>
        </form>
      </div>
    </div>
  );
}
