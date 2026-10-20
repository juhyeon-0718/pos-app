import { useState, type FormEvent } from "react";
import type { Menu } from "../../../api/menus";
import { errorText } from "../errorMessage";
import { useDeleteMenu, useOwnerMenus, useSaveMenu } from "../hooks/useOwnerData";
import { ErrorBanner } from "./ErrorBanner";

export function MenuSection() {
  const menus = useOwnerMenus();
  const save = useSaveMenu();
  const remove = useDeleteMenu();
  const [editing, setEditing] = useState<Menu | null>(null);
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [category, setCategory] = useState("");
  const [soldOut, setSoldOut] = useState(false);
  const [actionError, setActionError] = useState<unknown>(null);

  function startEdit(m: Menu | null) {
    setEditing(m);
    setName(m?.name ?? "");
    setPrice(m?.price != null ? String(m.price) : "");
    setCategory(m?.category ?? "");
    setSoldOut(m ? m.is_active === false : false);
    save.reset();
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    save.mutate(
      {
        id: editing?.id,
        data: { name: name.trim(), price: Number(price), category: category.trim() || undefined, is_active: !soldOut },
      },
      { onSuccess: () => startEdit(null) },
    );
  }

  // 일시품절/판매 다시 시작: PATCH는 MenuWrite 전체 본문이 필요하다(명세 §9 요청 3).
  function setSale(m: Menu, active: boolean) {
    setActionError(null);
    save.mutate(
      { id: m.id, data: { name: m.name ?? "", price: m.price ?? 0, category: m.category || undefined, is_active: active } },
      { onError: setActionError },
    );
  }

  function confirmSoldOut(m: Menu) {
    const msg = `"${m.name}"을(를) 일시품절로 바꿀까요? 손님 메뉴판에서 주문할 수 없게 돼요. 언제든 "판매 다시 시작"으로 되돌릴 수 있어요.`;
    if (window.confirm(msg)) setSale(m, false);
  }

  function confirmDelete(m: Menu) {
    const msg = `"${m.name}"을(를) 삭제할까요? 삭제하면 되돌릴 수 없어요.`;
    if (window.confirm(msg)) {
      setActionError(null);
      remove.mutate(m.id!, { onError: setActionError });
    }
  }

  return (
    <section aria-label="메뉴 관리">
      <h2>메뉴 관리</h2>
      <p className="owner-help">손님 주문 화면에 나오는 메뉴와 가격을 관리해요.</p>
      <form className="owner-form" onSubmit={onSubmit}>
        <label>메뉴 이름 *<input value={name} maxLength={50} placeholder="예: 된장찌개" onChange={(e) => setName(e.target.value)} required /></label>
        <label>가격 (원) *<input type="number" min="0" step="1" placeholder="예: 9000" value={price} onChange={(e) => setPrice(e.target.value)} required /></label>
        <label>카테고리<input value={category} placeholder="예: 찌개, 볶음, 밥" onChange={(e) => setCategory(e.target.value)} /></label>
        <label className="owner-check">
          <input type="checkbox" checked={soldOut} onChange={(e) => setSoldOut(e.target.checked)} />
          일시품절
          <span className="owner-help">(체크하면 손님 메뉴판에서 주문할 수 없어요)</span>
        </label>
        <button type="submit" disabled={save.isPending}>{save.isPending ? "저장 중…" : editing ? "저장" : "메뉴 추가"}</button>
        {editing && <button type="button" className="owner-secondary" onClick={() => startEdit(null)} disabled={save.isPending}>취소</button>}
        {save.isError && !actionError && <ErrorBanner text={errorText(save.error, "menu-save")} />}
      </form>

      {menus.isLoading && <p className="owner-loading" aria-busy="true">메뉴를 불러오는 중이에요…</p>}
      {menus.isError && (
        <div role="alert" className="owner-banner">
          <strong>⚠ 메뉴 목록을 불러오지 못했어요.</strong>
          <span>네트워크 상태를 확인하고 다시 시도해 주세요.</span>
          <button type="button" className="owner-secondary" onClick={() => menus.refetch()}>다시 시도</button>
        </div>
      )}
      {menus.data && menus.data.length === 0 && (
        <div className="owner-empty">
          <h3>아직 등록한 메뉴가 없어요</h3>
          <p>첫 메뉴를 추가하면 손님 주문 화면에 바로 나타나요.</p>
        </div>
      )}
      {actionError != null && <ErrorBanner text={errorText(actionError, "menu-action")} />}
      {menus.data && menus.data.length > 0 && (
        <ul className="owner-list">
          {menus.data.map((m) => {
            const off = m.is_active === false;
            return (
              <li key={m.id} className={off ? "owner-inactive" : undefined}>
                <span className="owner-name" title={m.name}>{m.name}</span>
                <span>{m.price?.toLocaleString()}원</span>
                <span>{m.category || "미분류"}</span>
                <span className={`owner-badge ${off ? "owner-badge-inactive" : "owner-badge-active"}`}>
                  {off ? "⊘ 일시품절" : "✓ 판매중"}
                </span>
                <button type="button" className="owner-secondary" aria-label={`${m.name} 수정`} onClick={() => startEdit(m)}>수정</button>
                {off ? (
                  <button type="button" aria-label={`${m.name} 판매 다시 시작`} disabled={save.isPending} onClick={() => setSale(m, true)}>
                    판매 다시 시작
                  </button>
                ) : (
                  <button type="button" className="owner-secondary" aria-label={`${m.name} 일시품절`} disabled={save.isPending} onClick={() => confirmSoldOut(m)}>
                    일시품절
                  </button>
                )}
                <button type="button" className="owner-danger" aria-label={`${m.name} 삭제`} disabled={remove.isPending} onClick={() => confirmDelete(m)}>
                  삭제
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
