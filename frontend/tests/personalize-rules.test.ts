import assert from "node:assert/strict";
import test from "node:test";

import { filterVendorResults, parsePriceRange } from "../lib/personalize-rules.ts";
import type { FoodArea } from "../lib/types.ts";


const areas = [
  {
    id: 1,
    area_type: "CANTEEN",
    name: "文瀛餐厅",
    description: "校内餐厅",
    location: "南区",
    address: "南区",
    is_active: true,
    floors: [],
    vendors: [],
    sections: [
      {
        id: 1,
        area_id: 1,
        restaurant_id: 1,
        name: "一层",
        level: 1,
        description: null,
        is_active: true,
        stalls: [],
        vendors: [
          {
            id: 1,
            area_id: 1,
            section_id: 1,
            floor_id: 1,
            name: "山西面馆",
            description: "刀削面",
            location_hint: "东侧",
            image_url: "/uploads/vendor.jpg",
            is_active: true,
            like_count: 3,
            comment_count: 0,
            liked_by_me: false,
            dishes: [
              {
                id: 1,
                vendor_id: 1,
                stall_id: 1,
                name: "油泼刀削面",
                description: "香辣筋道",
                price: "12.50",
                image_url: null,
                is_available: true,
                like_count: 0,
                comment_count: 0,
                tags: [{ id: 1, name: "面", category: "basic", is_active: true }]
              },
              {
                id: 2,
                vendor_id: 1,
                stall_id: 1,
                name: "清汤牛肉面",
                description: "清淡鲜香",
                price: "15.00",
                image_url: null,
                is_available: true,
                like_count: 0,
                comment_count: 0,
                tags: [{ id: 2, name: "清淡", category: "taste", is_active: true }]
              }
            ]
          }
        ]
      }
    ]
  }
] as FoodArea[];


test("parsePriceRange rejects invalid numbers and reversed ranges", () => {
  assert.equal(parsePriceRange("-1", "").error, "价格不能为负数，且最多保留两位小数");
  assert.equal(parsePriceRange("", "1.234").error, "价格不能为负数，且最多保留两位小数");
  assert.equal(parsePriceRange("100", "1").error, "最低价不能高于最高价");
  assert.deepEqual(parsePriceRange("10", "20.50"), { min: 10, max: 20.5, error: null });
});


test("unknown keyword strictly removes every vendor", () => {
  const results = filterVendorResults(areas, {
    areaType: "ALL",
    keyword: "披萨",
    minPrice: "",
    maxPrice: "",
    tagIds: [],
    highLike: false,
    hasImage: false
  });

  assert.equal(results.length, 0);
});


test("dish keyword returns only matching dishes and reasons", () => {
  const results = filterVendorResults(areas, {
    areaType: "ALL",
    keyword: "油泼",
    minPrice: "10",
    maxPrice: "13",
    tagIds: [1],
    highLike: true,
    hasImage: true
  });

  assert.equal(results.length, 1);
  assert.deepEqual(results[0].matchedDishes.map((dish) => dish.name), ["油泼刀削面"]);
  assert.deepEqual(results[0].reasons, ["命中关键词", "命中标签", "价格符合", "高赞店铺", "有实景图"]);
});
