"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ArrowRightLeft, BarChart3, Building2, ClipboardList, Download, Edit3, FileSpreadsheet, Home, ImageUp, LogOut, Megaphone, Plus, RefreshCw, ShieldCheck, Soup, Store, Tags, Trash2, Upload, Users } from "lucide-react";

import { ApiError, api, clearStoredToken } from "@/lib/api";
import { calculateAdminMetrics } from "@/lib/admin-metrics";
import { AdminOverview } from "@/components/admin/admin-overview";
import type { Announcement, AreaType, AuditLog, Dish, FoodArea, FoodVendor, ImportResult, Tag, User } from "@/lib/types";

const AREA_LABEL: Record<AreaType, string> = {
  CANTEEN: "校内餐厅",
  SNACK_STREET: "小吃街",
  CUSTOM_AREA: "自定义方位"
};

type AdminTab = "overview" | "areas" | "vendors" | "dishes" | "tags" | "users" | "announcements" | "logs" | "import";

export function AdminDashboard() {
  const [me, setMe] = useState<User | null>(null);
  const [areas, setAreas] = useState<FoodArea[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [admins, setAdmins] = useState<User[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [message, setMessage] = useState("");
  const [messageSuccess, setMessageSuccess] = useState(false);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [activeTab, setActiveTab] = useState<AdminTab>("overview");

  async function load(showFeedback = false) {
    if (showFeedback) setRefreshing(true);
    setMessage("");
    setMessageSuccess(false);
    try {
      const current = await api.me();
      setMe(current);
      if (current.role === "USER") {
        setMessage("当前账号不是管理员。");
        return;
      }
      const [areaData, tagData, userData, adminData, announcementData, logData] = await Promise.all([
        api.admin.foodAreas(),
        api.admin.tags(),
        api.admin.users(),
        api.admin.admins(),
        api.admin.announcements(),
        api.admin.auditLogs()
      ]);
      setAreas(areaData);
      setTags(tagData);
      setUsers(userData);
      setAdmins(adminData);
      setAnnouncements(announcementData);
      setAuditLogs(logData);
      setLastUpdated(new Date());
      if (showFeedback) {
        setMessage("刷新成功");
        setMessageSuccess(true);
      }
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "加载失败");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const sectionOptions = useMemo(
    () => areas.flatMap((area) => area.sections.map((section) => ({ ...section, areaName: area.name }))),
    [areas]
  );
  const vendorOptions = useMemo(
    () =>
      areas.flatMap((area) => [
        ...area.vendors.map((vendor) => ({ ...vendor, areaName: area.name, sectionName: "" })),
        ...area.sections.flatMap((section) => section.vendors.map((vendor) => ({ ...vendor, areaName: area.name, sectionName: section.name })))
      ]),
    [areas]
  );
  const metrics = useMemo(() => calculateAdminMetrics(areas), [areas]);
  const tabs: Array<{ id: AdminTab; label: string; icon: typeof BarChart3 }> = [
    { id: "overview", label: "数据概览", icon: BarChart3 },
    { id: "areas", label: "就餐地点与楼层", icon: Building2 },
    { id: "vendors", label: "店铺与窗口", icon: Store },
    { id: "dishes", label: "菜品管理", icon: Soup },
    { id: "tags", label: "标签管理", icon: Tags },
    { id: "users", label: "用户与管理员", icon: Users },
    { id: "announcements", label: "公告管理", icon: Megaphone },
    { id: "logs", label: "项目日志", icon: ClipboardList },
    { id: "import", label: "数据导入", icon: FileSpreadsheet }
  ];

  if (loading) return <div className="mx-auto max-w-7xl px-4 py-10 text-soy">正在进入管理端...</div>;

  if (!me || me.role === "USER") {
    async function switchAccount() {
      await clearStoredToken();
      window.location.assign("/auth/login?next=%2Fadmin");
    }
    return (
      <div className="mx-auto max-w-xl px-4 py-16">
        <div className="panel text-center">
          <ShieldCheck className="mx-auto mb-3 text-leaf" size={34} />
          <h1 className="text-2xl font-semibold text-ink">当前账号没有管理权限</h1>
          <p className="mt-2 text-sm text-soy">{message || "普通用户可以继续使用食堂、筛选和每日抽签功能。"}</p>
          <div className="mt-5 flex flex-wrap justify-center gap-2">
            <Link className="btn btn-ghost" href="/">
              <Home size={16} />
              返回首页
            </Link>
            <button className="btn btn-primary" type="button" onClick={switchAccount}>
              <LogOut size={16} />
              退出并切换管理员账号
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-leaf">{me.role === "SUPER_ADMIN" ? "终极管理员" : "基本管理员"}</p>
          <h1 className="text-3xl font-semibold text-ink">管理工作台</h1>
        </div>
        <button className="btn btn-ghost" onClick={() => load(true)} disabled={refreshing}>
          <RefreshCw size={16} />
          {refreshing ? "刷新中" : "刷新"}
        </button>
      </div>

      {message && <p className={`mb-4 rounded-md px-3 py-2 text-sm ${messageSuccess ? "bg-mint text-leaf" : "bg-chili/10 text-chili"}`}>{message}</p>}

      <div className="grid gap-5 lg:grid-cols-[210px_minmax(0,1fr)]">
        <aside className="sticky top-3 z-10 -mx-4 flex gap-2 overflow-x-auto border-y border-ink/10 bg-white/95 px-4 py-3 lg:mx-0 lg:block lg:h-fit lg:space-y-1 lg:rounded-lg lg:border lg:p-2">
          {tabs.map(({ id, label, icon: Icon }) => (
            <button key={id} type="button" className={`flex min-w-fit items-center gap-2 rounded-md px-3 py-2 text-sm font-medium lg:w-full ${activeTab === id ? "bg-leaf text-white" : "text-ink hover:bg-mint"}`} onClick={() => setActiveTab(id)} aria-current={activeTab === id ? "page" : undefined}>
              <Icon size={16} />
              {label}
            </button>
          ))}
        </aside>

        <main className="min-w-0 space-y-5">
          {activeTab === "overview" && <AdminOverview metrics={metrics} lastUpdated={lastUpdated} />}
          {activeTab === "areas" && (
            <>
              <CreateAreaForm onDone={load} />
              <ContentForms mode="sections" areas={areas} sectionOptions={sectionOptions} vendorOptions={vendorOptions} tags={tags} onDone={load} />
              <AreaTable areas={areas} onDone={load} />
            </>
          )}
          {activeTab === "vendors" && (
            <>
              <ContentForms mode="vendors" areas={areas} sectionOptions={sectionOptions} vendorOptions={vendorOptions} tags={tags} onDone={load} />
              <VendorTable vendors={vendorOptions} onDone={load} />
            </>
          )}
          {activeTab === "dishes" && (
            <>
              <ContentForms mode="dishes" areas={areas} sectionOptions={sectionOptions} vendorOptions={vendorOptions} tags={tags} onDone={load} />
              <DishManagementTable vendors={vendorOptions} tags={tags} onDone={load} />
            </>
          )}
          {activeTab === "tags" && <CreateTagForm tags={tags} onDone={load} />}
          {activeTab === "users" && (
            <div className="grid gap-5 xl:grid-cols-2">
              <UserPanel users={users} onDone={load} />
              <AdminPanel admins={admins} me={me} canManage={me.role === "SUPER_ADMIN"} onDone={load} />
            </div>
          )}
          {activeTab === "announcements" && <AnnouncementPanel announcements={announcements} onDone={load} />}
          {activeTab === "logs" && <AuditLogPanel logs={auditLogs} />}
          {activeTab === "import" && <ImportPanel onDone={load} />}
        </main>
      </div>
    </div>
  );
}

function ImportPanel({ onDone }: { onDone: () => Promise<void> }) {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [working, setWorking] = useState(false);
  const [message, setMessage] = useState("");

  async function downloadTemplate() {
    const blob = await api.admin.downloadFoodTemplate();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "sxu-food-import-template.xlsx";
    link.click();
    URL.revokeObjectURL(url);
  }

  async function runImport(dryRun: boolean) {
    if (!file) {
      setMessage("请先选择 .xlsx 文件");
      return;
    }
    setWorking(true);
    setMessage("");
    try {
      const data = await api.admin.importFoodData(file, dryRun);
      setResult(data);
      if (!dryRun) await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "导入失败");
    } finally {
      setWorking(false);
    }
  }

  return (
    <section className="panel">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-ink">批量导入</h2>
          <p className="mt-1 text-sm text-soy">支持 .xlsx，先预检再正式导入，重复数据会更新合并。</p>
        </div>
        <button type="button" className="btn btn-ghost" onClick={downloadTemplate}>
          <Download size={16} />
          模板
        </button>
      </div>
      <div className="grid gap-3 md:grid-cols-[1fr_auto_auto]">
        <input className="field" type="file" accept=".xlsx" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
        <button type="button" className="btn btn-ghost" disabled={working || !file} onClick={() => runImport(true)}>
          预检
        </button>
        <button type="button" className="btn btn-primary" disabled={working || !file} onClick={() => runImport(false)}>
          <Upload size={16} />
          导入
        </button>
      </div>
      {message && <p className="mt-3 rounded-md bg-chili/10 px-3 py-2 text-sm text-chili">{message}</p>}
      {result && (
        <div className="mt-3 rounded-lg bg-mint/45 p-3 text-sm text-soy">
          <p className="font-medium text-ink">{result.dry_run ? "预检结果" : "导入结果"}</p>
          <p className="mt-1">
            新建 {result.created_count} · 更新 {result.updated_count} · 跳过 {result.skipped_count} · 错误 {result.error_count}
          </p>
          {result.errors.length > 0 && (
            <div className="mt-2 space-y-1 text-chili">
              {result.errors.slice(0, 5).map((error) => (
                <p key={`${error.row}-${error.message}`}>第 {error.row} 行：{error.message}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}

function CreateAreaForm({ onDone }: { onDone: () => Promise<void> }) {
  const [name, setName] = useState("");
  const [location, setLocation] = useState("");
  const [description, setDescription] = useState("");
  const [areaType, setAreaType] = useState<AreaType>("CANTEEN");
  const [working, setWorking] = useState(false);
  const [message, setMessage] = useState("");
  const [success, setSuccess] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!name.trim() || working) return;
    setWorking(true);
    setMessage("");
    setSuccess(false);
    try {
      await api.admin.createFoodArea({ name: name.trim(), location: location.trim() || undefined, area_type: areaType, description: description.trim() || undefined });
      setName("");
      setLocation("");
      setDescription("");
      setMessage(`已创建地点：${name.trim()}`);
      setSuccess(true);
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "地点创建失败");
    } finally {
      setWorking(false);
    }
  }

  return (
    <form className="panel" onSubmit={submit}>
      <h2 className="text-lg font-semibold text-ink">新增就餐地点/位置</h2>
      <p className="mb-3 mt-1 text-sm text-soy">可录入校内餐厅、小吃街或自定义方位，例如“山西大学西侧小吃街”；创建后可在下方编辑或删除。</p>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-[150px_1fr_1fr_1fr_auto]">
        <select className="field" aria-label="地点类型，必填" value={areaType} onChange={(event) => setAreaType(event.target.value as AreaType)}>
          <option value="CANTEEN">校内餐厅</option>
          <option value="SNACK_STREET">小吃街</option>
          <option value="CUSTOM_AREA">自定义方位</option>
        </select>
        <input className="field" placeholder="地点名称，如：山西大学西侧小吃街 *" required value={name} onChange={(event) => setName(event.target.value)} />
        <input className="field" placeholder="具体方位，如：山西大学西门外" value={location} onChange={(event) => setLocation(event.target.value)} />
        <input className="field" placeholder="地点简介" value={description} onChange={(event) => setDescription(event.target.value)} />
        <button className="btn btn-primary" disabled={working || !name.trim()}>
          <Plus size={16} />
          {working ? "添加中" : "添加"}
        </button>
      </div>
      {message && <p className={`mt-3 text-sm ${success ? "text-leaf" : "text-chili"}`}>{message}</p>}
    </form>
  );
}

function ContentForms({
  mode,
  areas,
  sectionOptions,
  vendorOptions,
  tags,
  onDone
}: {
  mode: "sections" | "vendors" | "dishes";
  areas: FoodArea[];
  sectionOptions: Array<{ id: number; name: string; areaName: string }>;
  vendorOptions: Array<FoodVendor & { areaName: string; sectionName: string }>;
  tags: Tag[];
  onDone: () => Promise<void>;
}) {
  const [areaId, setAreaId] = useState("");
  const [sectionName, setSectionName] = useState("");
  const [sectionLevel, setSectionLevel] = useState("1");
  const [vendorAreaId, setVendorAreaId] = useState("");
  const [sectionId, setSectionId] = useState("");
  const [vendorName, setVendorName] = useState("");
  const [vendorLocation, setVendorLocation] = useState("");
  const [vendorDescription, setVendorDescription] = useState("");
  const [vendorImageUrl, setVendorImageUrl] = useState("");
  const [dishVendorId, setDishVendorId] = useState("");
  const [dishName, setDishName] = useState("");
  const [dishPrice, setDishPrice] = useState("");
  const [dishDescription, setDishDescription] = useState("");
  const [dishImageUrl, setDishImageUrl] = useState("");
  const [dishTagIds, setDishTagIds] = useState<number[]>([]);
  const [working, setWorking] = useState<"section" | "vendor" | "dish" | null>(null);
  const [message, setMessage] = useState("");
  const [success, setSuccess] = useState(false);

  const selectedVendorArea = areas.find((area) => area.id === Number(vendorAreaId));

  async function addSection(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!areaId || !sectionName.trim() || working) return;
    setWorking("section");
    setMessage("");
    setSuccess(false);
    try {
      await api.admin.createFoodSection(Number(areaId), { name: sectionName.trim(), level: Number(sectionLevel) || 1 });
      setSectionName("");
      setMessage("楼层创建成功");
      setSuccess(true);
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "楼层创建失败");
    } finally {
      setWorking(null);
    }
  }

  async function addVendor(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedVendorArea || !vendorName.trim() || (selectedVendorArea.area_type === "CANTEEN" && !sectionId) || working) return;
    setWorking("vendor");
    setMessage("");
    setSuccess(false);
    try {
      const payload = { name: vendorName.trim(), description: vendorDescription.trim() || undefined, location_hint: vendorLocation.trim() || undefined, image_url: vendorImageUrl.trim() || undefined };
      if (selectedVendorArea.area_type === "CANTEEN") {
        await api.admin.createSectionVendor(Number(sectionId), payload);
      } else {
        await api.admin.createDirectVendor(Number(vendorAreaId), payload);
      }
      setVendorName("");
      setVendorLocation("");
      setVendorDescription("");
      setVendorImageUrl("");
      setMessage("店铺创建成功");
      setSuccess(true);
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "店铺创建失败");
    } finally {
      setWorking(null);
    }
  }

  async function addDish(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!dishVendorId || !dishName.trim() || working) return;
    setWorking("dish");
    setMessage("");
    setSuccess(false);
    try {
      await api.admin.createVendorDish(Number(dishVendorId), { name: dishName.trim(), description: dishDescription.trim() || undefined, price: dishPrice || undefined, image_url: dishImageUrl.trim() || undefined, tag_ids: dishTagIds });
      setDishName("");
      setDishPrice("");
      setDishDescription("");
      setDishImageUrl("");
      setDishTagIds([]);
      setMessage("菜品创建成功");
      setSuccess(true);
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "菜品创建失败");
    } finally {
      setWorking(null);
    }
  }

  function toggleDishTag(tagId: number) {
    setDishTagIds((current) => (current.includes(tagId) ? current.filter((id) => id !== tagId) : [...current, tagId]));
  }

  return (
    <div>
      {mode === "sections" && <form className="panel" onSubmit={addSection}>
        <h3 className="mb-3 font-semibold text-ink">新增餐厅楼层</h3>
        <select className="field mb-2" value={areaId} onChange={(event) => setAreaId(event.target.value)}>
          <option value="">选择餐厅</option>
          {areas.filter((area) => area.area_type === "CANTEEN").map((area) => (
            <option key={area.id} value={area.id}>
              {area.name}
            </option>
          ))}
        </select>
        <input className="field mb-2" placeholder="楼层名称 *" required disabled={!areaId} value={sectionName} onChange={(event) => setSectionName(event.target.value)} />
        <input className="field mb-2" placeholder="楼层序号 *" required min="1" type="number" disabled={!areaId} value={sectionLevel} onChange={(event) => setSectionLevel(event.target.value)} />
        <button className="btn btn-primary w-full" disabled={working !== null || !areaId || !sectionName.trim()}>{working === "section" ? "添加中" : "添加楼层"}</button>
      </form>}

      {mode === "vendors" && <form className="panel" onSubmit={addVendor}>
        <h3 className="mb-3 font-semibold text-ink">新增店铺/窗口</h3>
        <select className="field mb-2" value={vendorAreaId} onChange={(event) => { setVendorAreaId(event.target.value); setSectionId(""); }}>
          <option value="">选择地点</option>
          {areas.map((area) => (
            <option key={area.id} value={area.id}>
              {AREA_LABEL[area.area_type]} · {area.name}
            </option>
          ))}
        </select>
        {selectedVendorArea?.area_type === "CANTEEN" && (
          <select className="field mb-2" required value={sectionId} onChange={(event) => setSectionId(event.target.value)}>
            <option value="">选择楼层</option>
            {sectionOptions
              .filter((section) => section.areaName === selectedVendorArea.name)
              .map((section) => (
                <option key={section.id} value={section.id}>
                  {section.areaName} · {section.name}
                </option>
              ))}
          </select>
        )}
        <input className="field mb-2" placeholder="店铺/窗口名称 *" required disabled={!vendorAreaId || (selectedVendorArea?.area_type === "CANTEEN" && !sectionId)} value={vendorName} onChange={(event) => setVendorName(event.target.value)} />
        <input className="field mb-2" placeholder="店铺位置" disabled={!vendorAreaId} value={vendorLocation} onChange={(event) => setVendorLocation(event.target.value)} />
        <textarea className="field mb-2" placeholder="店铺简介" disabled={!vendorAreaId} value={vendorDescription} onChange={(event) => setVendorDescription(event.target.value)} />
        <input className="field mb-2" placeholder="实景图片 URL" disabled={!vendorAreaId} value={vendorImageUrl} onChange={(event) => setVendorImageUrl(event.target.value)} />
        <button className="btn btn-primary w-full" disabled={working !== null || !selectedVendorArea || !vendorName.trim() || (selectedVendorArea.area_type === "CANTEEN" && !sectionId)}>{working === "vendor" ? "添加中" : "添加店铺"}</button>
      </form>}

      {mode === "dishes" && <form className="panel" onSubmit={addDish}>
        <h3 className="mb-3 font-semibold text-ink">新增菜品</h3>
        <select className="field mb-2" value={dishVendorId} onChange={(event) => setDishVendorId(event.target.value)}>
          <option value="">选择店铺/窗口</option>
          {vendorOptions.map((vendor) => (
            <option key={vendor.id} value={vendor.id}>
              {vendor.areaName} · {vendor.sectionName ? `${vendor.sectionName} · ` : ""}{vendor.name}
            </option>
          ))}
        </select>
        <input className="field mb-2" placeholder="菜品名称 *" required disabled={!dishVendorId} value={dishName} onChange={(event) => setDishName(event.target.value)} />
        <input className="field mb-2" placeholder="价格，如 12.50" inputMode="decimal" disabled={!dishVendorId} value={dishPrice} onChange={(event) => setDishPrice(event.target.value)} />
        <textarea className="field mb-2" placeholder="菜品简介" disabled={!dishVendorId} value={dishDescription} onChange={(event) => setDishDescription(event.target.value)} />
        <input className="field mb-2" placeholder="菜品图片 URL" disabled={!dishVendorId} value={dishImageUrl} onChange={(event) => setDishImageUrl(event.target.value)} />
        <div className="mb-3 flex flex-wrap gap-2">
          {tags.map((tag) => (
            <button
              key={tag.id}
              type="button"
              className={`rounded-md border px-2 py-1 text-xs ${
                dishTagIds.includes(tag.id) ? "border-leaf bg-mint text-leaf" : "border-ink/10 bg-white text-soy"
              }`}
              onClick={() => toggleDishTag(tag.id)}
            >
              {tag.name}
            </button>
          ))}
        </div>
        <button className="btn btn-primary w-full" disabled={working !== null || !dishVendorId || !dishName.trim()}>{working === "dish" ? "添加中" : "添加菜品"}</button>
      </form>}
      {message && <p className={`mt-3 rounded-md px-3 py-2 text-sm ${success ? "bg-mint text-leaf" : "bg-chili/10 text-chili"}`}>{message}</p>}
    </div>
  );
}

function AreaTable({ areas, onDone }: { areas: FoodArea[]; onDone: () => Promise<void> }) {
  const [workingKey, setWorkingKey] = useState("");
  const [message, setMessage] = useState("");
  async function toggleArea(area: FoodArea) {
    setWorkingKey(`area-${area.id}`);
    setMessage("");
    try {
      await api.admin.updateFoodArea(area.id, { is_active: !area.is_active });
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "地点状态更新失败");
    } finally {
      setWorkingKey("");
    }
  }

  async function editArea(area: FoodArea) {
    const name = window.prompt("地点名称", area.name);
    if (!name?.trim()) return;
    const type = window.prompt("地点类型：CANTEEN / SNACK_STREET / CUSTOM_AREA", area.area_type) as AreaType | null;
    if (!type || !["CANTEEN", "SNACK_STREET", "CUSTOM_AREA"].includes(type)) {
      setMessage("地点类型无效");
      return;
    }
    const location = window.prompt("大概位置", area.location ?? "");
    const description = window.prompt("地点简介", area.description ?? "");
    if (location === null || description === null) return;
    setWorkingKey(`area-${area.id}`);
    try {
      await api.admin.updateFoodArea(area.id, { name: name.trim(), area_type: type, location, description });
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "地点编辑失败");
    } finally {
      setWorkingKey("");
    }
  }

  async function deleteArea(area: FoodArea) {
    if (!window.confirm(`确认删除地点“${area.name}”及其全部楼层、店铺和菜品？此操作不可撤销。`)) return;
    setWorkingKey(`area-${area.id}`);
    try {
      await api.admin.deleteFoodArea(area.id);
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "地点删除失败");
    } finally {
      setWorkingKey("");
    }
  }

  async function editSection(section: FoodArea["sections"][number]) {
    const name = window.prompt("楼层名称", section.name);
    if (!name?.trim()) return;
    const levelText = window.prompt("楼层序号", String(section.level));
    const level = Number(levelText);
    if (!Number.isInteger(level) || level < 1) {
      setMessage("楼层序号必须是正整数");
      return;
    }
    const description = window.prompt("楼层简介", section.description ?? "");
    if (description === null) return;
    setWorkingKey(`section-${section.id}`);
    try {
      await api.admin.updateFoodSection(section.id, { name: name.trim(), level, description });
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "楼层编辑失败");
    } finally {
      setWorkingKey("");
    }
  }

  async function deleteSection(section: FoodArea["sections"][number]) {
    if (!window.confirm(`确认删除楼层“${section.name}”及其全部窗口和菜品？`)) return;
    setWorkingKey(`section-${section.id}`);
    try {
      await api.admin.deleteFoodSection(section.id);
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "楼层删除失败");
    } finally {
      setWorkingKey("");
    }
  }
  return (
    <section className="panel">
      <h2 className="mb-3 text-lg font-semibold text-ink">地点数据</h2>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="border-b border-ink/10 text-soy">
            <tr>
              <th className="py-2">类型</th>
              <th className="py-2">地点</th>
              <th className="py-2">楼层</th>
              <th className="py-2">店铺</th>
              <th className="py-2">菜品</th>
              <th className="py-2">状态</th>
              <th className="py-2">操作</th>
            </tr>
          </thead>
          <tbody>
            {areas.map((area) => {
              const sectionVendors = area.sections.flatMap((section) => section.vendors);
              const vendors = [...area.vendors, ...sectionVendors];
              return (
                <tr key={area.id} className="border-b border-ink/5">
                  <td className="py-3 text-soy">{AREA_LABEL[area.area_type]}</td>
                  <td className="py-3 font-medium text-ink">{area.name}</td>
                  <td className="py-3">
                    <div className="space-y-2">
                      {area.sections.length || "—"}
                      {area.sections.map((section) => (
                        <div key={section.id} className="flex items-center gap-1 text-xs">
                          <span>{section.name}（{section.level}）</span>
                          <button type="button" className="text-leaf underline" disabled={Boolean(workingKey)} onClick={() => editSection(section)}>编辑</button>
                          <button type="button" className="text-chili underline" disabled={Boolean(workingKey)} onClick={() => deleteSection(section)}>删除</button>
                        </div>
                      ))}
                    </div>
                  </td>
                  <td className="py-3">{vendors.length}</td>
                  <td className="py-3">{vendors.reduce((sum, vendor) => sum + vendor.dishes.length, 0)}</td>
                  <td className="py-3">
                    <button type="button" className="btn btn-ghost" disabled={Boolean(workingKey)} onClick={() => toggleArea(area)}>
                      {area.is_active ? "停用" : "启用"}
                    </button>
                  </td>
                  <td className="py-3">
                    <div className="flex gap-1">
                      <button type="button" className="btn btn-ghost" disabled={Boolean(workingKey)} onClick={() => editArea(area)}><Edit3 size={14} />编辑</button>
                      <button type="button" className="btn btn-ghost text-chili" disabled={Boolean(workingKey)} onClick={() => deleteArea(area)}><Trash2 size={14} />删除</button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {message && <p className="mt-3 text-sm text-chili">{message}</p>}
    </section>
  );
}

function VendorTable({ vendors, onDone }: { vendors: Array<FoodVendor & { areaName: string; sectionName: string }>; onDone: () => Promise<void> }) {
  const [workingId, setWorkingId] = useState<number | null>(null);
  const [message, setMessage] = useState("");
  async function toggle(vendor: FoodVendor) {
    setWorkingId(vendor.id);
    setMessage("");
    try {
      await api.admin.updateVendor(vendor.id, { is_active: !vendor.is_active });
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "店铺状态更新失败");
    } finally {
      setWorkingId(null);
    }
  }

  async function edit(vendor: FoodVendor) {
    const name = window.prompt("店铺/窗口名称", vendor.name);
    if (!name?.trim()) return;
    const location = window.prompt("店铺位置", vendor.location_hint ?? "");
    const description = window.prompt("店铺简介", vendor.description ?? "");
    const imageUrl = window.prompt("图片 URL（也可取消后使用“替换图片”上传）", vendor.image_url ?? "");
    if (location === null || description === null || imageUrl === null) return;
    setWorkingId(vendor.id);
    try {
      await api.admin.updateVendor(vendor.id, { name: name.trim(), location_hint: location, description, image_url: imageUrl });
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "店铺编辑失败");
    } finally {
      setWorkingId(null);
    }
  }

  async function replaceImage(vendor: FoodVendor, file: File | undefined) {
    if (!file) return;
    setWorkingId(vendor.id);
    try {
      const uploaded = await api.admin.uploadImage(file);
      await api.admin.updateVendor(vendor.id, { image_url: uploaded.image_url });
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "图片替换失败");
    } finally {
      setWorkingId(null);
    }
  }

  async function remove(vendor: FoodVendor) {
    if (!window.confirm(`确认删除店铺/窗口“${vendor.name}”及其全部菜品？`)) return;
    setWorkingId(vendor.id);
    try {
      await api.admin.deleteVendor(vendor.id);
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "店铺删除失败");
    } finally {
      setWorkingId(null);
    }
  }
  return (
    <section className="panel">
      <h2 className="mb-3 text-lg font-semibold text-ink">既有店铺/窗口</h2>
      <div className="space-y-2">
        {vendors.map((vendor) => (
          <div key={vendor.id} className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-ink/10 p-3">
            <div>
              <p className="font-medium text-ink">{vendor.name}</p>
              <p className="text-sm text-soy">{vendor.areaName}{vendor.sectionName ? ` · ${vendor.sectionName}` : ""} · {vendor.dishes.length} 道菜</p>
            </div>
            <div className="flex flex-wrap gap-1">
              <button type="button" className="btn btn-ghost" disabled={workingId === vendor.id} onClick={() => edit(vendor)}><Edit3 size={14} />编辑</button>
              <label className="btn btn-ghost cursor-pointer">
                <ImageUp size={14} />替换图片
                <input className="hidden" type="file" accept="image/jpeg,image/png,image/webp" disabled={workingId === vendor.id} onChange={(event) => replaceImage(vendor, event.target.files?.[0])} />
              </label>
              <button type="button" className="btn btn-ghost" disabled={workingId === vendor.id} onClick={() => toggle(vendor)}>{vendor.is_active ? "停用" : "启用"}</button>
              <button type="button" className="btn btn-ghost text-chili" disabled={workingId === vendor.id} onClick={() => remove(vendor)}><Trash2 size={14} />删除</button>
            </div>
          </div>
        ))}
      </div>
      {message && <p className="mt-3 text-sm text-chili">{message}</p>}
    </section>
  );
}

