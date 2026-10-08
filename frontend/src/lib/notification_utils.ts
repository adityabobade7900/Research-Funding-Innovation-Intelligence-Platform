import { NotificationType } from "@/types/notification";

export function formatRelativeTime(dateString: string): string {
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHours = Math.floor(diffMin / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSec < 60) return "Just now";
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  } catch {
    return "Recently";
  }
}

export function getTypeBadgeDetails(type: NotificationType): { label: string; bg: string; text: string; category: string } {
  switch (type) {
    case "FUNDING":
      return { label: "Funding Radar", bg: "bg-emerald-500/10 border-emerald-500/20", text: "text-emerald-400", category: "funding" };
    case "PATENT":
      return { label: "Patent IP", bg: "bg-violet-500/10 border-violet-500/20", text: "text-violet-400", category: "patents" };
    case "TECHNOLOGY":
      return { label: "Tech Intelligence", bg: "bg-cyan-500/10 border-cyan-500/20", text: "text-cyan-400", category: "technology" };
    case "RESEARCH_TREND":
      return { label: "Research Trend", bg: "bg-blue-500/10 border-blue-500/20", text: "text-blue-400", category: "research" };
    case "COMMERCIALIZATION":
      return { label: "Commercialization", bg: "bg-amber-500/10 border-amber-500/20", text: "text-amber-400", category: "commercialization" };
    case "PLATFORM":
    default:
      return { label: "Platform Alert", bg: "bg-slate-800 border-slate-700", text: "text-slate-300", category: "platform" };
  }
}
