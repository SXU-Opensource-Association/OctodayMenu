import type {
  Announcement,
  AuthResponse,
  AuditLog,
  Comment,
  DailyDraw,
  Dish,
  EmailVerificationResponse,
  AreaType,
  FoodArea,
  FoodAreaSummary,
  FoodSection,
  FoodVendor,
  Floor,
  ImportResult,
  LikeToggleResponse,
  Restaurant,
  RestaurantSummary,
  Stall,
  Tag,
  User,
  LoginResponse
} from "./types";
import { notifyAuthChanged } from "./auth-events";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";
const LEGACY_TOKEN_KEY = "sxuwhateat_token";

type RequestOptions = RequestInit & {
  token?: string | null;
};

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export function getStoredToken() {
  return null;
}

export function setStoredToken(_token: string) {
  window.localStorage.removeItem(LEGACY_TOKEN_KEY);
  notifyAuthChanged();
}

export async function clearStoredToken() {
  window.localStorage.removeItem(LEGACY_TOKEN_KEY);
  try {
    await fetch(`${API_BASE_URL}/auth/logout`, { method: "POST", credentials: "same-origin" });
  } finally {
    notifyAuthChanged();
  }
}

export function toMediaUrl(url: string | null | undefined) {
  if (!url) return null;
  if (/^https?:\/\//i.test(url)) return url;
  if (url.startsWith("/uploads") && /^https?:\/\//i.test(API_BASE_URL)) {
    return API_BASE_URL.replace(/\/api$/, "") + url;
  }
  return url;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { token: explicitToken, headers, ...fetchOptions } = options;
  const token = explicitToken;
  const isFormData = typeof FormData !== "undefined" && fetchOptions.body instanceof FormData;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...fetchOptions,
    credentials: "same-origin",
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(headers as Record<string, string> | undefined)
    }
  });

  if (!response.ok) {
    let message = "请求失败";
    try {
      const body = await response.json();
      message = body.detail ?? message;
    } catch {
      message = response.statusText;
    }
    throw new ApiError(response.status, message);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

async function requestBlob(path: string, options: RequestOptions = {}) {
  const { token: explicitToken, headers, ...fetchOptions } = options;
  const token = explicitToken;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...fetchOptions,
    credentials: "same-origin",
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(headers as Record<string, string> | undefined)
    }
  });
  if (!response.ok) {
    throw new ApiError(response.status, response.statusText || "请求失败");
  }
  return response.blob();
}

