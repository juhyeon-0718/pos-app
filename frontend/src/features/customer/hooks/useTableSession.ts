// QR 스캔 진입: URL 쿼리(table_id, qr_token)로 세션을 발급받고 sessionStorage에 보관한다.
// 새로고침해도 세션이 유지되도록 하되, 다른 테이블 QR로 들어오면 새로 발급받는다.

import { useEffect, useState } from "react";
import { createTableSession } from "../../../api/tables";

const SESSION_STORAGE_KEY = "pos:table-session-token";

interface TableSessionState {
  token: string | null;
  loading: boolean;
  error: string | null;
}

export function useTableSession(): TableSessionState {
  const [state, setState] = useState<TableSessionState>({
    token: sessionStorage.getItem(SESSION_STORAGE_KEY),
    loading: false,
    error: null,
  });

  useEffect(() => {
    if (state.token) return;

    const params = new URLSearchParams(window.location.search);
    const tableId = params.get("table_id");
    const qrToken = params.get("qr_token");

    if (!tableId || !qrToken) {
      setState({ token: null, loading: false, error: "INVALID_QR_LINK" });
      return;
    }

    setState((s) => ({ ...s, loading: true, error: null }));
    createTableSession(tableId, qrToken)
      .then((res) => {
        sessionStorage.setItem(SESSION_STORAGE_KEY, res.table_session_token);
        setState({ token: res.table_session_token, loading: false, error: null });
      })
      .catch(() => {
        setState({ token: null, loading: false, error: "SESSION_CREATE_FAILED" });
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return state;
}
