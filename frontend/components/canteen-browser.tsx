"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { Building2, Camera, Heart, ImagePlus, MapPin, MessageCircle, Search, Send, Store, X } from "lucide-react";

import { ApiError, api, toMediaUrl } from "@/lib/api";
import { compressCommentImage } from "@/lib/image-compression";
import type { AreaType, Comment, Dish, FoodArea, FoodAreaSummary, FoodSection, FoodVendor } from "@/lib/types";

const AREA_LABEL: Record<AreaType, string> = {
  CANTEEN: "校内餐厅",
  SNACK_STREET: "小吃街",
  CUSTOM_AREA: "自定义方位"
};

export function CanteenBrowser() {
  const [areas, setAreas] = useState<FoodAreaSummary[]>([]);
  const [selectedType, setSelectedType] = useState<AreaType>("CANTEEN");
  const [selectedAreaId, setSelectedAreaId] = useState<number | null>(null);
  const [areaDetail, setAreaDetail] = useState<FoodArea | null>(null);
  const [selectedSectionId, setSelectedSectionId] = useState<number | null>(null);
  const [selectedVendorId, setSelectedVendorId] = useState<number | null>(null);
  const [query, setQuery] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [vendorLikePending, setVendorLikePending] = useState(false);

  useEffect(() => {
    api
      .foodAreas()
      .then((items) => {
        setAreas(items);
        setSelectedAreaId(items[0]?.id ?? null);
      })
      .catch((caught) => setMessage(caught instanceof ApiError ? caught.message : "就餐地点加载失败"))
      .finally(() => setLoading(false));
  }, []);

  const filteredAreas = useMemo(() => {
    return areas.filter((area) => area.area_type === selectedType);
  }, [areas, selectedType]);

  useEffect(() => {
    if (!filteredAreas.length) {
      setSelectedAreaId(null);
      return;
    }
    if (!filteredAreas.some((area) => area.id === selectedAreaId)) {
      setSelectedAreaId(filteredAreas[0].id);
    }
  }, [filteredAreas, selectedAreaId]);

  useEffect(() => {
    if (!selectedAreaId) {
      setAreaDetail(null);
      setSelectedSectionId(null);
      setSelectedVendorId(null);
      return;
    }

    let active = true;
    setDetailLoading(true);
    setMessage("");
    api
      .foodArea(selectedAreaId)
      .then((detail) => {
        if (!active) return;
        const firstSection = detail.sections[0] ?? null;
        const firstVendors = detail.area_type === "CANTEEN" ? firstSection?.vendors ?? [] : detail.vendors;
        setAreaDetail(detail);
        setSelectedSectionId(firstSection?.id ?? null);
        setSelectedVendorId(firstVendors[0]?.id ?? null);
      })
      .catch((caught) => {
        if (!active) return;
        setAreaDetail(null);
        setMessage(caught instanceof ApiError ? caught.message : "地点详情加载失败");
      })
      .finally(() => {
        if (active) setDetailLoading(false);
      });
    return () => {
      active = false;
    };
  }, [selectedAreaId]);

  const selectedArea = areas.find((area) => area.id === selectedAreaId) ?? null;
  const selectedSection = areaDetail?.sections.find((section) => section.id === selectedSectionId) ?? null;
  const sourceVendors = areaDetail?.area_type === "CANTEEN" ? selectedSection?.vendors ?? [] : areaDetail?.vendors ?? [];
  const normalizedQuery = normalize(query);
  const filteredVendors = useMemo(() => {
    if (!normalizedQuery) return sourceVendors;
    return sourceVendors.filter((vendor) => vendorMatchesQuery(vendor, normalizedQuery));
  }, [sourceVendors, normalizedQuery]);
  const activeVendor = filteredVendors.find((vendor) => vendor.id === selectedVendorId) ?? filteredVendors[0] ?? null;
  const activeDishes = useMemo(() => {
    if (!activeVendor) return [];
    if (!normalizedQuery || vendorOwnFieldsMatchQuery(activeVendor, normalizedQuery)) return activeVendor.dishes;
    return activeVendor.dishes.filter((dish) => dishMatchesQuery(dish, normalizedQuery));
  }, [activeVendor, normalizedQuery]);

  function updateVendor(vendorId: number, updater: (vendor: FoodVendor) => FoodVendor) {
    setAreaDetail((current) => {
      if (!current) return current;
      const updateList = (vendors: FoodVendor[]) => vendors.map((vendor) => (vendor.id === vendorId ? updater(vendor) : vendor));
      return {
        ...current,
        vendors: updateList(current.vendors ?? []),
        sections: (current.sections ?? []).map((section) => ({
          ...section,
          vendors: updateList(section.vendors ?? []),
          stalls: updateList(section.stalls ?? section.vendors ?? [])
        })),
        floors: (current.floors ?? []).map((section) => ({
          ...section,
          vendors: updateList(section.vendors ?? []),
          stalls: updateList(section.stalls ?? section.vendors ?? [])
        }))
      };
    });
  }

  async function toggleVendorLike() {
    if (!activeVendor || vendorLikePending) return;
    setVendorLikePending(true);
    try {
      const result = await api.toggleVendorLike(activeVendor.id);
      updateVendor(activeVendor.id, (vendor) => ({ ...vendor, liked_by_me: result.liked, like_count: result.like_count }));
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "点赞失败");
    } finally {
      setVendorLikePending(false);
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-10 text-soy">
        <div className="panel flex min-h-[280px] items-center justify-center">正在加载就餐地点...</div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:py-8">
      <section className="mb-5 grid gap-4 rounded-lg border border-ink/10 bg-white/90 p-4 shadow-soft lg:grid-cols-[1fr_420px]">
        <div>
          <p className="text-sm font-medium text-leaf">就餐地点社区</p>
          <h1 className="mt-1 text-2xl font-semibold text-ink sm:text-3xl">先选店铺，再看菜品和真实反馈</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-soy">
            页面重点展示窗口和饭馆：实景、位置、热度、评论和紧凑菜品列表，适合快速判断“去哪家吃”。
          </p>
          <div className="mt-4 grid gap-2 sm:grid-cols-3">
            <StatCard icon={<Building2 size={17} />} label="楼层" value={selectedArea?.section_count ?? 0} />
            <StatCard icon={<Store size={17} />} label="店铺" value={selectedArea?.vendor_count ?? 0} />
            <StatCard icon={<MessageCircle size={17} />} label="菜品" value={selectedArea?.dish_count ?? 0} />
          </div>
        </div>
        <div className="rounded-lg bg-mint/60 p-3">
          <p className="text-xs font-medium text-leaf">当前地点</p>
          <h2 className="mt-1 text-xl font-semibold text-ink">{selectedArea?.name ?? "暂无地点"}</h2>
          <p className="mt-2 flex items-center gap-1 text-sm text-soy">
            <MapPin size={15} />
            {selectedArea?.location ?? selectedArea?.address ?? "校内外"}
          </p>
          <label className="relative mt-4 block">
            <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-soy" size={17} />
            <input className="field bg-white pl-9 pr-9" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索店铺、菜品、标签" />
            {query && (
              <button type="button" className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md p-1 text-soy hover:bg-mint" onClick={() => setQuery("")} aria-label="清空搜索">
                <X size={16} />
              </button>
            )}
          </label>
        </div>
      </section>

      {message && <p className="mb-4 rounded-md bg-chili/10 px-3 py-2 text-sm text-chili">{message}</p>}

      <div className="mb-4 flex gap-2 overflow-x-auto pb-1">
        {(["CANTEEN", "SNACK_STREET", "CUSTOM_AREA"] as AreaType[]).map((type) => (
          <button key={type} type="button" className={`whitespace-nowrap rounded-md border px-3 py-2 text-sm transition ${selectedType === type ? "border-leaf bg-leaf text-white" : "border-ink/10 bg-white text-ink hover:border-leaf/50"}`} onClick={() => setSelectedType(type)}>
            {AREA_LABEL[type]}
          </button>
        ))}
      </div>

      {filteredAreas.length === 0 ? (
        <EmptyState title="暂无就餐地点" description="管理员录入餐厅、小吃街或自定义方位后，这里会展示完整信息。" />
      ) : (
        <div className="grid gap-4 lg:grid-cols-[280px_1fr]">
          <aside className="space-y-4">
            <AreaRail areas={filteredAreas} selectedAreaId={selectedAreaId} onSelect={(id) => setSelectedAreaId(id)} />
            {areaDetail?.area_type === "CANTEEN" && (
              <SectionTabs
                sections={areaDetail.sections}
                selectedSectionId={selectedSectionId}
                detailLoading={detailLoading}
                onSelect={(section) => {
                  setSelectedSectionId(section.id);
                  setSelectedVendorId(section.vendors[0]?.id ?? null);
                }}
              />
            )}
          </aside>

          <main className="grid min-w-0 gap-4 xl:grid-cols-[360px_1fr]">
            <section className="panel min-w-0">
              <div className="mb-3 flex items-center justify-between gap-3">
                <h2 className="font-semibold text-ink">店铺/窗口列表</h2>
                <span className="text-xs text-soy">{filteredVendors.length} 个</span>
              </div>
              {detailLoading ? (
                <EmptyState title="正在加载" description="店铺信息马上出现。" compact />
              ) : !sourceVendors.length ? (
                <EmptyState title="暂无店铺" description="管理员添加窗口或饭馆后即可查看。" compact />
              ) : !filteredVendors.length ? (
                <EmptyState title="搜索无结果" description="换一个店铺、菜品或标签试试。" compact />
              ) : (
                <div className="space-y-2">
                  {filteredVendors.map((vendor) => (
                    <VendorRow key={vendor.id} vendor={vendor} active={activeVendor?.id === vendor.id} onSelect={() => setSelectedVendorId(vendor.id)} />
                  ))}
                </div>
              )}
            </section>

            <section className="min-w-0 space-y-4">
              <VendorDetail vendor={activeVendor} dishes={activeDishes} queryActive={Boolean(normalizedQuery)} likePending={vendorLikePending} onLike={toggleVendorLike} onCommentAdded={() => activeVendor && updateVendor(activeVendor.id, (vendor) => ({ ...vendor, comment_count: vendor.comment_count + 1 }))} />
            </section>
          </main>
        </div>
      )}
    </div>
  );
}

