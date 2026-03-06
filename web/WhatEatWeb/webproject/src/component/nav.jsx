"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter, usePathname } from "next/navigation";

export function Nav() {
  const router = useRouter();
  const pathname = usePathname();
  const [canteenOpen, setCanteenOpen] = useState(false);
  const canteenWrapRef = useRef(null);

  useEffect(() => {
    function onDocMouseDown(e) {
      if (!canteenWrapRef.current) return;
      if (!canteenWrapRef.current.contains(e.target)) setCanteenOpen(false);
    }

    function onDocKeyDown(e) {
      if (e.key === "Escape") setCanteenOpen(false);
    }

    document.addEventListener("mousedown", onDocMouseDown);
    document.addEventListener("keydown", onDocKeyDown);
    return () => {
      document.removeEventListener("mousedown", onDocMouseDown);
      document.removeEventListener("keydown", onDocKeyDown);
    };
  }, []);

  const handleRestaurantClick = (restaurantName) => {
    router.push(`/view/restaurant?name=${encodeURIComponent(restaurantName)}`);
    setCanteenOpen(false);
  };

  return (
    <nav className="nav" aria-label="主导航">
      <div className="row">
        <button
          type="button"
          className="itemBtn"
          onClick={() => router.push("/view/home")}
        >
          首页
        </button>

        <div className="dropdown" ref={canteenWrapRef}>
          <button
            type="button"
            className="itemBtn"
            aria-haspopup="menu"
            aria-expanded={canteenOpen}
            onClick={() => setCanteenOpen((v) => !v)}
          >
            食堂
          </button>

          <ul
            className="menu"
            role="menu"
            data-open={canteenOpen ? "true" : "false"}
          >
            <li role="none">
              <button
                type="button"
                role="menuitem"
                className="menuItem"
                onClick={() => handleRestaurantClick("令德餐厅")}
              >
                令德餐厅
              </button>
            </li>
            <li role="none">
              <button
                type="button"
                role="menuitem"
                className="menuItem"
                onClick={() => handleRestaurantClick("令德二楼文化餐厅")}
              >
                令德二楼文化餐厅
              </button>
            </li>
            <li role="none">
              <button
                type="button"
                role="menuitem"
                className="menuItem"
                onClick={() => handleRestaurantClick("文瀛餐厅")}
              >
                文瀛餐厅
              </button>
            </li>
            <li role="none">
              <button
                type="button"
                role="menuitem"
                className="menuItem"
                onClick={() => handleRestaurantClick("许西餐厅")}
              >
                许西餐厅
              </button>
            </li>
            <li role="none">
              <button
                type="button"
                role="menuitem"
                className="menuItem"
                onClick={() => handleRestaurantClick("教职工餐厅")}
              >
                教职工餐厅
              </button>
            </li>
          </ul>
        </div>

        <button
          type="button"
          className="itemBtn"
          onClick={() => router.push("/view/myself")}
        >
          个人中心
        </button>
      </div>
    </nav>
  );
}