"use client";

import { Nav } from "../../../component/nav.jsx";
import MyselfView from "../../../component/myself.jsx";
import ProtectedLayout from "../../../component/ProtectedLayout.jsx";

export default function MyselfPage() {
  return (
    <ProtectedLayout>
      <Nav />
      <MyselfView />
    </ProtectedLayout>
  );
}
