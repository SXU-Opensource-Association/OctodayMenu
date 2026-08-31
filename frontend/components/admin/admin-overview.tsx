import { AlertTriangle, Building2, ImageOff, Soup, Store, Tags } from "lucide-react";

import type { AdminMetrics } from "@/lib/admin-metrics";


export function AdminOverview({ metrics, lastUpdated }: { metrics: AdminMetrics; lastUpdated: Date | null }) {
  const cards = [
    { label: "可用地点", value: metrics.activeAreaCount, icon: Building2 },
    { label: "可用店铺", value: metrics.activeVendorCount, icon: Store },
    { label: "可抽签菜品", value: metrics.drawableDishCount, icon: Soup },
    { label: "空店铺", value: metrics.emptyVendorCount, icon: Tags },
    { label: "缺少店铺图片", value: metrics.missingVendorImageCount, icon: ImageOff },
    { label: "缺少菜品价格", value: metrics.missingDishPriceCount, icon: AlertTriangle }
  ];

  return (
    <section className="space-y-4">
      {metrics.drawableDishCount === 0 && (
        <div className="flex items-start gap-3 rounded-lg border border-chili/25 bg-chili/5 p-4 text-chili" role="alert">
          <AlertTriangle className="mt-0.5 flex-none" size={20} />
          <div>
            <h2 className="font-semibold">发布阻断：当前没有可抽签菜品</h2>
            <p className="mt-1 text-sm">请先添加启用店铺和供应中的菜品，再开放每日抽签。</p>
          </div>
        </div>
      )}
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {cards.map(({ label, value, icon: Icon }) => (
          <article key={label} className="rounded-lg border border-ink/10 bg-white p-4 shadow-soft">
            <div className="flex items-center justify-between gap-3">
              <span className="text-sm text-soy">{label}</span>
              <Icon className="text-leaf" size={18} />
            </div>
            <p className="mt-2 text-3xl font-semibold text-ink">{value}</p>
          </article>
        ))}
      </div>
      <p className="text-xs text-soy">
        {lastUpdated ? `最后更新：${lastUpdated.toLocaleString("zh-CN")}` : "尚未完成数据刷新"}
      </p>
    </section>
  );
}
