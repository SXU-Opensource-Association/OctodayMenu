"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CalendarCheck, Dices, LockKeyhole, Megaphone, SlidersHorizontal, Store } from "lucide-react";

import { ApiError, api } from "@/lib/api";
import type { Announcement, DailyDraw } from "@/lib/types";

export function UserDashboard() {
  const [draw, setDraw] = useState<DailyDraw | null>(null);
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api
      .todayDraw()
      .then(setDraw)
      .catch(() => null);
    api.announcements().then(setAnnouncements).catch(() => null);
  }, []);

  async function checkInAndDraw() {
    setLoading(true);
    setMessage("");
    try {
      setDraw(await api.drawToday());
    } catch (caught) {
      if (caught instanceof ApiError && caught.status === 401) {
        setMessage("请先登录，再完成今日签到和随机抽签。");
      } else {
        setMessage(caught instanceof ApiError ? caught.message : "签到失败");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto min-h-[calc(100vh-66px)] max-w-6xl px-4 py-8">
      {announcements.length > 0 && (
        <section className="mb-6 space-y-2" aria-label="站点公告">
          {announcements.map((announcement) => (
            <article key={announcement.id} className={`rounded-lg border px-4 py-3 ${announcement.level === "IMPORTANT" ? "border-chili/25 bg-chili/5" : "border-leaf/20 bg-mint/45"}`}>
              <div className="flex items-start gap-3">
                <Megaphone className={announcement.level === "IMPORTANT" ? "mt-0.5 shrink-0 text-chili" : "mt-0.5 shrink-0 text-leaf"} size={19} />
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="font-semibold text-ink">{announcement.title}</h2>
                    {announcement.level === "IMPORTANT" && <span className="rounded-full bg-chili/10 px-2 py-0.5 text-xs text-chili">重要</span>}
                  </div>
                  <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-soy">{announcement.content}</p>
                  <p className="mt-1 text-xs text-soy">发布于 {new Date(announcement.published_at).toLocaleString("zh-CN")}</p>
                </div>
              </div>
            </article>
          ))}
        </section>
      )}

      <div className="grid items-center gap-8 py-2 lg:grid-cols-[1fr_420px]">
      <section>
        <p className="mb-3 text-sm font-medium text-leaf">SXUWhatEat</p>
        <h1 className="max-w-3xl text-4xl font-semibold leading-tight text-ink md:text-5xl">
          今天吃什么，从一次签到开始
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-7 text-soy">
          首页只保留核心入口。想看餐厅、楼层、窗口和菜品，进入食堂窗口；没想法时直接随机抽取今天的饭。
        </p>

        <div className="mt-8 grid gap-3 sm:grid-cols-3">
          <Link href="/canteens" className="panel block hover:border-leaf/40">
            <div className="mb-3 flex items-center justify-between">
              <Store className="text-leaf" size={24} />
              <span className="inline-flex items-center gap-1 text-xs text-soy"><LockKeyhole size={12} />登录后使用</span>
            </div>
            <h2 className="font-semibold text-ink">食堂窗口</h2>
            <p className="mt-1 text-sm text-soy">逐级查看餐厅、楼层、窗口和菜品。</p>
          </Link>
          <Link href="/draw" className="panel block hover:border-leaf/40">
            <div className="mb-3 flex items-center justify-between">
              <Dices className="text-chili" size={24} />
              <span className="inline-flex items-center gap-1 text-xs text-soy"><LockKeyhole size={12} />登录后使用</span>
            </div>
            <h2 className="font-semibold text-ink">每日随机</h2>
            <p className="mt-1 text-sm text-soy">不设筛选，随机抽取可用菜品。</p>
          </Link>
          <Link href="/personalize" className="panel block hover:border-leaf/40">
            <div className="mb-3 flex items-center justify-between">
              <SlidersHorizontal className="text-leaf" size={24} />
              <span className="inline-flex items-center gap-1 text-xs text-soy"><LockKeyhole size={12} />登录后使用</span>
            </div>
            <h2 className="font-semibold text-ink">个性筛选</h2>
            <p className="mt-1 text-sm text-soy">按口味、价格、热度和实景图筛店铺。</p>
          </Link>
        </div>
      </section>

      <aside className="rounded-lg border border-leaf/15 bg-rice p-5 shadow-soft">
        <div className="mb-4 flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-md bg-white text-leaf">
            <CalendarCheck size={24} />
          </span>
          <div>
            <h2 className="text-xl font-semibold text-ink">今日签到</h2>
            <p className="text-sm text-soy">签到会随机生成今天的饭菜结果</p>
          </div>
        </div>

        <button className="btn btn-primary w-full" onClick={checkInAndDraw} disabled={loading}>
          <Dices size={16} />
          {loading ? "签到中" : draw ? "查看今日结果" : "签到并随机抽取"}
        </button>

        {message && <p className="mt-3 rounded-md bg-chili/10 px-3 py-2 text-sm text-chili">{message}</p>}
        {draw && (
          <div className="mt-4 rounded-lg border border-leaf/20 bg-white p-4">
            <p className="text-sm text-soy">{draw.food_area.name} · {draw.vendor.name}</p>
            <h3 className="mt-1 text-2xl font-semibold text-ink">{draw.dish.name}</h3>
            <p className="mt-2 text-sm text-soy">{draw.dish.description ?? "这就是今天的随机结果。"}</p>
          </div>
        )}
      </aside>
      </div>
    </div>
  );
}