function AreaRail({ areas, selectedAreaId, onSelect }: { areas: FoodAreaSummary[]; selectedAreaId: number | null; onSelect: (id: number) => void }) {
  return (
    <section className="panel">
      <h2 className="mb-3 font-semibold text-ink">地点</h2>
      <div className="-mx-1 flex gap-3 overflow-x-auto px-1 pb-1 lg:mx-0 lg:block lg:space-y-2 lg:overflow-visible lg:px-0">
        {areas.map((area) => (
          <button key={area.id} type="button" className={`min-w-[230px] rounded-md border p-3 text-left transition lg:w-full ${area.id === selectedAreaId ? "border-leaf bg-mint text-leaf" : "border-ink/10 bg-white text-ink hover:border-leaf/50"}`} onClick={() => onSelect(area.id)}>
            <span className="block font-semibold">{area.name}</span>
            <span className="mt-1 block text-xs text-soy">{AREA_LABEL[area.area_type]} · {area.location ?? area.address ?? "校内外"}</span>
            <span className="mt-2 block text-xs text-soy">{area.vendor_count} 店铺 · {area.dish_count} 菜品</span>
          </button>
        ))}
      </div>
    </section>
  );
}

function SectionTabs({ sections, selectedSectionId, detailLoading, onSelect }: { sections: FoodSection[]; selectedSectionId: number | null; detailLoading: boolean; onSelect: (section: FoodSection) => void }) {
  if (detailLoading) return <section className="panel text-sm text-soy">正在加载楼层...</section>;
  if (!sections.length) return <section className="panel text-sm text-soy">该餐厅暂无楼层。</section>;
  return (
    <section className="panel sticky top-20">
      <h2 className="mb-3 font-semibold text-ink">楼层</h2>
      <div className="flex gap-2 overflow-x-auto pb-1 lg:block lg:space-y-2 lg:overflow-visible">
        {sections.map((section) => (
          <button key={section.id} type="button" className={`min-w-[130px] rounded-md border px-3 py-2 text-left transition lg:w-full ${section.id === selectedSectionId ? "border-leaf bg-leaf text-white" : "border-ink/10 bg-white text-ink hover:border-leaf/50"}`} onClick={() => onSelect(section)}>
            <span className="block font-medium">{section.name}</span>
            <span className={`mt-1 block text-xs ${section.id === selectedSectionId ? "text-white/80" : "text-soy"}`}>{section.vendors.length} 个窗口</span>
          </button>
        ))}
      </div>
    </section>
  );
}

