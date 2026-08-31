import type { Metadata } from "next";

import { SiteNav } from "@/components/site-nav";
import "./globals.css";

export const metadata: Metadata = {
  title: "SXU 今天吃什么",
  description: "面向大学生的餐厅、窗口、菜品查询与每日抽签系统"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>
        <SiteNav />
        <main>{children}</main>
      </body>
    </html>
  );
}
