import { useQuery } from "@tanstack/react-query";
import { fetchMenusAsStaff, type Menu } from "../../../api/menus";
import { useAuthStore } from "../../../hooks/useAuthStore";

export function useStaffMenus() {
  const accessToken = useAuthStore((s) => s.accessToken);

  return useQuery<Menu[]>({
    queryKey: ["menus", "staff"],
    queryFn: () => fetchMenusAsStaff(accessToken as string),
    enabled: Boolean(accessToken),
  });
}