function VendorRow({ vendor, active, onSelect }: { vendor: FoodVendor; active: boolean; onSelect: () => void }) {
  return (
    <button type="button" className={`w-full rounded-md border p-3 text-left transition ${active ? "border-leaf bg-mint" : "border-ink/10 bg-white hover:border-leaf/50"}`} onClick={onSelect}>
      <span className="flex items-start justify-between gap-3">
        <span className="min-w-0">
          <span className="block truncate font-semibold text-ink">{vendor.name}</span>
          <span className="mt-1 line-clamp-2 text-sm leading-5 text-soy">{vendor.description ?? "暂无店铺简介"}</span>
          {vendor.location_hint && <span className="mt-1 block text-xs text-soy">位置：{vendor.location_hint}</span>}
        </span>
        <Store className="mt-1 flex-none text-leaf" size={18} />
      </span>
      <span className="mt-3 flex flex-wrap gap-2 text-xs text-soy">
        <span className="rounded-md bg-white/80 px-2 py-1">{vendor.dishes.length} 道菜</span>
        <span className="inline-flex items-center gap-1 rounded-md bg-white/80 px-2 py-1"><Heart size={13} />{vendor.like_count}</span>
        <span className="inline-flex items-center gap-1 rounded-md bg-white/80 px-2 py-1"><MessageCircle size={13} />{vendor.comment_count}</span>
      </span>
    </button>
  );
}

