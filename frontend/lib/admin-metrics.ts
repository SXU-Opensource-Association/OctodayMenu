import type { FoodArea, FoodVendor } from "./types.ts";


export type AdminMetrics = {
  activeAreaCount: number;
  activeVendorCount: number;
  drawableDishCount: number;
  emptyVendorCount: number;
  missingVendorImageCount: number;
  missingDishPriceCount: number;
};

export function calculateAdminMetrics(areas: FoodArea[]): AdminMetrics {
  const activeAreas = areas.filter((area) => area.is_active);
  const activeVendors = activeAreas.flatMap((area) => collectActiveVendors(area));
  return {
    activeAreaCount: activeAreas.length,
    activeVendorCount: activeVendors.length,
    drawableDishCount: activeVendors.reduce(
      (total, vendor) => total + vendor.dishes.filter((dish) => dish.is_available).length,
      0
    ),
    emptyVendorCount: activeVendors.filter((vendor) => vendor.dishes.length === 0).length,
    missingVendorImageCount: activeVendors.filter((vendor) => !vendor.image_url).length,
    missingDishPriceCount: activeVendors.reduce(
      (total, vendor) => total + vendor.dishes.filter((dish) => dish.price === null).length,
      0
    )
  };
}

function collectActiveVendors(area: FoodArea): FoodVendor[] {
  const direct = area.vendors.filter((vendor) => vendor.is_active);
  const sectionVendors = area.sections
    .filter((section) => section.is_active)
    .flatMap((section) => section.vendors.filter((vendor) => vendor.is_active));
  return [...direct, ...sectionVendors];
}
