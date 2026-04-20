export type NotificationOpsHealthSnapshot = {
  window_hours: number;
  passed: boolean;
  checks: Record<string, boolean>;
  delivery: {
    pending_total: number;
    failed_total: number;
    terminal_failed_total: number;
    retryable_failed_total: number;
    retries_due_total: number;
    oldest_pending_age_seconds: number;
    recent_success_rate: number;
    recent_sent_total: number;
    recent_failed_total: number;
    recent_skipped_total: number;
    max_attempts: number;
  };
  digest: {
    pending_total: number;
    failed_total: number;
  };
  thresholds: {
    max_pending_total: number;
    max_oldest_pending_age_seconds: number;
  };
};