export const api = {
  sendEmailVerification(payload: { email: string }) {
    return request<EmailVerificationResponse>("/auth/email-verifications", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  register(payload: { email: string; password: string; display_name?: string; verification_code: string }) {
    return request<AuthResponse>("/auth/register", { method: "POST", body: JSON.stringify(payload) });
  },
  login(payload: { email: string; password: string; verification_code?: string }) {
    return request<LoginResponse>("/auth/login", { method: "POST", body: JSON.stringify(payload) });
  },
  me() {
    return request<User>("/auth/me");
  },
  announcements() {
    return request<Announcement[]>("/announcements");
  },
  restaurants() {
    return request<RestaurantSummary[]>("/restaurants");
  },
  restaurant(id: number) {
    return request<Restaurant>(`/restaurants/${id}`);
  },
  foodAreas(params: { area_type?: AreaType } = {}) {
    const search = new URLSearchParams();
    if (params.area_type) search.set("area_type", params.area_type);
    const query = search.toString();
    return request<FoodAreaSummary[]>(`/food-areas${query ? `?${query}` : ""}`);
  },
  foodArea(id: number) {
    return request<FoodArea>(`/food-areas/${id}`);
  },
  tags() {
    return request<Tag[]>("/tags");
  },
  dishes(
    params: {
      restaurant_id?: number;
      area_id?: number;
      area_type?: AreaType;
      tag_ids?: number[];
      min_price?: string;
      max_price?: string;
      keyword?: string;
    } = {}
  ) {
    const search = new URLSearchParams();
    if (params.restaurant_id) search.set("restaurant_id", String(params.restaurant_id));
    if (params.area_id) search.set("area_id", String(params.area_id));
    if (params.area_type) search.set("area_type", params.area_type);
    if (params.min_price) search.set("min_price", params.min_price);
    if (params.max_price) search.set("max_price", params.max_price);
    if (params.keyword) search.set("keyword", params.keyword);
    for (const id of params.tag_ids ?? []) search.append("tag_ids", String(id));
    const query = search.toString();
    return request<Dish[]>(`/dishes${query ? `?${query}` : ""}`);
  },
  todayDraw() {
    return request<DailyDraw>("/draws/today");
  },
  drawToday() {
    return request<DailyDraw>("/draws/today", { method: "POST", body: JSON.stringify({}) });
  },
  toggleVendorLike(vendorId: number) {
    return request<LikeToggleResponse>(`/vendors/${vendorId}/like`, { method: "POST" });
  },
  vendorComments(vendorId: number) {
    return request<Comment[]>(`/vendors/${vendorId}/comments`);
  },
  createVendorComment(vendorId: number, payload: { content: string; image_url?: string }) {
    return request<Comment>(`/vendors/${vendorId}/comments`, { method: "POST", body: JSON.stringify(payload) });
  },
  replyComment(commentId: number, payload: { content: string; image_url?: string }) {
    return request<Comment>(`/comments/${commentId}/replies`, { method: "POST", body: JSON.stringify(payload) });
  },
  toggleCommentLike(commentId: number) {
    return request<LikeToggleResponse>(`/comments/${commentId}/like`, { method: "POST" });
  },
  uploadCommentImage(file: File) {
    const form = new FormData();
    form.append("file", file);
    return request<{ image_url: string }>("/uploads/comment-images", { method: "POST", body: form });
  },
  admin: {
    users() {
      return request<User[]>("/admin/users");
    },
    updateUser(id: number, payload: { display_name?: string; is_active?: boolean }) {
      return request<User>(`/admin/users/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
    },
    blacklistUser(id: number) {
      return request<User>(`/admin/users/${id}/blacklist`, { method: "POST" });
    },
    removeUserFromBlacklist(id: number) {
      return request<User>(`/admin/users/${id}/blacklist`, { method: "DELETE" });
    },
    muteUser(id: number) {
      return request<User>(`/admin/users/${id}/mute`, { method: "POST" });
    },
    unmuteUser(id: number) {
      return request<User>(`/admin/users/${id}/mute`, { method: "DELETE" });
    },
    admins() {
      return request<User[]>("/admin/admins");
    },
    createAdmin(payload: { email: string; password: string; display_name?: string; role?: "ADMIN" | "SUPER_ADMIN" }) {
      return request<User>("/admin/admins", { method: "POST", body: JSON.stringify(payload) });
    },
    updateAdmin(id: number, payload: { display_name?: string; is_active?: boolean }) {
      return request<User>(`/admin/admins/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
    },
    deleteAdmin(id: number) {
      return request<void>(`/admin/admins/${id}`, { method: "DELETE" });
    },
    transferSuperAdmin(id: number) {
      return request<User>(`/admin/admins/${id}/transfer-super-admin`, { method: "POST" });
    },
    foodAreas() {
      return request<FoodArea[]>("/admin/food-areas");
    },
    createFoodArea(payload: { name: string; area_type: AreaType; description?: string; location?: string }) {
      return request<FoodArea>("/admin/food-areas", { method: "POST", body: JSON.stringify(payload) });
    },
    updateFoodArea(id: number, payload: { name?: string; area_type?: AreaType; description?: string; location?: string; is_active?: boolean }) {
      return request<FoodArea>(`/admin/food-areas/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
    },
    deleteFoodArea(id: number) {
      return request<void>(`/admin/food-areas/${id}`, { method: "DELETE" });
    },
    createFoodSection(areaId: number, payload: { name: string; level: number; description?: string }) {
      return request<FoodSection>(`/admin/food-areas/${areaId}/sections`, {
        method: "POST",
        body: JSON.stringify(payload)
      });
    },
    updateFoodSection(id: number, payload: { name?: string; level?: number; description?: string; is_active?: boolean }) {
      return request<FoodSection>(`/admin/sections/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
    },
    deleteFoodSection(id: number) {
      return request<void>(`/admin/sections/${id}`, { method: "DELETE" });
    },
    createDirectVendor(areaId: number, payload: { name: string; description?: string; location_hint?: string; image_url?: string }) {
      return request<FoodVendor>(`/admin/food-areas/${areaId}/vendors`, {
        method: "POST",
        body: JSON.stringify(payload)
      });
    },
    createSectionVendor(sectionId: number, payload: { name: string; description?: string; location_hint?: string; image_url?: string }) {
      return request<FoodVendor>(`/admin/sections/${sectionId}/vendors`, {
        method: "POST",
        body: JSON.stringify(payload)
      });
    },
    updateVendor(id: number, payload: { name?: string; description?: string; location_hint?: string; image_url?: string; is_active?: boolean }) {
      return request<FoodVendor>(`/admin/vendors/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
    },
    deleteVendor(id: number) {
      return request<void>(`/admin/vendors/${id}`, { method: "DELETE" });
    },
    createVendorDish(
      vendorId: number,
      payload: { name: string; description?: string; price?: string; image_url?: string; tag_ids: number[] }
    ) {
      return request<Dish>(`/admin/vendors/${vendorId}/dishes`, { method: "POST", body: JSON.stringify(payload) });
    },
    updateDish(id: number, payload: { name?: string; description?: string; price?: string | null; image_url?: string; is_available?: boolean; tag_ids?: number[] }) {
      return request<Dish>(`/admin/dishes/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
    },
    deleteDish(id: number) {
      return request<void>(`/admin/dishes/${id}`, { method: "DELETE" });
    },
    downloadFoodTemplate() {
      return requestBlob("/admin/import/food-template");
    },
    importFoodData(file: File, dryRun: boolean) {
      const form = new FormData();
      form.append("file", file);
      return request<ImportResult>(`/admin/import/food-data?dry_run=${dryRun ? "true" : "false"}`, {
        method: "POST",
        body: form
      });
    },
    restaurants() {
      return request<Restaurant[]>("/admin/restaurants");
    },
    createRestaurant(payload: { name: string; description?: string; address?: string }) {
      return request<Restaurant>("/admin/restaurants", { method: "POST", body: JSON.stringify(payload) });
    },
    createFloor(restaurantId: number, payload: { name: string; level: number; description?: string }) {
      return request<Floor>(`/admin/restaurants/${restaurantId}/floors`, {
        method: "POST",
        body: JSON.stringify(payload)
      });
    },
    createStall(floorId: number, payload: { name: string; description?: string; location_hint?: string; image_url?: string }) {
      return request<Stall>(`/admin/floors/${floorId}/stalls`, {
        method: "POST",
        body: JSON.stringify(payload)
      });
    },
    createTag(payload: { name: string; category: "basic" | "taste" }) {
      return request<Tag>("/admin/tags", { method: "POST", body: JSON.stringify(payload) });
    },
    tags() {
      return request<Tag[]>("/admin/tags");
    },
    updateTag(id: number, payload: { name?: string; category?: "basic" | "taste"; is_active?: boolean }) {
      return request<Tag>(`/admin/tags/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
    },
    deleteTag(id: number) {
      return request<void>(`/admin/tags/${id}`, { method: "DELETE" });
    },
    uploadImage(file: File) {
      const form = new FormData();
      form.append("file", file);
      return request<{ image_url: string }>("/admin/uploads/images", { method: "POST", body: form });
    },
    auditLogs(limit = 200) {
      return request<AuditLog[]>(`/admin/audit-logs?limit=${limit}`);
    },
    announcements() {
      return request<Announcement[]>("/admin/announcements");
    },
    publishAnnouncement(payload: { title: string; content: string; level: "INFO" | "IMPORTANT"; expires_at?: string }) {
      return request<Announcement>("/admin/announcements", { method: "POST", body: JSON.stringify(payload) });
    },
    deleteAnnouncement(id: number) {
      return request<void>(`/admin/announcements/${id}`, { method: "DELETE" });
    },
    createDish(
      stallId: number,
      payload: { name: string; description?: string; price?: string; image_url?: string; tag_ids: number[] }
    ) {
      return request<Dish>(`/admin/stalls/${stallId}/dishes`, { method: "POST", body: JSON.stringify(payload) });
    }
  }
};
