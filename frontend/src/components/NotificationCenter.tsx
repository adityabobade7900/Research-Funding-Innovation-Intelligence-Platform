"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Bell,
  CheckCheck,
  RefreshCw,
  Sparkles,
  Search,
  FileCode2,
  TrendingUp,
  Briefcase,
  Layers,
  ChevronRight,
  Inbox,
  AlertCircle,
  Check,
} from "lucide-react";
import { api } from "@/lib/api";
import { NotificationItem, NotificationType } from "@/types/notification";
import { formatRelativeTime, getTypeBadgeDetails } from "@/lib/notification_utils";

export function getTypeIcon(type: NotificationType) {
  switch (type) {
    case "FUNDING":
      return Search;
    case "PATENT":
      return FileCode2;
    case "TECHNOLOGY":
      return Sparkles;
    case "RESEARCH_TREND":
      return TrendingUp;
    case "COMMERCIALIZATION":
      return Briefcase;
    case "PLATFORM":
    default:
      return Layers;
  }
}

export default function NotificationCenter() {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState<NotificationType | "ALL">("ALL");
  const panelRef = useRef<HTMLDivElement>(null);

  // Fetch unread count & initial items
  const loadNotifications = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.get("/notifications?limit=50");
      if (res.data?.success && res.data?.data) {
        setNotifications(res.data.data.items || []);
        setUnreadCount(res.data.data.unread_count || 0);
      }
    } catch (err: any) {
      setError(err?.response?.data?.error?.message || "Failed to load notifications");
    } finally {
      setLoading(false);
    }
  }, []);

  const loadUnreadCountOnly = useCallback(async () => {
    try {
      const res = await api.get("/notifications/unread");
      if (res.data?.success && res.data?.data) {
        setUnreadCount(res.data.data.unread_count || 0);
      }
    } catch {
      // Silently ignore polling/header count failures
    }
  }, []);

  useEffect(() => {
    loadUnreadCountOnly();
  }, [loadUnreadCountOnly]);

  useEffect(() => {
    if (isOpen) {
      loadNotifications();
    }
  }, [isOpen, loadNotifications]);

  // Handle clicking outside to close
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  const handleMarkAsRead = async (id: number, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    try {
      // Optimistic update
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
      await api.patch(`/notifications/${id}/read`);
    } catch {
      // Revert if failed
      loadNotifications();
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
      await api.patch("/notifications/read-all");
    } catch {
      loadNotifications();
    }
  };

  const handleScanAlerts = async () => {
    try {
      setScanning(true);
      setError(null);
      await api.post("/notifications/scan");
      await loadNotifications();
    } catch (err: any) {
      setError(err?.response?.data?.error?.message || "Intelligence scan failed");
    } finally {
      setScanning(false);
    }
  };

  const handleNotificationClick = async (notif: NotificationItem) => {
    if (!notif.is_read) {
      await handleMarkAsRead(notif.id);
    }
    setIsOpen(false);
    if (notif.target_url) {
      router.push(notif.target_url);
    }
  };

  const filteredNotifications = notifications.filter((n) => {
    if (activeCategory === "ALL") return true;
    return n.type === activeCategory;
  });

  return (
    <div className="relative" ref={panelRef}>
      {/* Bell Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Notification Center"
        className={`p-2 rounded-lg border transition-all relative ${
          isOpen
            ? "bg-slate-800 border-blue-500/50 text-white"
            : "bg-slate-900 border-slate-800 text-slate-400 hover:text-white hover:border-slate-700"
        }`}
      >
        <Bell className="w-4 h-4" />
        {unreadCount > 0 ? (
          <span className="absolute -top-1 -right-1 flex h-4 min-w-[16px] px-1 items-center justify-center rounded-full bg-blue-600 text-[10px] font-bold text-white shadow-lg shadow-blue-500/40 animate-pulse">
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        ) : (
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-slate-600"></span>
        )}
      </button>

      {/* Floating Dropdown Panel */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 max-w-[90vw] sm:w-[420px] rounded-2xl bg-slate-900/95 border border-slate-800 shadow-2xl backdrop-blur-2xl z-50 overflow-hidden flex flex-col max-h-[82vh] animate-in fade-in zoom-in-95 duration-150">
          {/* Header */}
          <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-white tracking-tight">Notification Center</span>
              {unreadCount > 0 && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  {unreadCount} unread
                </span>
              )}
            </div>

            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={handleScanAlerts}
                disabled={scanning}
                title="Scan intelligence modules for new events"
                className="p-1.5 rounded-lg text-slate-400 hover:text-blue-400 hover:bg-slate-800/80 transition-colors disabled:opacity-50 text-xs flex items-center gap-1"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${scanning ? "animate-spin text-blue-400" : ""}`} />
                <span className="text-[11px] hidden sm:inline">{scanning ? "Scanning..." : "Scan"}</span>
              </button>

              {unreadCount > 0 && (
                <button
                  type="button"
                  onClick={handleMarkAllAsRead}
                  title="Mark all as read"
                  className="p-1.5 rounded-lg text-slate-400 hover:text-emerald-400 hover:bg-slate-800/80 transition-colors text-xs flex items-center gap-1"
                >
                  <CheckCheck className="w-3.5 h-3.5" />
                  <span className="text-[11px] hidden sm:inline">Mark all</span>
                </button>
              )}
            </div>
          </div>

          {/* Category Tabs */}
          <div className="px-3 py-2 border-b border-slate-800/70 bg-slate-950/40 flex items-center gap-1.5 overflow-x-auto scrollbar-none">
            {(
              [
                { id: "ALL", label: "All" },
                { id: "FUNDING", label: "Funding" },
                { id: "PATENT", label: "Patents" },
                { id: "TECHNOLOGY", label: "Tech" },
                { id: "RESEARCH_TREND", label: "Trends" },
                { id: "COMMERCIALIZATION", label: "Commercial" },
                { id: "PLATFORM", label: "Platform" },
              ] as const
            ).map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveCategory(tab.id)}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-medium whitespace-nowrap transition-colors ${
                  activeCategory === tab.id
                    ? "bg-blue-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Content Body */}
          <div className="flex-1 overflow-y-auto divide-y divide-slate-800/50">
            {loading ? (
              <div className="p-8 flex flex-col items-center justify-center gap-2 text-slate-400 text-xs">
                <RefreshCw className="w-5 h-5 animate-spin text-blue-400" />
                <span>Syncing notifications...</span>
              </div>
            ) : error ? (
              <div className="p-6 text-center">
                <AlertCircle className="w-6 h-6 text-rose-400 mx-auto mb-2" />
                <p className="text-xs text-rose-300 mb-3">{error}</p>
                <button
                  type="button"
                  onClick={loadNotifications}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 transition-colors"
                >
                  Retry
                </button>
              </div>
            ) : filteredNotifications.length === 0 ? (
              <div className="p-10 flex flex-col items-center justify-center text-center text-slate-500">
                <Inbox className="w-8 h-8 text-slate-600 mb-2 stroke-[1.5]" />
                <p className="text-xs font-medium text-slate-400">No notifications found</p>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  {activeCategory === "ALL"
                    ? "Click 'Scan' to discover real-time alerts across funding, patents, and tech."
                    : `No ${activeCategory.toLowerCase().replace('_', ' ')} alerts tracked currently.`}
                </p>
              </div>
            ) : (
              filteredNotifications.map((item) => {
                const badge = getTypeBadgeDetails(item.type);
                const IconComponent = getTypeIcon(item.type);
                return (
                  <div
                    key={item.id}
                    onClick={() => handleNotificationClick(item)}
                    className={`p-3.5 transition-colors cursor-pointer flex gap-3 group relative ${
                      item.is_read
                        ? "hover:bg-slate-800/40 opacity-80"
                        : "bg-blue-500/[0.03] hover:bg-blue-500/[0.08]"
                    }`}
                  >
                    {/* Unread Glow Indicator */}
                    {!item.is_read && (
                      <span className="absolute top-4 left-1.5 w-1.5 h-1.5 rounded-full bg-blue-500 shadow-sm shadow-blue-400"></span>
                    )}

                    {/* Icon */}
                    <div
                      className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 border ${badge.bg} ${badge.text}`}
                    >
                      <IconComponent className="w-4 h-4" />
                    </div>

                    {/* Text Details */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <span
                          className={`text-[10px] font-semibold px-1.5 py-0.2 rounded border ${badge.bg} ${badge.text}`}
                        >
                          {badge.label}
                        </span>

                        <div className="flex items-center gap-1.5">
                          {item.priority === "HIGH" && (
                            <span className="text-[9px] px-1.5 py-0.2 rounded bg-rose-500/10 border border-rose-500/20 text-rose-400 font-bold uppercase tracking-wider">
                              HIGH
                            </span>
                          )}
                          <span className="text-[10px] text-slate-500">{formatRelativeTime(item.created_at)}</span>
                        </div>
                      </div>

                      <h4
                        className={`text-xs font-semibold tracking-tight leading-snug line-clamp-1 mb-0.5 ${
                          item.is_read ? "text-slate-300" : "text-white"
                        }`}
                      >
                        {item.title}
                      </h4>
                      <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">{item.message}</p>
                    </div>

                    {/* Action Controls */}
                    <div className="flex flex-col justify-between items-end flex-shrink-0">
                      {!item.is_read ? (
                        <button
                          type="button"
                          onClick={(e) => handleMarkAsRead(item.id, e)}
                          title="Mark as read"
                          className="p-1 rounded text-slate-500 hover:text-emerald-400 hover:bg-slate-800 transition-colors"
                        >
                          <Check className="w-3.5 h-3.5" />
                        </button>
                      ) : (
                        <span className="w-3.5 h-3.5"></span>
                      )}
                      <ChevronRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-slate-300 group-hover:translate-x-0.5 transition-all" />
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Footer */}
          <div className="p-2.5 bg-slate-950/80 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-500 px-4">
            <span>Module 10 Proactive Intelligence</span>
            {filteredNotifications.length > 0 && (
              <span>Showing {filteredNotifications.length} items</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
