import type { ReactNode } from "react";
import { Button } from "./Button";
import { Icon, type IconName } from "./Icon";
import "./ui.css";

// 로딩·빈 상태·오류 표시. 정렬을 컴포넌트가 직접 지정해 #root의 text-align에 기대지 않는다.

interface LoadingStateProps {
  label?: string;
}

export function LoadingState({ label = "불러오는 중" }: LoadingStateProps) {
  return (
    <div className="ui-state ui-loading" aria-busy="true">
      <span className="ui-skeleton" style={{ width: "70%" }} />
      <span className="ui-skeleton" />
      <span className="ui-skeleton" style={{ width: "50%" }} />
      <div className="ui-loading-note" role="status">
        <Icon name="spinner" />
        {label}
      </div>
    </div>
  );
}

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: IconName;
  action?: ReactNode;
}

export function EmptyState({ title, description, icon = "inbox", action }: EmptyStateProps) {
  return (
    <div className="ui-state ui-empty">
      <Icon name={icon} />
      <h2>{title}</h2>
      {description ? <p>{description}</p> : null}
      {action}
    </div>
  );
}

interface ErrorStateProps {
  title?: string;
  description?: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = "불러오지 못했습니다",
  description = "네트워크를 확인하고 다시 시도해 주세요.",
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="ui-state ui-empty" role="alert">
      <Icon name="alert" />
      <h2>{title}</h2>
      <p>{description}</p>
      {onRetry ? (
        <Button icon="refresh" onClick={onRetry}>
          다시 시도
        </Button>
      ) : null}
    </div>
  );
}
