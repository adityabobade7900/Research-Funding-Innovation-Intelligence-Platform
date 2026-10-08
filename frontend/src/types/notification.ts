export type NotificationType =
  | "FUNDING"
  | "PATENT"
  | "TECHNOLOGY"
  | "RESEARCH_TREND"
  | "COMMERCIALIZATION"
  | "PLATFORM";

export type NotificationPriority = "LOW" | "MEDIUM" | "HIGH";

export interface NotificationItem {
  id: number;
  user_id: number;
  type: NotificationType;
  title: string;
  message: string;
  related_module?: string | null;
  related_record_id?: string | null;
  target_url?: string | null;
  priority: NotificationPriority;
  is_read: boolean;
  created_at: string;
}

export interface NotificationListResponse {
  items: NotificationItem[];
  total: number;
  unread_count: number;
}

export interface NotificationUnreadResponse {
  unread_count: number;
}

export interface NotificationMarkReadResponse {
  id: number;
  is_read: boolean;
}

export interface NotificationMarkAllReadResponse {
  updated_count: number;
  message: string;
}

export interface NotificationScanResult {
  scanned_modules: string[];
  generated_count: number;
  notifications: NotificationItem[];
}
