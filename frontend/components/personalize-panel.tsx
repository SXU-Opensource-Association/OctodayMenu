"use client";

import { useEffect, useMemo, useState } from "react";
import { Filter, Heart, Image, MapPin, RotateCcw, Search, Store } from "lucide-react";

import { ApiError, api, toMediaUrl } from "@/lib/api";
import { filterVendorResults, parsePriceRange, type VendorMatch } from "@/lib/personalize-rules";
import type { AreaType, FoodArea, FoodAreaSummary, Tag } from "@/lib/types";

const AREA_LABEL: Record<AreaType | "ALL", string> = {
  ALL: "全部地点",
  CANTEEN: "校内餐厅",
  SNACK_STREET: "小吃街",
  CUSTOM_AREA: "自定义方位"
};

export function PersonalizePanel() {
  const [areas, setAreas] = useState<FoodArea[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [areaType, setAreaType] = useState<AreaType | "ALL">("ALL");
  const [keyword, setKeyword] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [tagIds, setTagIds] = useState<number[]>([]);
  const [highLike, setHighLike] = useState(false);
  const [hasImage, setHasImage] = useState(false);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [summaries, tagData] = await Promise.all([api.foodAreas(), api.tags()]);
        const details = await Promise.all(summaries.map((area: FoodAreaSummary) => api.foodArea(area.id)));
        setAreas(details);
        setTags(tagData);
      } catch (caught) {
        setMessage(caught instanceof ApiError ? caught.message : "筛选数据加载失败");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const priceRange = useMemo(() => parsePriceRange(minPrice, maxPrice), [minPrice, maxPrice]);
  const results = useMemo(
    () =>
      filterVendorResults(areas, {
        areaType,
        keyword,
        minPrice,
        maxPrice,
        tagIds,
        highLike,
        hasImage
      }),
    [areas, areaType, keyword, minPrice, maxPrice, tagIds, highLike, hasImage]
  );

  function toggleTag(tagId: number) {
    setTagIds((current) => (current.includes(tagId) ? current.filter((id) => id !== tagId) : [...current, tagId]));
  }

  function clearFilters() {
    setAreaType("ALL");
    setKeyword("");
    setMinPrice("");
    setMaxPrice("");
    setTagIds([]);
    setHighLike(false);
    setHasImage(false);
  }

  if (loading) return <div className="mx-auto max-w-7xl px-4 py-10 text-soy">正在加载个性化筛选...</div>;

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:py-8">
      <section className="mb-5 rounded-lg border border-ink/10 bg-white/90 p-4 shadow-soft">
        <p className="text-sm font-medium text-leaf">个性化筛选</p>
        <h1 className="mt-1 text-2xl font-semibold text-ink sm:text-3xl">按当前想法筛出更适合去的店铺</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-soy">
          使用严格筛选：店铺或菜品必须满足当前条件才会出现，结果会说明具体匹配依据。
        </p>
      </section>
      {message && <p className="mb-4 rounded-md bg-chili/10 px-3 py-2 text-sm text-chili">{message}</p>}
      <div className="grid gap-4 lg:grid-cols-[320px_1fr]">
        <aside className="panel h-fit">
          <div className="mb-3 flex items-center justify-between gap-2">
            <span className="flex items-center gap-2">
              <Filter size={18} className="text-leaf" />
              <h2 className="font-semibold text-ink">筛选条件</h2>
            </span>
            <button type="button" className="inline-flex items-center gap-1 text-xs font-medium text-leaf" onClick={clearFilters}>
              <RotateCcw size={13} />
              清空全部
            </button>
          </div>
          <select className="field mb-3" value={areaType} onChange={(event) => setAreaType(event.target.value as AreaType | "ALL")}>
            {(["ALL", "CANTEEN", "SNACK_STREET", "CUSTOM_AREA"] as Array<AreaType | "ALL">).map((type) => <option key={type} value={type}>{AREA_LABEL[type]}</option>)}
          </select>
          <label className="relative mb-3 block">
            <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-soy" size={16} />
            <input className="field pl-9" value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="关键词，如 面、咖啡、清淡" />
          </label>
          <div className="mb-3 grid grid-cols-2 gap-2">
            <input className="field" value={minPrice} onChange={(event) => setMinPrice(event.target.value)} placeholder="最低价" inputMode="decimal" aria-invalid={Boolean(priceRange.error)} />
            <input className="field" value={maxPrice} onChange={(event) => setMaxPrice(event.target.value)} placeholder="最高价" inputMode="decimal" aria-invalid={Boolean(priceRange.error)} />
          </div>
          {priceRange.error && <p className="mb-3 text-xs font-medium text-chili">{priceRange.error}</p>}
          <div className="mb-3 flex flex-wrap gap-2">
            {tags.map((tag) => (
              <button key={tag.id} type="button" className={`rounded-md border px-2 py-1 text-xs ${tagIds.includes(tag.id) ? "border-leaf bg-mint text-leaf" : "border-ink/10 bg-white text-soy"}`} onClick={() => toggleTag(tag.id)}>
                {tag.name}
              </button>
            ))}
          </div>
          <label className="mb-2 flex items-center gap-2 text-sm text-ink">
            <input type="checkbox" checked={highLike} onChange={(event) => setHighLike(event.target.checked)} />
            只看有点赞的店铺
          </label>
          <label className="flex items-center gap-2 text-sm text-ink">
            <input type="checkbox" checked={hasImage} onChange={(event) => setHasImage(event.target.checked)} />
            只看有实景图的店铺
          </label>
        </aside>
        <main className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-ink">匹配结果</h2>
            <span className="text-sm text-soy">{results.length} 个店铺</span>
          </div>
          {priceRange.error ? (
            <InvalidFilterState />
          ) : results.length === 0 ? (
            <EmptyState />
          ) : (
            results.map((item) => <ResultCard key={item.vendor.id} item={item} />)
          )}
        </main>
      </div>
    </div>
  );
}

