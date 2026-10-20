import { useState } from "react";
import { LoginPage } from "../auth/LoginPage";
import { useAuthStore } from "../../hooks/useAuthStore";
import { IngredientSection } from "./components/IngredientSection";
import { MenuSection } from "./components/MenuSection";
import "./owner.css";

type Tab = "menus" | "ingredients";

export function OwnerPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const role = useAuthStore((s) => s.role);
  const [tab, setTab] = useState<Tab>("menus");

  if (!accessToken) return <LoginPage />;
  if (role !== "owner") {
    return (
      <main className="owner-page">
        <p role="alert" className="owner-error">사장 계정으로 로그인해 주세요.</p>
      </main>
    );
  }

  return (
    <main className="owner-page">
      <h1>사장 관리</h1>
      <nav className="owner-tabs" aria-label="관리 메뉴">
        <button type="button" aria-pressed={tab === "menus"} onClick={() => setTab("menus")}>메뉴</button>
        <button type="button" aria-pressed={tab === "ingredients"} onClick={() => setTab("ingredients")}>식재료</button>
      </nav>
      {tab === "menus" && <MenuSection />}
      {tab === "ingredients" && <IngredientSection />}
    </main>
  );
}