function VendorDetail({ vendor, dishes, queryActive, likePending, onLike, onCommentAdded }: { vendor: FoodVendor | null; dishes: Dish[]; queryActive: boolean; likePending: boolean; onLike: () => void; onCommentAdded: () => void }) {
  if (!vendor) return <section className="panel"><EmptyState title="选择店铺查看详情" description="点击左侧店铺后可查看实景、菜品列表和评论。" compact /></section>;
  const imageUrl = toMediaUrl(vendor.image_url);
  return (
    <>
      <section className="overflow-hidden rounded-lg border border-ink/10 bg-white shadow-soft">
        <div className="grid gap-0 lg:grid-cols-[300px_1fr]">
          {imageUrl ? (
            <img src={imageUrl} alt={vendor.name} className="h-56 w-full object-cover lg:h-full" />
          ) : (
            <div className="flex h-56 items-center justify-center bg-mint text-leaf lg:h-full">
              <Camera size={42} />
            </div>
          )}
          <div className="p-4">
            <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
              <div>
                <p className="text-sm font-medium text-leaf">窗口/饭馆</p>
                <h2 className="mt-1 text-2xl font-semibold text-ink">{vendor.name}</h2>
                {vendor.location_hint && <p className="mt-2 flex items-center gap-1 text-sm text-soy"><MapPin size={15} />{vendor.location_hint}</p>}
              </div>
              <button type="button" data-testid="vendor-like-button" className={`btn ${vendor.liked_by_me ? "btn-primary" : "btn-ghost"}`} onClick={onLike} disabled={likePending} aria-label={`${vendor.liked_by_me ? "取消店铺点赞" : "点赞店铺"}，当前 ${vendor.like_count} 个赞`}>
                <Heart size={16} fill={vendor.liked_by_me ? "currentColor" : "none"} />
                {vendor.liked_by_me ? "已点赞" : "点赞"} · {vendor.like_count}
              </button>
            </div>
            <p className="mt-3 text-sm leading-6 text-soy">{vendor.description ?? "暂无店铺简介，欢迎在评论区补充真实体验。"}</p>
            <div className="mt-4 flex flex-wrap gap-2 text-xs text-soy">
              <span className="rounded-md bg-mint px-2 py-1 text-leaf">{vendor.dishes.length} 道菜</span>
              <span className="rounded-md bg-rice px-2 py-1">{vendor.comment_count} 条评论</span>
              {vendor.image_url && <span className="rounded-md bg-rice px-2 py-1">有实景图</span>}
            </div>
          </div>
        </div>
      </section>

      <section className="panel">
        <h3 className="mb-3 font-semibold text-ink">菜品列表</h3>
        <DishTable dishes={dishes} originalCount={vendor.dishes.length} queryActive={queryActive} />
      </section>

      <CommentPanel vendorId={vendor.id} onCommentAdded={onCommentAdded} />
    </>
  );
}

