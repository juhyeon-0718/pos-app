import { useState, type FormEvent } from "react";
import type { Ingredient } from "../../../api/ingredients";
import { errorText } from "../errorMessage";
import { useDeactivateIngredient, useOwnerIngredients, useSaveIngredient } from "../hooks/useOwnerData";
import { ErrorBanner } from "./ErrorBanner";

export function IngredientSection() {
  const list = useOwnerIngredients();
  const save = useSaveIngredient();
  const pause = useDeactivateIngredient();
  const [editing, setEditing] = useState<Ingredient | null>(null);
  const [name, setName] = useState("");
  const [unit, setUnit] = useState("");
  const [safety, setSafety] = useState("");
  const [lead, setLead] = useState("");
  const [unitPrice, setUnitPrice] = useState("");
  const [pauseName, setPauseName] = useState("");

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
        data: { name: name.trim(), unit: unit.trim(), safety_stock: num(safety), lead_time_days: num(lead), unit_price: num(unitPrice) },
      },
      { onSuccess: () => startEdit(null) },
    );
  }

  function confirmPause(i: Ingredient) {
    const msg = `"${i.name}"을(를) 사용중지로 바꿀까요? 발주 추천에서 빠져요. 재고 기록과 지난 분석 데이터는 그대로 남아요.`;
    if (window.confirm(msg)) {
      setPauseName(i.name ?? "");
      pause.mutate(i.id!);
    }
  }

  return (
    <section aria-label="식재료 관리">
      <h2>식재료 관리</h2>
      <p className="owner-help">식재료의 최소로 남겨둘 양, 주문 후 도착까지 며칠, 단가를 관리해요.</p>
      <form className="owner-form" onSubmit={onSubmit}>
        <label>식재료 이름 *<input value={name} maxLength={50} placeholder="예: 돼지고기(앞다리)" onChange={(e) => setName(e.target.value)} required /></label>
        <label>단위 *<input value={unit} placeholder="예: kg, 개" onChange={(e) => setUnit(e.target.value)} required /></label>
        <label>최소로 남겨둘 양<input type="number" min="0" value={safety} onChange={(e) => setSafety(e.target.value)} /></label>
        <label>주문 후 도착까지 며칠<input type="number" min="0" step="1" value={lead} onChange={(e) => setLead(e.target.value)} /></label>
        <label>단가 (원)<input type="number" min="0" value={unitPrice} onChange={(e) => setUnitPrice(e.target.value)} /></label>
        <button type="submit" disabled={save.isPending}>{save.isPending ? "저장 중…" : editing ? "저장" : "식재료 추가"}</button>
        {editing && <button type="button" className="owner-secondary" onClick={() => startEdit(null)} disabled={save.isPending}>취소</button>}
        {save.isError && <ErrorBanner text={errorText(save.error, "ingredient-save")} />}
      </form>

      {list.isLoading && <p className="owner-loading" aria-busy="true">식재료를 불러오는 중이에요…</p>}
      {list.isError && (
        <div role="alert" className="owner-banner">
          <strong>⚠ 식재료 목록을 불러오지 못했어요.</strong>
          <span>네트워크 상태를 확인하고 다시 시도해 주세요.</span>
          <button type="button" className="owner-secondary" onClick={() => list.refetch()}>다시 시도</button>
        </div>
      )}
      {list.data && list.data.length === 0 && (
        <div className="owner-empty">
          <h3>아직 등록한 식재료가 없어요</h3>
          <p>위에서 식재료를 추가해 주세요.</p>
        </div>
      )}
      {pause.isError && <ErrorBanner text={errorText(pause.error, "ingredient-pause", pauseName)} />}
      {list.data && list.data.length > 0 && (
        <ul className="owner-list">
          {list.data.map((i) => {
            const off = i.is_active === false;
            return (
              <li key={i.id} className={off ? "owner-inactive" : undefined}>
                <span className="owner-name" title={i.name}>{i.name}</span>
                <span>현재 {i.current_stock}{i.unit}</span>
                <span>최소 {i.safety_stock ?? "-"}</span>
                <span>도착까지 {i.lead_time_days != null ? `${i.lead_time_days}일` : "-"}</span>
                <span>단가 {i.unit_price?.toLocaleString() ?? "-"}원</span>
                <span className={`owner-badge ${off ? "owner-badge-inactive" : "owner-badge-active"}`}>
                  {off ? "⊘ 사용중지" : "✓ 사용중"}
                </span>
                <button type="button" className="owner-secondary" aria-label={`${i.name} 수정`} onClick={() => startEdit(i)}>수정</button>
                {!off && (
                  <button type="button" className="owner-danger" aria-label={`${i.name} 사용중지`} disabled={pause.isPending} onClick={() => confirmPause(i)}>
                    사용중지
                  </button>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