function DishManagementTable({ vendors, tags, onDone }: { vendors: Array<FoodVendor & { areaName: string; sectionName: string }>; tags: Tag[]; onDone: () => Promise<void> }) {
  const [workingId, setWorkingId] = useState<number | null>(null);
  const [message, setMessage] = useState("");
  const dishes = vendors.flatMap((vendor) => vendor.dishes.map((dish) => ({ dish, vendor })));
  async function toggle(item: (typeof dishes)[number]) {
    setWorkingId(item.dish.id);
    setMessage("");
    try {
      await api.admin.updateDish(item.dish.id, { is_available: !item.dish.is_available });
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "菜品状态更新失败");
    } finally {
      setWorkingId(null);
    }
  }

  async function edit(dish: Dish) {
    const name = window.prompt("菜品名称", dish.name);
    if (!name?.trim()) return;
    const price = window.prompt("价格（留空表示未填写）", dish.price ?? "");
    const description = window.prompt("菜品简介", dish.description ?? "");
    const imageUrl = window.prompt("图片 URL（也可取消后使用“替换图片”上传）", dish.image_url ?? "");
    const tagHelp = tags.map((tag) => `${tag.id}=${tag.name}`).join("，");
    const tagIdsText = window.prompt(`标签 ID，使用英文逗号分隔。可选：${tagHelp}`, dish.tags.map((tag) => tag.id).join(","));
    if (price === null || description === null || imageUrl === null || tagIdsText === null) return;
    const tagIds = tagIdsText.trim() ? tagIdsText.split(",").map((value) => Number(value.trim())) : [];
    if (tagIds.some((id) => !Number.isInteger(id) || !tags.some((tag) => tag.id === id))) {
      setMessage("标签 ID 无效");
      return;
    }
    setWorkingId(dish.id);
    try {
      await api.admin.updateDish(dish.id, { name: name.trim(), price: price.trim() || null, description, image_url: imageUrl, tag_ids: tagIds });
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "菜品编辑失败");
    } finally {
      setWorkingId(null);
    }
  }

  async function replaceImage(dish: Dish, file: File | undefined) {
    if (!file) return;
    setWorkingId(dish.id);
    try {
      const uploaded = await api.admin.uploadImage(file);
      await api.admin.updateDish(dish.id, { image_url: uploaded.image_url });
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "图片替换失败");
    } finally {
      setWorkingId(null);
    }
  }

  async function remove(dish: Dish) {
    if (!window.confirm(`确认删除菜品“${dish.name}”？`)) return;
    setWorkingId(dish.id);
    try {
      await api.admin.deleteDish(dish.id);
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "菜品删除失败");
    } finally {
      setWorkingId(null);
    }
  }
  return (
    <section className="panel">
      <h2 className="mb-3 text-lg font-semibold text-ink">既有菜品</h2>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[620px] text-left text-sm">
          <thead className="border-b border-ink/10 text-soy"><tr><th className="py-2">菜品</th><th>店铺</th><th>价格</th><th>标签</th><th>状态</th><th>操作</th></tr></thead>
          <tbody>
            {dishes.map((item) => (
              <tr key={item.dish.id} className="border-b border-ink/5">
                <td className="py-3 font-medium text-ink">{item.dish.name}</td>
                <td>{item.vendor.name}</td>
                <td>{item.dish.price ? `¥${item.dish.price}` : "未填写"}</td>
                <td>{item.dish.tags.map((tag) => tag.name).join("、") || "—"}</td>
                <td>{item.dish.is_available ? "供应中" : "已停售"}</td>
                <td>
                  <div className="flex flex-wrap gap-1">
                    <button type="button" className="btn btn-ghost" disabled={workingId === item.dish.id} onClick={() => edit(item.dish)}><Edit3 size={14} />编辑</button>
                    <label className="btn btn-ghost cursor-pointer"><ImageUp size={14} />替换图片<input className="hidden" type="file" accept="image/jpeg,image/png,image/webp" disabled={workingId === item.dish.id} onChange={(event) => replaceImage(item.dish, event.target.files?.[0])} /></label>
                    <button type="button" className="btn btn-ghost" disabled={workingId === item.dish.id} onClick={() => toggle(item)}>{item.dish.is_available ? "停售" : "恢复"}</button>
                    <button type="button" className="btn btn-ghost text-chili" disabled={workingId === item.dish.id} onClick={() => remove(item.dish)}><Trash2 size={14} />删除</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {message && <p className="mt-3 text-sm text-chili">{message}</p>}
    </section>
  );
}

function CreateTagForm({ tags, onDone }: { tags: Tag[]; onDone: () => Promise<void> }) {
  const [name, setName] = useState("");
  const [category, setCategory] = useState<"basic" | "taste">("basic");
  const [working, setWorking] = useState(false);
  const [message, setMessage] = useState("");
  const [workingTagId, setWorkingTagId] = useState<number | null>(null);
  const [toggleError, setToggleError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!name.trim() || working) return;
    setWorking(true);
    setMessage("");
    try {
      await api.admin.createTag({ name: name.trim(), category });
      setName("");
      setMessage("标签创建成功");
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "标签创建失败");
    } finally {
      setWorking(false);
    }
  }

  async function toggle(tag: Tag) {
    setWorkingTagId(tag.id);
    setToggleError("");
    try {
      await api.admin.updateTag(tag.id, { is_active: !tag.is_active });
      await onDone();
    } catch (caught) {
      setToggleError(caught instanceof ApiError ? caught.message : "标签状态更新失败");
    } finally {
      setWorkingTagId(null);
    }
  }

  async function edit(tag: Tag) {
    const updatedName = window.prompt("标签名称", tag.name);
    if (!updatedName?.trim()) return;
    const updatedCategory = window.prompt("标签类型：basic 或 taste", tag.category) as "basic" | "taste" | null;
    if (!updatedCategory || !["basic", "taste"].includes(updatedCategory)) {
      setToggleError("标签类型无效");
      return;
    }
    setWorkingTagId(tag.id);
    try {
      await api.admin.updateTag(tag.id, { name: updatedName.trim(), category: updatedCategory });
      await onDone();
    } catch (caught) {
      setToggleError(caught instanceof ApiError ? caught.message : "标签编辑失败");
    } finally {
      setWorkingTagId(null);
    }
  }

  async function remove(tag: Tag) {
    if (!window.confirm(`确认删除标签“${tag.name}”？菜品与该标签的关联也会删除。`)) return;
    setWorkingTagId(tag.id);
    try {
      await api.admin.deleteTag(tag.id);
      await onDone();
    } catch (caught) {
      setToggleError(caught instanceof ApiError ? caught.message : "标签删除失败");
    } finally {
      setWorkingTagId(null);
    }
  }

  return (
    <form className="panel" onSubmit={submit}>
      <h2 className="mb-3 text-lg font-semibold text-ink">新增标签</h2>
      <input className="field mb-2" placeholder="标签名，如 面、辣 *" required value={name} onChange={(event) => setName(event.target.value)} />
      <select className="field mb-3" value={category} onChange={(event) => setCategory(event.target.value as "basic" | "taste")}>
        <option value="basic">基础类型</option>
        <option value="taste">味道类型</option>
      </select>
      <button className="btn btn-primary w-full" disabled={working || !name.trim()}>{working ? "添加中" : "添加标签"}</button>
      {message && <p className="mt-2 text-sm text-leaf">{message}</p>}
      <div className="mt-4 space-y-2">
        {tags.map((tag) => (
          <div key={tag.id} className="flex items-center justify-between rounded-md bg-mint/45 p-2 text-sm">
            <span>{tag.name} · {tag.category === "basic" ? "基础" : "味道"}</span>
            <div className="flex gap-1">
              <button type="button" className="btn btn-ghost" disabled={workingTagId === tag.id} onClick={() => edit(tag)}><Edit3 size={14} />编辑</button>
              <button type="button" className="btn btn-ghost" disabled={workingTagId === tag.id} onClick={() => toggle(tag)}>{tag.is_active ? "停用" : "启用"}</button>
              <button type="button" className="btn btn-ghost text-chili" disabled={workingTagId === tag.id} onClick={() => remove(tag)}><Trash2 size={14} />删除</button>
            </div>
          </div>
        ))}
      </div>
      {toggleError && <p className="mt-3 text-sm text-chili">{toggleError}</p>}
    </form>
  );
}

