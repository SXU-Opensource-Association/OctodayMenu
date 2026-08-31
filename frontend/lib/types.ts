export type Role = "USER" | "ADMIN" | "SUPER_ADMIN";
export type TagCategory = "basic" | "taste";
export type AreaType = "CANTEEN" | "SNACK_STREET" | "CUSTOM_AREA";

export type User = {
  id: number;
  email: string;
  display_name: string | null;
  role: Role;
  is_active: boolean;
  is_blacklisted: boolean;
  is_muted: boolean;
};

export type Announcement = {
  id: number;
  title: string;
  content: string;
  level: "INFO" | "IMPORTANT";
  created_by_id: number | null;
  created_by_email: string;
  published_at: string;
  expires_at: string | null;
};

export type Tag = {
  id: number;
  name: string;
  category: TagCategory;
  is_active: boolean;
};

export type Dish = {
  id: number;
  vendor_id: number;
  stall_id: number;
  name: string;
  description: string | null;
  price: string | null;
  image_url: string | null;
  is_available: boolean;
  like_count: number;
  comment_count: number;
  tags: Tag[];
};

export type FoodVendor = {
  id: number;
  area_id: number;
  section_id: number | null;
  floor_id: number;
  name: string;
  description: string | null;
  location_hint: string | null;
  image_url: string | null;
  is_active: boolean;
  like_count: number;
  comment_count: number;
  liked_by_me: boolean;
  dishes: Dish[];
};

export type FoodSection = {
  id: number;
  area_id: number;
  restaurant_id: number;
  name: string;
  level: number;
  description: string | null;
  is_active: boolean;
  vendors: FoodVendor[];
  stalls: FoodVendor[];
};

export type FoodAreaSummary = {
  id: number;
  area_type: AreaType;
  name: string;
  description: string | null;
  location: string | null;
  address: string | null;
  is_active: boolean;
  floor_count: number;
  section_count: number;
  stall_count: number;
  vendor_count: number;
  dish_count: number;
};

export type FoodArea = {
  id: number;
  area_type: AreaType;
  name: string;
  description: string | null;
  location: string | null;
  address: string | null;
  is_active: boolean;
  sections: FoodSection[];
  floors: FoodSection[];
  vendors: FoodVendor[];
};

export type Stall = FoodVendor;
export type Floor = FoodSection;
export type RestaurantSummary = FoodAreaSummary;
export type Restaurant = FoodArea;

export type DailyDraw = {
  id: number;
  draw_date: string;
  dish: Dish;
  food_area: FoodAreaSummary;
  section: FoodSection | null;
  vendor: FoodVendor;
  restaurant: RestaurantSummary;
  stall: Stall;
};

export type AuthResponse = {
  access_token: string;
  token_type: "bearer";
  user: User;
};

export type AdminMfaChallengeResponse = {
  mfa_required: true;
  message: string;
  dev_code?: string | null;
};

export type LoginResponse = AuthResponse | AdminMfaChallengeResponse;

export type AuditLog = {
  id: number;
  actor_id: number | null;
  actor_email: string;
  actor_role: string;
  action: string;
  resource: string;
  status_code: number;
  ip_address: string | null;
  created_at: string;
};

export type EmailVerificationResponse = {
  status: "sent";
  dev_code?: string | null;
};

export type LikeToggleResponse = {
  liked: boolean;
  like_count: number;
};

export type Comment = {
  id: number;
  vendor_id: number;
  parent_id: number | null;
  content: string;
  image_url: string | null;
  like_count: number;
  reply_count: number;
  liked_by_me: boolean;
  author: User;
  created_at: string;
  replies: Comment[];
};

export type ImportErrorItem = {
  row: number;
  message: string;
};

export type ImportRowResult = {
  row: number;
  status: "created" | "updated" | "skipped" | "error";
  message: string;
};

export type ImportResult = {
  dry_run: boolean;
  created_count: number;
  updated_count: number;
  skipped_count: number;
  error_count: number;
  errors: ImportErrorItem[];
  rows: ImportRowResult[];
};
