// 현장에서 읽는 테이블 표기. 화면에는 내부 식별자(table_id)가 아니라 table_no를 보여 준다.
// table_no가 없으면(null/undefined) "테이블 -"로 표시한다.

export function tableLabel(tableNo: number | null | undefined): string {
  return tableNo == null ? "테이블 -" : `${tableNo}번 테이블`;
}
