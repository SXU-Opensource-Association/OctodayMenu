"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Flame, MessageCircle, ThumbsUp } from "lucide-react";

import { ApiError, api } from "@/lib/api";
import type { Restaurant } from "@/lib/types";

export function RestaurantDetail({ restaurantId }: { restaurantId: number }) {
  const [restaurant, setRestaurant] = useState<Restaurant | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .restaurant(restaurantId)
      .then(setRestaurant)
      .catch((caught) => setError(caught instanceof ApiError ? caught.message : "加载失败"));
  }, [restaurantId]);

  if (error) return <div className="mx-auto max-w-5xl px-4 py-10 text-chili">{error}</div>;
  if (!restaurant) return <div className="mx-auto max-w-5xl px-4 py-10 text-soy">正在加载餐厅详情...</div>;

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <Link className="mb-4 inline-flex items-center gap-2 text-sm font-medium text-leaf" href="/">
        <ArrowLeft size={16} />
        返回餐厅列表
      </Link>
      <section className="mb-6">
        <p className="text-sm font-medium text-leaf">{restaurant.address ?? "校内餐厅"}</p>
        <h1 className="mt-2 text-4xl font-semibold text-ink">{restaurant.name}</h1>
        <p className="mt-3 max-w-2xl text-soy">{restaurant.description ?? "这里还没有餐厅简介。"}</p>
      </section>

      <div className="space-y-5">
        {restaurant.floors.map((floor) => (
          <section key={floor.id} className="panel">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-ink">{floor.name}</h2>
                <p className="text-sm text-soy">{floor.description ?? `第 ${floor.level} 层`}</p>
              </div>
              <span className="rounded-md bg-mint px-2 py-1 text-sm text-leaf">{floor.stalls.length} 个窗口</span>
            </div>
            <div className="grid gap-4 lg:grid-cols-2">
              {floor.stalls.map((stall) => (
                <article key={stall.id} className="rounded-lg border border-ink/10 bg-white p-4">
                  <div className="mb-3 flex items-start justify-between gap-3">
                    <div>
                      <h3 className="text-lg font-semibold text-ink">{stall.name}</h3>
                      <p className="mt-1 text-sm text-soy">{stall.description ?? stall.location_hint ?? "暂无窗口简介"}</p>
                    </div>
                    <div className="flex gap-2 text-xs text-soy">
                      <span className="inline-flex items-center gap-1">
                        <ThumbsUp size={13} />
                        {stall.like_count}
                      </span>
                      <span className="inline-flex items-center gap-1">
                        <MessageCircle size={13} />
                        {stall.comment_count}
                      </span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    {stall.dishes.map((dish) => (
                      <div key={dish.id} className="rounded-md bg-mint/40 p-3">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <h4 className="font-medium text-ink">{dish.name}</h4>
                            <p className="mt-1 text-sm text-soy">{dish.description ?? "暂无菜品简介"}</p>
                          </div>
                          <span className="whitespace-nowrap text-sm font-semibold text-chili">
                            {dish.price ? `¥${dish.price}` : "时价"}
                          </span>
                        </div>
                        <div className="mt-2 flex flex-wrap gap-2">
                          {dish.tags.map((tag) => (
                            <span key={tag.id} className="inline-flex items-center gap-1 rounded-md bg-white px-2 py-1 text-xs text-soy">
                              {tag.category === "taste" && <Flame size={12} />}
                              {tag.name}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
