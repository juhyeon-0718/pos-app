// GET /menus를 React Query로 감싼다. 메뉴는 자주 바뀌지 않으므로 폴링하지 않는다.

import { useQuery } from "@tanstack/react-query";
import { fetchMenus, type Menu } from "../../../api/menus";

export function useMenus(tableSessionToken: string | null) {
  return useQuery<Menu[]>({
    queryKey: ["menus", tableSessionToken],
    queryFn: () => fetchMenus(tableSessionToken as string),
    enabled: Boolean(tableSessionToken),
  });
}