function DishTable({ dishes, originalCount, queryActive }: { dishes: Dish[]; originalCount: number; queryActive: boolean }) {
  if (originalCount === 0) return <EmptyState title="该店铺暂无菜品" description="管理员添加菜品后即可展示。" compact />;
  if (!dishes.length) return <EmptyState title="菜品搜索无结果" description="当前店铺没有匹配关键词的菜品。" compact />;
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[560px] text-left text-sm">
        <thead className="border-b border-ink/10 text-soy">
          <tr><th className="py-2">菜品</th><th className="py-2">价格</th><th className="py-2">标签</th><th className="py-2">状态</th></tr>
        </thead>
        <tbody>
          {dishes.map((dish) => (
            <tr key={dish.id} className="border-b border-ink/5">
              <td className="py-3"><p className="font-medium text-ink">{dish.name}</p><p className="mt-1 max-w-md text-xs text-soy">{dish.description ?? (queryActive ? "匹配当前搜索" : "暂无简介")}</p></td>
              <td className="py-3 font-semibold text-chili">{dish.price ? `¥${dish.price}` : "时价"}</td>
              <td className="py-3"><div className="flex flex-wrap gap-1">{dish.tags.map((tag) => <span key={tag.id} className="rounded-md bg-rice px-2 py-1 text-xs text-soy">{tag.name}</span>)}</div></td>
              <td className="py-3"><span className={`rounded-md px-2 py-1 text-xs ${dish.is_available ? "bg-mint text-leaf" : "bg-ink/10 text-soy"}`}>{dish.is_available ? "供应中" : "已售罄"}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function CommentPanel({ vendorId, onCommentAdded }: { vendorId: number; onCommentAdded: () => void }) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [content, setContent] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(true);
  const [posting, setPosting] = useState(false);
  const [likingCommentIds, setLikingCommentIds] = useState<number[]>([]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setMessage("");
    setSuccess("");
    api
      .vendorComments(vendorId)
      .then((items) => {
        if (active) setComments(items);
      })
      .catch((caught) => {
        if (active) setMessage(caught instanceof ApiError ? caught.message : "评论加载失败");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [vendorId]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!content.trim()) return;
    setPosting(true);
    setMessage("");
    setSuccess("");
    try {
      let image_url: string | undefined;
      if (file) {
        const compressed = await compressCommentImage(file);
        image_url = (await api.uploadCommentImage(compressed)).image_url;
      }
      const created = await api.createVendorComment(vendorId, { content, image_url });
      setComments((current) => [created, ...current]);
      setContent("");
      setFile(null);
      onCommentAdded();
      setSuccess("评论发布成功");
      window.setTimeout(() => {
        document.getElementById(`comment-${created.id}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
      }, 0);
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "评论发布失败");
    } finally {
      setPosting(false);
    }
  }

  async function toggleCommentLike(commentId: number) {
    if (likingCommentIds.includes(commentId)) return;
    setLikingCommentIds((current) => [...current, commentId]);
    setMessage("");
    try {
      const result = await api.toggleCommentLike(commentId);
      setComments((current) => updateCommentTree(current, commentId, (comment) => ({ ...comment, liked_by_me: result.liked, like_count: result.like_count })));
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "评论点赞失败");
    } finally {
      setLikingCommentIds((current) => current.filter((id) => id !== commentId));
    }
  }

  async function reply(commentId: number, text: string) {
    const created = await api.replyComment(commentId, { content: text });
    setComments((current) => updateCommentTree(current, commentId, (comment) => ({ ...comment, reply_count: comment.reply_count + 1, replies: [...comment.replies, created] })));
    onCommentAdded();
  }

  const replyCount = comments.reduce((total, comment) => total + comment.reply_count, 0);

  return (
    <section className="panel">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h3 className="font-semibold text-ink">评论与追问</h3>
        <span className="text-xs text-soy">{comments.length} 条评论 · {replyCount} 条回复</span>
      </div>
      <form onSubmit={submit} className="mb-4 rounded-lg bg-mint/45 p-3">
        <textarea className="field min-h-[90px] resize-none bg-white" value={content} onChange={(event) => setContent(event.target.value)} placeholder="说说这家店的排队、口味、份量或环境..." maxLength={1000} />
        <div className="mt-2 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <label className="btn btn-ghost cursor-pointer">
              <ImagePlus size={16} />
              {file ? "已选择 1 张图片" : "添加评论图片"}
              <input className="hidden" type="file" accept="image/png,image/jpeg,image/webp" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
            </label>
            <p className="mt-1 text-xs text-soy">JPEG / PNG / WebP，压缩后不超过 1MB，每条 1 张</p>
          </div>
          <div className="text-right">
            <p className="mb-1 text-xs text-soy">{content.length}/1000</p>
            <button className="btn btn-primary" disabled={posting || !content.trim()}>
              <Send size={16} />
              {posting ? "发布中" : "发布评论"}
            </button>
          </div>
        </div>
      </form>
      {message && <p className="mb-3 rounded-md bg-chili/10 px-3 py-2 text-sm text-chili">{message}</p>}
      {success && <p className="mb-3 rounded-md bg-mint px-3 py-2 text-sm text-leaf">{success}</p>}
      {loading ? <p className="text-sm text-soy">正在加载评论...</p> : comments.length === 0 ? <EmptyState title="暂无评论" description="成为第一个分享真实体验的人。" compact /> : (
        <div className="space-y-3">
          {comments.map((comment) => <CommentItem key={comment.id} comment={comment} likePending={likingCommentIds.includes(comment.id)} onLike={toggleCommentLike} onReply={reply} />)}
        </div>
      )}
    </section>
  );
}

function CommentItem({ comment, likePending, onLike, onReply }: { comment: Comment; likePending: boolean; onLike: (id: number) => Promise<void>; onReply: (id: number, text: string) => Promise<void> }) {
  const [replyText, setReplyText] = useState("");
  const [open, setOpen] = useState(false);
  const [repliesExpanded, setRepliesExpanded] = useState(false);
  const [replyPosting, setReplyPosting] = useState(false);
  const [replyMessage, setReplyMessage] = useState("");
  const imageUrl = toMediaUrl(comment.image_url);
  async function submitReply(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = replyText.trim();
    if (!text || replyPosting) return;
    setReplyPosting(true);
    setReplyMessage("");
    try {
      await onReply(comment.id, text);
      setReplyText("");
      setOpen(false);
      setRepliesExpanded(true);
      setReplyMessage("回复发布成功");
    } catch (caught) {
      setReplyMessage(caught instanceof ApiError ? caught.message : "回复发布失败");
    } finally {
      setReplyPosting(false);
    }
  }
  return (
    <article id={`comment-${comment.id}`} className="scroll-mt-24 rounded-lg border border-ink/10 bg-white p-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-medium text-ink">{comment.author.display_name ?? comment.author.email}</p>
          <p className="mt-1 text-xs text-soy">{new Date(comment.created_at).toLocaleString("zh-CN")}</p>
        </div>
        <button className={`inline-flex items-center gap-1 rounded-md px-2 py-1 text-sm ${comment.liked_by_me ? "bg-leaf text-white" : "bg-mint text-leaf"}`} onClick={() => onLike(comment.id)} type="button" disabled={likePending} aria-label={`${comment.liked_by_me ? "取消评论点赞" : "点赞评论"}，当前 ${comment.like_count} 个赞`}>
          <Heart size={14} fill={comment.liked_by_me ? "currentColor" : "none"} />
          {comment.liked_by_me ? "已点赞" : "点赞"} · {comment.like_count}
        </button>
      </div>
      <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-ink">{comment.content}</p>
      {imageUrl && <img src={imageUrl} alt="评论图片" className="mt-3 max-h-56 rounded-md object-cover" />}
      <button type="button" className="mt-3 text-sm font-medium text-leaf" onClick={() => setOpen((value) => !value)}>
        回复 {comment.reply_count ? `(${comment.reply_count})` : ""}
      </button>
      {open && (
        <form onSubmit={submitReply} className="mt-3 grid gap-2 sm:grid-cols-[1fr_auto]">
          <div>
            <input className="field" value={replyText} onChange={(event) => setReplyText(event.target.value)} placeholder="回复这条评论" maxLength={500} />
            <p className="mt-1 text-right text-xs text-soy">{replyText.length}/500</p>
          </div>
          <button className="btn btn-primary h-10" disabled={replyPosting || !replyText.trim()}>{replyPosting ? "回复中" : "回复"}</button>
        </form>
      )}
      {replyMessage && <p className="mt-2 text-sm text-leaf">{replyMessage}</p>}
      {comment.replies.length > 0 && (
        <>
          <button type="button" className="ml-3 mt-3 text-sm font-medium text-leaf" onClick={() => setRepliesExpanded((value) => !value)}>
            {repliesExpanded ? "收起回复" : `展开 ${comment.replies.length} 条回复`}
          </button>
          {repliesExpanded && (
            <div className="mt-2 space-y-2 border-l-2 border-mint pl-3">
              {comment.replies.map((reply) => (
                <div key={reply.id} className="rounded-md bg-rice p-2 text-sm">
                  <p className="font-medium text-ink">{reply.author.display_name ?? reply.author.email}</p>
                  <p className="mt-1 text-soy">{reply.content}</p>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </article>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) {
  return (
    <div className="rounded-lg border border-ink/10 bg-white px-3 py-2">
      <div className="flex items-center gap-2 text-leaf">{icon}<span className="text-xs font-medium">{label}</span></div>
      <p className="mt-1 text-xl font-semibold text-ink">{value}</p>
    </div>
  );
}

function EmptyState({ title, description, compact = false }: { title: string; description: string; compact?: boolean }) {
  return (
    <div className={`flex flex-col items-center justify-center rounded-lg bg-mint/45 p-6 text-center ${compact ? "min-h-[130px]" : "min-h-[280px]"}`}>
      <Store className="text-leaf" size={compact ? 24 : 34} />
      <h2 className="mt-3 font-semibold text-ink">{title}</h2>
      <p className="mt-1 max-w-md text-sm leading-6 text-soy">{description}</p>
    </div>
  );
}

function updateCommentTree(comments: Comment[], commentId: number, updater: (comment: Comment) => Comment): Comment[] {
  return comments.map((comment) => {
    if (comment.id === commentId) return updater(comment);
    return { ...comment, replies: updateCommentTree(comment.replies, commentId, updater) };
  });
}

function normalize(value: string | null | undefined) {
  return (value ?? "").trim().toLowerCase();
}

function includesQuery(value: string | null | undefined, query: string) {
  return normalize(value).includes(query);
}

function vendorOwnFieldsMatchQuery(vendor: FoodVendor, query: string) {
  return includesQuery(vendor.name, query) || includesQuery(vendor.description, query) || includesQuery(vendor.location_hint, query);
}

function vendorMatchesQuery(vendor: FoodVendor, query: string) {
  return vendorOwnFieldsMatchQuery(vendor, query) || vendor.dishes.some((dish) => dishMatchesQuery(dish, query));
}

function dishMatchesQuery(dish: Dish, query: string) {
  return includesQuery(dish.name, query) || includesQuery(dish.description, query) || includesQuery(dish.price, query) || dish.tags.some((tag) => includesQuery(tag.name, query));
}
