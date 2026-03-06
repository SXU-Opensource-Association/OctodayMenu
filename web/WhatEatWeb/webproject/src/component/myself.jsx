"use client";

import { useRouter } from "next/navigation";
import { logout } from "../api/login";
import { removeToken, removeUserInfo } from "../util/auth";

export default () => {
    const router = useRouter();

    const handleLogout = async () => {
        try {
            // 调用后端退出登录接口
            await logout();
        } catch (error) {
            // 即使后端请求失败，也清除本地 token（网络错误等情况）
            console.error("退出登录失败:", error);
        } finally {
            // 无论成功与否，都清除本地存储的 token 和用户信息
            removeToken();
            removeUserInfo();
            // 跳转到登录页
            router.push("/login");
        }
    };

    return (
        <div>
            <h1>个人中心开发中</h1>
            <button onClick={handleLogout}>退出登录</button>
        </div>
    )
}