// 메뉴 목록. 모바일 터치 타겟 기준(각 행 48px 이상)으로 "담기" 버튼을 둔다.

import type { Menu } from "../../../api/menus";
import { useCartStore } from "../store/cartStore";

export function MenuList({ menus }: { menus: Menu[] }) {
  const addItem = useCartStore((s) => s.addItem);

  const activeMenus = menus.filter((m) => m.is_active !== false);

  if (activeMenus.length === 0) {
    return <p className="menu-empty">현재 주문 가능한 메뉴가 없습니다.</p>;
  }

  return (
    <ul className="menu-list">
      {activeMenus.map((menu) => (
        <li key={menu.id} className="menu-row">
          <div className="menu-info">
            <span className="menu-name">{menu.name}</span>
            <span className="menu-price">{(menu.price ?? 0).toLocaleString()}원</span>
          </div>
          <button
            type="button"
            className="menu-add-btn"
            onClick={() =>
              addItem({ id: menu.id ?? "", name: menu.name ?? "", price: menu.price ?? 0 })
            }
          >
            담기
          </button>
        </li>
      ))}
    </ul>
  );
}
