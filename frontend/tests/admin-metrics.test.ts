import assert from "node:assert/strict";
import test from "node:test";

import { calculateAdminMetrics } from "../lib/admin-metrics.ts";
import type { FoodArea } from "../lib/types.ts";


test("calculateAdminMetrics reports release readiness gaps", () => {
  const areas = [
    {
      id: 1,
      area_type: "CANTEEN",
      name: "餐厅",
      is_active: true,
      sections: [
        {
          id: 1,
          is_active: true,
          vendors: [
            {
              id: 1,
              is_active: true,
              image_url: null,
              dishes: [
                { id: 1, is_available: true, price: "12.00" },
                { id: 2, is_available: true, price: null }
              ]
            },
            { id: 2, is_active: true, image_url: "/vendor.jpg", dishes: [] }
          ]
        }
      ],
      vendors: []
    },
    {
      id: 2,
      area_type: "CUSTOM_AREA",
      name: "停用地点",
      is_active: false,
      sections: [],
      vendors: [{ id: 3, is_active: true, image_url: null, dishes: [{ id: 3, is_available: true, price: "8.00" }] }]
    }
  ] as unknown as FoodArea[];

  assert.deepEqual(calculateAdminMetrics(areas), {
    activeAreaCount: 1,
    activeVendorCount: 2,
    drawableDishCount: 2,
    emptyVendorCount: 1,
    missingVendorImageCount: 1,
    missingDishPriceCount: 1
  });
});
