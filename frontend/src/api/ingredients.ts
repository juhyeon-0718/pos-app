// 식재료 관리 API (사장, F-06). 타입은 schema.ts에서만 가져온다.

import type { components } from "./schema";
import { ownerFetch } from "./ownerFetch";

export type Ingredient = components["schemas"]["Ingredient"];
export type IngredientWrite = components["schemas"]["IngredientWrite"];

export async function listIngredients(token: string): Promise<Ingredient[]> {
  const body = await ownerFetch<components["schemas"]["IngredientListResponse"]>(
    token,
    "/ingredients",
  );
  return body.items ?? [];
}

export const createIngredient = (token: string, data: IngredientWrite) =>
  ownerFetch<Ingredient>(token, "/ingredients", { method: "POST", body: data });

export const updateIngredient = (token: string, id: string, data: IngredientWrite) =>
  ownerFetch<Ingredient>(token, `/ingredients/${encodeURIComponent(id)}`, {
    method: "PATCH",
    body: data,
  });

// 삭제는 is_active=false 비활성화다. 레시피가 참조 중이면 409.
export const deactivateIngredient = (token: string, id: string) =>
  ownerFetch<Ingredient>(token, `/ingredients/${encodeURIComponent(id)}`, { method: "DELETE" });
