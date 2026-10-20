import { useState, type FormEvent } from "react";
import type { Menu } from "../../../api/menus";
import { errorMessage } from "../errorMessage";
import { useDeleteMenu, useOwnerMenus, useSaveMenu } from "../hooks/useOwnerData";

export function MenuSection() {
  const menus = useOwnerMenus();
  const save = useSaveMenu();
  const remove = useDeleteMenu();
  const [editing, setEditing] = useState<Menu | null>(null);
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [category, setCategory] = useState("");
  const [isActive, setIsActive] = useState(true);

  function startEdit(m: Menu | null) {
    setEditing(m);
    setName(m?.name ?? "");
    setPrice(m?.price != null ? String(m.price) : "");
    setCategory(m?.category ?? "");
    setIsActive(m?.is_active ?? true);
    save.reset();
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    save.mutate(
      {
        id: editing?.id,
        data: {
          name: name.trim(),
          price: Number(price),
          category: category.trim() || undefined,
          is_active: isActive,
        },
      },
      { onSuccess: () => startEdit(null) },
    );
  }

  return (
    <section aria-label="메뉴 관리">
      <h2>메뉴·가격</h2>
      <form className="owner-form" onSubmit={onSubmit}>
        <label>이름<input value={name} onChange={(e) => setName(e.target.value)} required /></label>
        <label>가격(원)<input type="number" min="0" value={price} onChange={(e) => setPrice(e.target.value)} required /></label>
        <label>분류<input value={category} onChange={(e) => setCategory(e.target.value)} /></label>
        <label className="owner-check">
          <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
          지금 판매하나요?
        </label>
        <button type="submit" disabled={save.isPending}>{editing ? "수정 저장" : "메뉴 추가"}</button>
        {editing && <button type="button" className="owner-secondary" onClick={() => startEdit(null)}>취소</button>}
        {save.isError && <p role="alert" className="owner-error">{errorMessage(save.error)}</p>}
      </form>

      {menus.isLoading && <p>불러오는 중...</p>}
      {menus.isError && <p role="alert" className="owner-error">메뉴 목록을 불러오지 못했습니다.</p>}
      {menus.data && menus.data.length === 0 && <p>등록된 메뉴가 없습니다. 위에서 첫 메뉴를 추가해 주세요.</p>}
      {remove.isError && <p role="alert" className="owner-error">{errorMessage(remove.error)}</p>}
      {menus.data && menus.data.length > 0 && (
        <ul className="owner-list">
          {menus.data.map((m) => (
            <li key={m.id}>
              <span className="owner-name">{m.name}</span>
              <span>{m.price?.toLocaleString()}원</span>
              <span>{m.category}</span>
              <span>{m.is_active === false ? "비활성" : "판매중"}</span>
              <button type="button" onClick={() => startEdit(m)}>수정</button>
              <button
                type="button"
                className="owner-danger"
                disabled={remove.isPending}
                onClick={() => window.confirm(`"${m.name}" 메뉴를 삭제(비활성화)할까요?`) && remove.mutate(m.id!)}
              >
                삭제
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
