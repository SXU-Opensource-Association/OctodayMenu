import type { AreaType, Dish, FoodArea, FoodVendor } from "./types.ts";


export type PersonalizeFilters = {
  areaType: AreaType | "ALL";
  keyword: string;
  minPrice: string;
  maxPrice: string;
  tagIds: number[];
  highLike: boolean;
  hasImage: boolean;
};

export type VendorMatch = {
  vendor: FoodVendor;
  area: FoodArea;
  sectionName: string | null;
  matchedDishes: Dish[];
  reasons: string[];
  score: number;
};

export const clearableFilterDefaults: PersonalizeFilters = {
  areaType: "ALL",
  keyword: "",
  minPrice: "",
  maxPrice: "",
  tagIds: [],
  highLike: false,
  hasImage: false
};

export function parsePriceRange(minValue: string, maxValue: string) {
  const pattern = /^\d+(?:\.\d{1,2})?$/;
  const parse = (value: string) => {
    const normalized = value.trim();
    if (!normalized) return null;
    if (!pattern.test(normalized)) return Number.NaN;
    return Number(normalized);
  };
  const min = parse(minValue);
  const max = parse(maxValue);
  if (Number.isNaN(min) || Number.isNaN(max)) {
    return { min: null, max: null, error: "价格不能为负数，且最多保留两位小数" };
  }
  if (min !== null && max !== null && min > max) {
    return { min, max, error: "最低价不能高于最高价" };
  }
  return { min, max, error: null };
}

export function filterVendorResults(areas: FoodArea[], filters: PersonalizeFilters): VendorMatch[] {
  const range = parsePriceRange(filters.minPrice, filters.maxPrice);
  if (range.error) return [];
  const keyword = normalize(filters.keyword);
  const selectedTags = new Set(filters.tagIds);
  const hasPriceFilter = range.min !== null || range.max !== null;

  return flattenVendors(areas)
    .filter((item) => filters.areaType === "ALL" || item.area.area_type === filters.areaType)
    .filter((item) => !filters.highLike || item.vendor.like_count > 0)
    .filter((item) => !filters.hasImage || Boolean(item.vendor.image_url))
    .map((item) => {
      const ownerKeywordMatch =
        !keyword ||
        fieldsMatch(
          [
            item.area.name,
            item.area.description,
            item.area.location,
            item.sectionName,
            item.vendor.name,
            item.vendor.description,
            item.vendor.location_hint
          ],
          keyword
        );
      const matchedDishes = item.vendor.dishes.filter((dish) => {
        const price = dish.price === null ? null : Number(dish.price);
        if (range.min !== null && (price === null || price < range.min)) return false;
        if (range.max !== null && (price === null || price > range.max)) return false;
        if (selectedTags.size > 0 && !dish.tags.some((tag) => selectedTags.has(tag.id))) return false;
        if (keyword && !ownerKeywordMatch && !dishMatchesKeyword(dish, keyword)) return false;
        return true;
      });

      const requiresDishMatch = filters.tagIds.length > 0 || hasPriceFilter || (keyword.length > 0 && !ownerKeywordMatch);
      if ((keyword && !ownerKeywordMatch && matchedDishes.length === 0) || (requiresDishMatch && matchedDishes.length === 0)) {
        return null;
      }
      if (keyword && !ownerKeywordMatch && !item.vendor.dishes.some((dish) => dishMatchesKeyword(dish, keyword))) {
        return null;
      }

      const reasons = [
        ...(keyword ? ["命中关键词"] : []),
        ...(filters.tagIds.length ? ["命中标签"] : []),
        ...(hasPriceFilter ? ["价格符合"] : []),
        ...(filters.highLike ? ["高赞店铺"] : []),
        ...(filters.hasImage ? ["有实景图"] : [])
      ];
      const score = matchedDishes.length * 10 + item.vendor.like_count * 2 + (item.vendor.image_url ? 4 : 0);
      return { ...item, matchedDishes, reasons, score };
    })
    .filter((item): item is VendorMatch => item !== null)
    .sort((a, b) => b.score - a.score || b.vendor.like_count - a.vendor.like_count);
}

function flattenVendors(areas: FoodArea[]) {
  return areas.flatMap((area) => [
    ...area.vendors.map((vendor) => ({ area, vendor, sectionName: null })),
    ...area.sections.flatMap((section) =>
      section.vendors.map((vendor) => ({ area, vendor, sectionName: section.name }))
    )
  ]);
}

function dishMatchesKeyword(dish: Dish, keyword: string) {
  return (
    fieldsMatch([dish.name, dish.description, dish.price], keyword) ||
    dish.tags.some((tag) => normalize(tag.name).includes(keyword))
  );
}

function fieldsMatch(values: Array<string | null | undefined>, keyword: string) {
  return values.some((value) => normalize(value).includes(keyword));
}

function normalize(value: string | null | undefined) {
  return (value ?? "").trim().toLowerCase();
}
