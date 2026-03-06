"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Nav } from "../../../component/nav.jsx";
import RestaurantView from "../../../component/restaurant.jsx";
import ProtectedLayout from "../../../component/ProtectedLayout.jsx";

export default function RestaurantPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const restaurantName = searchParams.get("name") || "令德餐厅";

  return (
    <ProtectedLayout>
      <Nav />
      <RestaurantView restaurantName={restaurantName} />
    </ProtectedLayout>
  );
}
