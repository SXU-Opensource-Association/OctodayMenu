import { RestaurantDetail } from "@/components/restaurant-detail";

export default async function RestaurantPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <RestaurantDetail restaurantId={Number(id)} />;
}