function AnnouncementPanel({ announcements, onDone }: { announcements: Announcement[]; onDone: () => Promise<void> }) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [level, setLevel] = useState<"INFO" | "IMPORTANT">("INFO");
  const [expiresAt, setExpiresAt] = useState("");
  const [working, setWorking] = useState(false);
  const [message, setMessage] = useState("");

  async function publish(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!title.trim() || !content.trim() || working) return;
    setWorking(true);
    setMessage("");
    try {
      await api.admin.publishAnnouncement({
        title: title.trim(),
        content: content.trim(),
        level,
        ...(expiresAt ? { expires_at: new Date(expiresAt).toISOString() } : {})
      });
      setTitle("");
      setContent("");
      setExpiresAt("");
      setLevel("INFO");
      setMessage("公告发布成功");
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "公告发布失败");
    } finally {
      setWorking(false);
    }
  }

  async function remove(announcement: Announcement) {
    if (!window.confirm(`确认删除公告“${announcement.title}”？`)) return;
    setWorking(true);
    setMessage("");
    try {
      await api.admin.deleteAnnouncement(announcement.id);
      setMessage("公告已删除");
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "公告删除失败");
    } finally {
      setWorking(false);
    }
  }

  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,420px)_minmax(0,1fr)]">
      <form className="panel h-fit space-y-3" onSubmit={publish}>
        <div className="flex items-center gap-2">
          <Megaphone size={18} className="text-leaf" />
          <div>
            <h2 className="text-lg font-semibold text-ink">发布公告</h2>
            <p className="text-sm text-soy">发布后立即显示在首页，可设置自动失效时间。</p>
          </div>
        </div>
        <input className="field" maxLength={120} required placeholder="公告标题 *" value={title} onChange={(event) => setTitle(event.target.value)} />
        <textarea className="field min-h-32 resize-y" maxLength={2000} required placeholder="公告正文 *" value={content} onChange={(event) => setContent(event.target.value)} />
        <select className="field" value={level} onChange={(event) => setLevel(event.target.value as "INFO" | "IMPORTANT")}>
          <option value="INFO">普通公告</option>
          <option value="IMPORTANT">重要公告</option>
        </select>
        <label className="block text-sm text-soy">
          <span className="mb-1 block">失效时间（可选）</span>
          <input className="field" type="datetime-local" value={expiresAt} onChange={(event) => setExpiresAt(event.target.value)} />
        </label>
        <button className="btn btn-primary w-full" disabled={working || !title.trim() || !content.trim()}>
          <Megaphone size={16} />{working ? "处理中" : "发布公告"}
        </button>
        {message && <p className="text-sm text-leaf">{message}</p>}
      </form>

      <section className="panel">
        <h2 className="mb-3 text-lg font-semibold text-ink">公告记录</h2>
        <div className="space-y-3">
          {announcements.map((announcement) => {
            const expired = announcement.expires_at ? new Date(announcement.expires_at).getTime() <= Date.now() : false;
            return (
              <article key={announcement.id} className="rounded-md border border-ink/10 p-3">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="font-semibold text-ink">{announcement.title}</h3>
                      <span className={`rounded-full px-2 py-0.5 text-xs ${announcement.level === "IMPORTANT" ? "bg-chili/10 text-chili" : "bg-mint text-leaf"}`}>
                        {announcement.level === "IMPORTANT" ? "重要" : "普通"}
                      </span>
                      {expired && <span className="rounded-full bg-ink/5 px-2 py-0.5 text-xs text-soy">已失效</span>}
                    </div>
                    <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-soy">{announcement.content}</p>
                    <p className="mt-2 text-xs text-soy">
                      {announcement.created_by_email} · {new Date(announcement.published_at).toLocaleString("zh-CN")}
                      {announcement.expires_at ? ` · 失效于 ${new Date(announcement.expires_at).toLocaleString("zh-CN")}` : " · 长期有效"}
                    </p>
                  </div>
                  <button type="button" className="btn btn-ghost text-chili" disabled={working} onClick={() => remove(announcement)}>
                    <Trash2 size={14} />删除
                  </button>
                </div>
              </article>
            );
          })}
          {!announcements.length && <p className="py-8 text-center text-sm text-soy">暂无公告</p>}
        </div>
      </section>
    </div>
  );
}

