"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Dices, LogIn, RefreshCw } from "lucide-react";

import { ApiError, api } from "@/lib/api";
import type { DailyDraw } from "@/lib/types";

export function DrawPanel() {
  const [draw, setDraw] = useState<DailyDraw | null>(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api
      .todayDraw()
      .then(setDraw)
      .catch(() => null);
  }, []);

  async function submitDraw() {
    setLoading(true);
    setMessage("");
    try {
      setDraw(await api.drawToday());
    } catch (caught) {
      if (caught instanceof ApiError && caught.status === 401) {
        setMessage("请先登录，再抽取今天的饭。");
      } else {
        setMessage(caught instanceof ApiError ? caught.message : "抽签失败");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto grid min-h-[calc(100vh-66px)] max-w-6xl items-center gap-8 px-4 py-10 lg:grid-cols-[420px_1fr]">
      <section className="panel">
        <div className="mb-5 flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-md bg-rice text-chili">
            <Dices size={24} />
          </span>
          <div>
            <h1 className="text-2xl font-semibold text-ink">每日抽签</h1>
            <p className="text-sm text-soy">今天的结果会固定保存</p>
          </div>
        </div>

        <div className="mb-4 rounded-md bg-mint/45 p-3 text-sm leading-6 text-soy">
          系统会从全部可用菜品中随机抽取。每天第一次抽签后，当天再次进入会显示同一个结果。
        </div>

        <button className="btn btn-primary w-full" onClick={submitDraw} disabled={loading}>
          <RefreshCw size={16} />
          {loading ? "抽签中" : "抽今天吃什么"}
        </button>
        {message && (
          <div className="mt-4 rounded-md bg-chili/10 p-3 text-sm text-chili">
            {message}
            {message.includes("登录") && (
              <Link className="ml-2 inline-flex items-center gap-1 font-medium text-leaf" href="/auth/login">
                <LogIn size={14} />
                去登录
              </Link>
            )}
          </div>
        )}
      </section>

      <section className="rounded-lg border border-leaf/15 bg-rice p-8 shadow-soft">
        {draw ? (
          <>
            <p className="text-sm font-medium text-leaf">{draw.draw_date} · {draw.food_area?.name ?? draw.restaurant.name}</p>
            <h2 className="mt-3 text-4xl font-semibold leading-tight text-ink">{draw.dish.name}</h2>
            <p className="mt-4 max-w-xl text-soy">{draw.dish.description ?? "这就是今天的答案。去店里看看现做的味道。"}</p>
            <div className="mt-5 flex flex-wrap gap-2">
              {draw.section && <span className="rounded-md bg-white px-3 py-2 text-sm text-soy">{draw.section.name}</span>}
              <span className="rounded-md bg-white px-3 py-2 text-sm text-soy">{draw.vendor?.name ?? draw.stall.name}</span>
              {draw.dish.tags.map((tag) => (
                <span key={tag.id} className="rounded-md bg-white px-3 py-2 text-sm text-soy">
                  {tag.name}
                </span>
              ))}
            </div>
          </>
        ) : (
          <>
            <p className="text-sm font-medium text-leaf">还没有结果</p>
            <h2 className="mt-3 text-4xl font-semibold leading-tight text-ink">今天随机交给食堂</h2>
            <p className="mt-4 max-w-xl text-soy">不需要筛选餐厅、楼层或口味，系统会直接从全部可用菜品里抽取。</p>
          </>
        )}
      </section>
    </div>
  );
}
