import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { describe, expect, it, vi } from "vitest";
import { Badge, Banner, Button, Card, EmptyState, ErrorState, Icon, LoadingState, Modal } from "./index";

describe("Button", () => {
  it("기본은 type=button이고 클릭하면 onClick이 호출된다", async () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>주문하기</Button>);
    const btn = screen.getByRole("button", { name: "주문하기" });
    expect(btn.getAttribute("type")).toBe("button");
    await userEvent.click(btn);
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("variant와 size가 클래스로 반영된다", () => {
    render(
      <Button variant="success" size="kitchen">
        조리 완료
      </Button>,
    );
    const cls = screen.getByRole("button").className;
    expect(cls).toContain("ui-btn-success");
    expect(cls).toContain("ui-btn-kitchen");
  });

  it("loading이면 aria-busy, 비활성, 스피너 + 글자를 보이고 클릭되지 않는다", async () => {
    const onClick = vi.fn();
    const { container } = render(
      <Button loading onClick={onClick}>
        처리 중
      </Button>,
    );
    const btn = screen.getByRole("button", { name: "처리 중" });
    expect(btn.getAttribute("aria-busy")).toBe("true");
    expect((btn as HTMLButtonElement).disabled).toBe(true);
    expect(container.querySelector('[data-icon="spinner"]')).not.toBeNull();
    await userEvent.click(btn);
    expect(onClick).not.toHaveBeenCalled();
  });

  it("disabled면 클릭되지 않는다", async () => {
    const onClick = vi.fn();
    render(
      <Button disabled onClick={onClick}>
        주문하기
      </Button>,
    );
    await userEvent.click(screen.getByRole("button"));
    expect(onClick).not.toHaveBeenCalled();
  });
});

describe("Badge", () => {
  const cases = [
    ["received", "접수", "inbox"],
    ["cooking", "조리중", "flame"],
    ["served", "서빙완료", "check"],
    ["paid", "결제 완료", "receipt"],
    ["cancelled", "취소됨", "x"],
  ] as const;

  it.each(cases)("%s: 글자와 아이콘을 함께 그린다", (status, label, icon) => {
    const { container } = render(<Badge status={status} />);
    expect(screen.getByText(label)).toBeTruthy();
    expect(container.querySelector(`[data-icon="${icon}"]`)).not.toBeNull();
  });

  it("large는 큰 배지 클래스를 붙인다", () => {
    const { container } = render(<Badge status="received" large />);
    expect(container.querySelector(".ui-badge-lg")).not.toBeNull();
  });
});

describe("Card", () => {
  it("attention이면 강조 테두리 클래스, as로 태그를 바꾼다", () => {
    const { container } = render(
      <ul>
        <Card as="li" attention>
          3번 테이블
        </Card>
      </ul>,
    );
    const li = container.querySelector("li");
    expect(li?.className).toContain("ui-card-attention");
    expect(li?.textContent).toBe("3번 테이블");
  });
});

describe("Banner", () => {
  it("오류는 role=alert, 경고·안내는 role=status", () => {
    render(
      <>
        <Banner tone="error" title="주문을 보내지 못했습니다">
          다시 시도해 주세요.
        </Banner>
        <Banner tone="info">주문이 접수되었습니다.</Banner>
      </>,
    );
    expect(screen.getByRole("alert").textContent).toContain("주문을 보내지 못했습니다");
    expect(screen.getByRole("status").textContent).toContain("주문이 접수되었습니다.");
  });

  it("action을 오른쪽에 보여 준다", () => {
    render(
      <Banner tone="error" action={<Button>다시 시도</Button>}>
        오류
      </Banner>,
    );
    expect(screen.getByRole("button", { name: "다시 시도" })).toBeTruthy();
  });
});