function ResultCard({ item }: { item: VendorMatch }) {
  const imageUrl = toMediaUrl(item.vendor.image_url);
  return (
    <article className="overflow-hidden rounded-lg border border-ink/10 bg-white shadow-soft">
      <div className="grid gap-0 md:grid-cols-[220px_1fr]">
        {imageUrl ? <img src={imageUrl} alt={item.vendor.name} className="h-44 w-full object-cover md:h-full" /> : <div className="flex h-44 items-center justify-center bg-mint text-leaf md:h-full"><Store size={36} /></div>}
        <div className="p-4">
          <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-start">
            <div>
              <p className="text-xs font-medium text-leaf">{AREA_LABEL[item.area.area_type]} · {item.area.name}{item.sectionName ? ` · ${item.sectionName}` : ""}</p>
              <h3 className="mt-1 text-xl font-semibold text-ink">{item.vendor.name}</h3>
              <p className="mt-1 flex items-center gap-1 text-sm text-soy"><MapPin size={14} />{item.vendor.location_hint ?? item.area.location ?? "校内外"}</p>
            </div>
            <div className="flex gap-2 text-xs text-soy">
              <span className="inline-flex items-center gap-1 rounded-md bg-mint px-2 py-1 text-leaf"><Heart size={13} />{item.vendor.like_count}</span>
              {item.vendor.image_url && <span className="inline-flex items-center gap-1 rounded-md bg-rice px-2 py-1"><Image size={13} />实景</span>}
            </div>
          </div>
          <p className="mt-3 text-sm leading-6 text-soy">{item.vendor.description ?? "暂无店铺简介"}</p>
          {item.reasons.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {item.reasons.map((reason) => (
                <span key={reason} className="rounded-md bg-mint px-2 py-1 text-xs font-medium text-leaf">
                  {reason}
                </span>
              ))}
            </div>
          )}
          <div className="mt-3 divide-y divide-ink/5 rounded-md border border-ink/10">
            {item.matchedDishes.slice(0, 5).map((dish) => (
              <div key={dish.id} className="flex items-center justify-between gap-3 px-3 py-2 text-sm">
                <span className="min-w-0 truncate text-ink">{dish.name}</span>
                <span className="flex-none font-semibold text-chili">{dish.price ? `¥${dish.price}` : "时价"}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </article>
  );
}

function EmptyState() {
  return (
    <div className="flex min-h-[260px] flex-col items-center justify-center rounded-lg bg-mint/45 p-6 text-center">
      <Store className="text-leaf" size={34} />
      <h2 className="mt-3 font-semibold text-ink">暂无匹配结果</h2>
      <p className="mt-1 max-w-md text-sm leading-6 text-soy">放宽价格、标签或关键词后再试试。</p>
    </div>
  );
}

function InvalidFilterState() {
  return (
    <div className="flex min-h-[260px] flex-col items-center justify-center rounded-lg bg-chili/5 p-6 text-center">
      <Filter className="text-chili" size={34} />
      <h2 className="mt-3 font-semibold text-ink">筛选条件有误</h2>
      <p className="mt-1 max-w-md text-sm leading-6 text-soy">修正价格区间后再查看匹配结果。</p>
    </div>
  );
}
