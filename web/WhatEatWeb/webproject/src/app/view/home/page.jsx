"use client";

import { Nav } from "../../../component/nav.jsx";
import HomeView from "../../../component/home.jsx";
import ProtectedLayout from "../../../component/ProtectedLayout.jsx";

export default function HomePage() {
  return (
    <ProtectedLayout>
      <Nav />
      <HomeView />
    </ProtectedLayout>
  );
}