describe("상태 표시", () => {
  it("LoadingState는 aria-busy와 '불러오는 중'을 보인다", () => {
    const { container } = render(<LoadingState />);
    expect(container.querySelector('[aria-busy="true"]')).not.toBeNull();
    expect(screen.getByText("불러오는 중")).toBeTruthy();
  });

  it("EmptyState는 제목과 안내를 보인다", () => {
    render(<EmptyState title="아직 주문이 없습니다" description="새 주문이 들어오면 여기에 표시됩니다." />);
    expect(screen.getByRole("heading", { name: "아직 주문이 없습니다" })).toBeTruthy();
    expect(screen.getByText("새 주문이 들어오면 여기에 표시됩니다.")).toBeTruthy();
  });

  it("ErrorState는 role=alert이고 다시 시도 버튼이 onRetry를 부른다", async () => {
    const onRetry = vi.fn();
    render(<ErrorState onRetry={onRetry} />);
    expect(screen.getByRole("alert").textContent).toContain("불러오지 못했습니다");
    await userEvent.click(screen.getByRole("button", { name: "다시 시도" }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("ErrorState는 onRetry가 없으면 버튼을 그리지 않는다", () => {
    render(<ErrorState />);
    expect(screen.queryByRole("button")).toBeNull();
  });
});

describe("Icon", () => {
  it("장식용이라 aria-hidden이다", () => {
    const { container } = render(<Icon name="check" />);
    expect(container.querySelector("svg")?.getAttribute("aria-hidden")).toBe("true");
  });
});

function ModalHarness({ busy = false }: { busy?: boolean }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button onClick={() => setOpen(true)}>열기</button>
      {open ? (
        <Modal
          title="주문을 보낼까요?"
          busy={busy}
          onClose={() => setOpen(false)}
          footer={
            <>
              <Button variant="secondary" onClick={() => setOpen(false)}>
                돌아가기
              </Button>
              <Button>주문 보내기</Button>
            </>
          }
        >
          합계 21,000원
        </Modal>
      ) : null}
    </>
  );
}

describe("Modal", () => {
  it("제목으로 이름 붙은 dialog를 열고 첫 버튼에 포커스를 둔다", async () => {
    render(<ModalHarness />);
    await userEvent.click(screen.getByRole("button", { name: "열기" }));
    const dialog = screen.getByRole("dialog", { name: "주문을 보낼까요?" });
    expect(dialog.getAttribute("aria-modal")).toBe("true");
    expect(document.activeElement).toBe(screen.getByRole("button", { name: "돌아가기" }));
  });

  it("Esc로 닫히고 열었던 버튼으로 포커스가 돌아온다", async () => {
    render(<ModalHarness />);
    const opener = screen.getByRole("button", { name: "열기" });
    await userEvent.click(opener);
    await userEvent.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(document.activeElement).toBe(opener);
  });

  it("Tab 포커스가 모달 안에서만 돈다", async () => {
    render(<ModalHarness />);
    await userEvent.click(screen.getByRole("button", { name: "열기" }));
    const back = screen.getByRole("button", { name: "돌아가기" });
    const send = screen.getByRole("button", { name: "주문 보내기" });
    expect(document.activeElement).toBe(back);
    await userEvent.tab();
    expect(document.activeElement).toBe(send);
    await userEvent.tab();
    expect(document.activeElement).toBe(back);
    await userEvent.tab({ shift: true });
    expect(document.activeElement).toBe(send);
  });

  it("바깥(overlay)을 누르면 닫힌다", async () => {
    const { container } = render(<ModalHarness />);
    await userEvent.click(screen.getByRole("button", { name: "열기" }));
    await userEvent.click(container.ownerDocument.querySelector(".ui-overlay") as HTMLElement);
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("busy면 Esc와 바깥 클릭으로 닫히지 않는다", async () => {
    render(<ModalHarness busy />);
    await userEvent.click(screen.getByRole("button", { name: "열기" }));
    await userEvent.keyboard("{Escape}");
    await userEvent.click(document.querySelector(".ui-overlay") as HTMLElement);
    expect(screen.getByRole("dialog").getAttribute("aria-busy")).toBe("true");
  });
});