function UserPanel({ users, onDone }: { users: User[]; onDone: () => Promise<void> }) {
  const [workingId, setWorkingId] = useState<number | null>(null);
  const [message, setMessage] = useState("");

  async function toggleBlacklist(user: User) {
    const action = user.is_blacklisted ? "移出黑名单" : "拉入黑名单";
    if (!window.confirm(`确认将用户 ${user.display_name ?? user.email} ${action}？${user.is_blacklisted ? "" : "该用户的现有登录会立即失效。"}`)) return;
    setWorkingId(user.id);
    setMessage("");
    try {
      if (user.is_blacklisted) await api.admin.removeUserFromBlacklist(user.id);
      else await api.admin.blacklistUser(user.id);
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "黑名单状态更新失败");
    } finally {
      setWorkingId(null);
    }
  }

  async function toggleMute(user: User) {
    const action = user.is_muted ? "解除禁言" : "禁言";
    if (!window.confirm(`确认${action}用户 ${user.display_name ?? user.email}？`)) return;
    setWorkingId(user.id);
    setMessage("");
    try {
      if (user.is_muted) await api.admin.unmuteUser(user.id);
      else await api.admin.muteUser(user.id);
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "禁言状态更新失败");
    } finally {
      setWorkingId(null);
    }
  }

  return (
    <section className="panel">
      <div className="mb-3 flex items-center gap-2">
        <Users size={18} className="text-leaf" />
        <h2 className="text-lg font-semibold text-ink">普通用户</h2>
      </div>
      <p className="mb-3 text-sm text-soy">黑名单用户不能登录；禁言用户仍可浏览和点赞，但不能发布评论、回复或评论图片。</p>
      <div className="space-y-2">
        {users.map((user) => (
          <div key={user.id} className="flex items-center justify-between gap-3 rounded-md bg-mint/45 p-3 text-sm">
            <div>
              <p className="font-medium text-ink">{user.display_name ?? user.email}</p>
              <p className="text-soy">{user.email}</p>
              <div className="mt-1 flex flex-wrap gap-1 text-xs">
                {user.is_blacklisted && <span className="rounded-full bg-chili/10 px-2 py-0.5 text-chili">黑名单</span>}
                {user.is_muted && <span className="rounded-full bg-ink/10 px-2 py-0.5 text-ink">已禁言</span>}
                {!user.is_blacklisted && !user.is_muted && <span className="rounded-full bg-mint px-2 py-0.5 text-leaf">正常</span>}
              </div>
            </div>
            <div className="flex flex-wrap gap-1">
              <button className="btn btn-ghost" disabled={workingId === user.id} onClick={() => toggleMute(user)}>
                {user.is_muted ? "解除禁言" : "禁言"}
              </button>
              <button className={`btn btn-ghost ${user.is_blacklisted ? "text-leaf" : "text-chili"}`} disabled={workingId === user.id} onClick={() => toggleBlacklist(user)}>
                {user.is_blacklisted ? "移出黑名单" : "拉入黑名单"}
              </button>
            </div>
          </div>
        ))}
      </div>
      {message && <p className="mt-3 text-sm text-chili">{message}</p>}
    </section>
  );
}

