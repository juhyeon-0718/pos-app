import { useState, type FormEvent } from "react";
import type { Ingredient } from "../../../api/ingredients";
import { errorMessage } from "../errorMessage";
import { useDeactivateIngredient, useOwnerIngredients, useSaveIngredient } from "../hooks/useOwnerData";

export function IngredientSection() {
  const list = useOwnerIngredients();
  const save = useSaveIngredient();
  const deactivate = useDeactivateIngredient();
  const [editing, setEditing] = useState<Ingredient | null>(null);
  const [name, setName] = useState("");
  const [unit, setUnit] = useState("");
  const [safety, setSafety] = useState("");
  const [lead, setLead] = useState("");
  const [unitPrice, setUnitPrice] = useState("");

  function startEdit(i: Ingredient | null) {
    setEditing(i);
    setName(i?.name ?? "");
    setUnit(i?.unit ?? "");
    setSafety(i?.safety_stock != null ? String(i.safety_stock) : "");
    setLead(i?.lead_time_days != null ? String(i.lead_time_days) : "");
    setUnitPrice(i?.unit_price != null ? String(i.unit_price) : "");
    save.reset();
  }

  const num = (v: string) => (v === "" ? undefined : Number(v));

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    save.mutate(
      {
        id: editing?.id,
        data: {
          name: name.trim(),
          unit: unit.trim(),
          safety_stock: num(safety),
          lead_time_days: num(lead),
          unit_price: num(unitPrice),
        },
      },
      { onSuccess: () => startEdit(null) },
    );
  }

  return (
    <section aria-label="식재료 관리">
      <h2>식재료</h2>
      <form className="owner-form" onSubmit={onSubmit}>
        <label>이름<input value={name} onChange={(e) => setName(e.target.value)} required /></label>
        <label>단위<input value={unit} onChange={(e) => setUnit(e.target.value)} required /></label>
        <label>최소로 남겨둘 양<input type="number" min="0" value={safety} onChange={(e) => setSafety(e.target.value)} /></label>
        <label>주문 후 도착까지 며칠<input type="number" min="0" step="1" value={lead} onChange={(e) => setLead(e.target.value)} /></label>
        <label>단가(원)<input type="number" min="0" value={unitPrice} onChange={(e) => setUnitPrice(e.target.value)} /></label>
        <button type="submit" disabled={save.isPending}>{editing ? "수정 저장" : "식재료 추가"}</button>
        {editing && <button type="button" className="owner-secondary" onClick={() => startEdit(null)}>취소</button>}
        {save.isError && <p role="alert" className="owner-error">{errorMessage(save.error)}</p>}
      </form>

      {list.isLoading && <p>불러오는 중...</p>}
      {list.isError && <p role="alert" className="owner-error">식재료 목록을 불러오지 못했습니다.</p>}
      {list.data && list.data.length === 0 && <p>등록된 식재료가 없습니다. 위에서 추가해 주세요.</p>}
      {deactivate.isError && <p role="alert" className="owner-error">{errorMessage(deactivate.error)}</p>}
      {list.data && list.data.length > 0 && (
        <ul className="owner-list">
          {list.data.map((i) => (
            <li key={i.id}>
              <span className="owner-name">{i.name}</span>
              <span>현재 {i.current_stock}{i.unit}</span>
              <span>최소 {i.safety_stock ?? "-"}</span>
              <span>단가 {i.unit_price?.toLocaleString() ?? "-"}원</span>
              {i.is_active === false && <span>사용 안 함</span>}
              <button type="button" onClick={() => startEdit(i)}>수정</button>
              {i.is_active !== false && (
                <button
                  type="button"
                  className="owner-danger"
                  disabled={deactivate.isPending}
                  onClick={() => window.confirm(`"${i.name}"을(를) 사용 안 함으로 바꿀까요?`) && deactivate.mutate(i.id!)}
                >
                  사용 안 함으로 바꾸기
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
