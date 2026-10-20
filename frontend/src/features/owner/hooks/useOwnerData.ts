import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuthStore } from "../../../hooks/useAuthStore";
import * as menusApi from "../../../api/menus";
import * as ingApi from "../../../api/ingredients";

function useToken(): string {
  return useAuthStore((s) => s.accessToken) ?? "";
}

export function useOwnerMenus() {
  const token = useToken();
  return useQuery({ queryKey: ["owner", "menus"], queryFn: () => menusApi.listMenusAsOwner(token), enabled: !!token });
}

export function useSaveMenu() {
  const token = useToken();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (v: { id?: string; data: menusApi.MenuWrite }) =>
      v.id ? menusApi.updateMenu(token, v.id, v.data) : menusApi.createMenu(token, v.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["owner", "menus"] }),
  });
}

export function useDeleteMenu() {
  const token = useToken();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => menusApi.deleteMenu(token, id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["owner", "menus"] }),
  });
}

export function useOwnerIngredients() {
  const token = useToken();
  return useQuery({ queryKey: ["owner", "ingredients"], queryFn: () => ingApi.listIngredients(token), enabled: !!token });
}

export function useSaveIngredient() {
  const token = useToken();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (v: { id?: string; data: ingApi.IngredientWrite }) =>
      v.id ? ingApi.updateIngredient(token, v.id, v.data) : ingApi.createIngredient(token, v.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["owner", "ingredients"] }),
  });
}

export function useDeactivateIngredient() {
  const token = useToken();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => ingApi.deactivateIngredient(token, id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["owner", "ingredients"] }),
  });
}
