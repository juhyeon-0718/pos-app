// POST /tables/{table_id}/session: QR 스캔 → 손님 세션 토큰 발급.
// 필드명은 docs/api/openapi.yaml -> schema.ts 기준. 손으로 다시 쓰지 않는다.

const BASE_URL = "/api/v1";

export interface TableSessionResponse {
  table_session_token: string;
  expires_at: string;
}

export async function createTableSession(
  tableId: string,
  qrToken: string,
  baseUrl = BASE_URL,
): Promise<TableSessionResponse> {
  const res = await fetch(`${baseUrl}/tables/${tableId}/session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ qr_token: qrToken }),
  });

  if (!res.ok) {
    throw new Error(`CREATE_TABLE_SESSION_FAILED: ${res.status}`);
  }
  return res.json();
}
