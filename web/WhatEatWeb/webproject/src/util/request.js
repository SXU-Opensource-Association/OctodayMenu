import axios from "axios";
import { getToken, removeToken } from "./auth";

// axios 实例
const service = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8080", // 后端运行在8080端口
  timeout: 5000,
});

// 请求拦截：自动带上 Token
service.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers = config.headers || {};
      // 后端需要 Authorization: Bearer token 格式
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截：按通用 code 处理
service.interceptors.response.use(
  (response) => {
    const res = response.data;

    // 支持两种成功码：20000（原设计）和 200（当前后端使用）
    const successCodes = [20000, 200];
    if (res && !successCodes.includes(res.code)) {
      // token 相关错误，自动移除本地 token
      if ([50008, 50012, 50014].includes(res.code)) {
        removeToken();
      }
      return Promise.reject(new Error(res.message || "请求出错"));
    }
    return res;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default service;