function AdminPanel({ admins, me, canManage, onDone }: { admins: User[]; me: User; canManage: boolean; onDone: () => Promise<void> }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [working, setWorking] = useState(false);
  const [message, setMessage] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!email.trim() || password.length < 8 || working) return;
    setWorking(true);
    setMessage("");
    try {
      await api.admin.createAdmin({ email: email.trim(), password, role: "ADMIN" });
      setEmail("");
      setPassword("");
      setMessage("基本管理员创建成功");
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "管理员创建失败");
    } finally {
      setWorking(false);
    }
  }

  async function toggleAdmin(admin: User) {
    if (!canManage || admin.role === "SUPER_ADMIN") return;
    const action = admin.is_active ? "停用" : "启用";
    if (!window.confirm(`确认${action}管理员 ${admin.email}？`)) return;
    setWorking(true);
    try {
      await api.admin.updateAdmin(admin.id, { is_active: !admin.is_active });
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "管理员状态更新失败");
    } finally {
      setWorking(false);
    }
  }

  async function transfer(admin: User) {
    if (!canManage || admin.role !== "ADMIN") return;
    if (!window.confirm(`确认把超级管理员权限转让给 ${admin.email}？转让后你将变为基本管理员。`)) return;
    setWorking(true);
    try {
      await api.admin.transferSuperAdmin(admin.id);
      setMessage("超级管理员权限已转让");
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "权限转让失败");
    } finally {
      setWorking(false);
    }
  }

  async function remove(admin: User) {
    if (!canManage || admin.role !== "ADMIN") return;
    if (!window.confirm(`确认删除基本管理员 ${admin.email}？`)) return;
    setWorking(true);
    try {
      await api.admin.deleteAdmin(admin.id);
      await onDone();
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : "管理员删除失败");
    } finally {
      setWorking(false);
    }
  }

  return (
    <section className="panel">
      <h2 className="mb-3 text-lg font-semibold text-ink">管理员</h2>
      {canManage ? (
        <form className="mb-4 space-y-2" onSubmit={submit}>
          <input className="field" type="email" required placeholder="管理员邮箱 *" value={email} onChange={(event) => setEmail(event.target.value)} />
          <input className="field" minLength={8} type="password" placeholder="初始密码（至少 8 位）*" value={password} onChange={(event) => setPassword(event.target.value)} />
          <button className="btn btn-primary w-full" disabled={working || !email.trim() || password.length < 8}>{working ? "创建中" : "创建基本管理员"}</button>
          <p className="text-xs text-soy">填写有效邮箱和至少 8 位初始密码后，创建按钮才会启用。</p>
        </form>
      ) : (
        <p className="mb-4 rounded-md bg-mint/45 p-3 text-sm text-soy">基本管理员可以查看管理员列表，但不能新增、停用、删除或转让管理员账号。</p>
      )}
      {message && <p className="mb-3 text-sm text-leaf">{message}</p>}
      <div className="space-y-2">
        {admins.map((admin) => (
          <div key={admin.id} className="flex flex-wrap items-center justify-between gap-2 rounded-md bg-mint/45 p-3 text-sm">
            <div>
              <p className="font-medium text-ink">{admin.display_name ?? admin.email}{admin.id === me.id ? "（当前账号）" : ""}</p>
              <p className="text-soy">{admin.email} · {admin.role === "SUPER_ADMIN" ? "超级管理员" : "基本管理员"} · {admin.is_active ? "启用" : "停用"}</p>
            </div>
            {canManage && admin.role === "ADMIN" && (
              <div className="flex flex-wrap gap-1">
                <button className="btn btn-ghost" type="button" disabled={working} onClick={() => transfer(admin)}><ArrowRightLeft size={14} />转让超级管理员</button>
                <button className="btn btn-ghost" type="button" disabled={working} onClick={() => toggleAdmin(admin)}>{admin.is_active ? "停用" : "启用"}</button>
                <button className="btn btn-ghost text-chili" type="button" disabled={working} onClick={() => remove(admin)}><Trash2 size={14} />删除</button>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

function AuditLogPanel({ logs }: { logs: AuditLog[] }) {
  const actionLabel: Record<string, string> = { POST: "新增/执行", PATCH: "编辑", DELETE: "删除" };
  return (
    <section className="panel">
      <div className="mb-3 flex items-center gap-2">
        <ClipboardList size={18} className="text-leaf" />
        <div>
          <h2 className="text-lg font-semibold text-ink">项目操作日志</h2>
          <p className="text-sm text-soy">记录管理员对管理接口的新增、编辑、删除和权限转让操作，不记录密码或请求正文。</p>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] text-left text-sm">
          <thead className="border-b border-ink/10 text-soy"><tr><th className="py-2">时间</th><th>管理员</th><th>角色</th><th>动作</th><th>资源</th><th>结果</th><th>IP</th></tr></thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} className="border-b border-ink/5">
                <td className="py-3 whitespace-nowrap">{new Date(log.created_at).toLocaleString("zh-CN")}</td>
                <td>{log.actor_email}</td>
                <td>{log.actor_role === "SUPER_ADMIN" ? "超级管理员" : "基本管理员"}</td>
                <td>{actionLabel[log.action] ?? log.action}</td>
                <td className="max-w-[280px] truncate font-mono text-xs" title={log.resource}>{log.resource}</td>
                <td className={log.status_code < 400 ? "text-leaf" : "text-chili"}>{log.status_code}</td>
                <td>{log.ip_address ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!logs.length && <p className="py-8 text-center text-sm text-soy">暂无管理员操作日志</p>}
    </section>
  );
}
