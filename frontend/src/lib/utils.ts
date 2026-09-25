import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatRoleName(role: string): string {
  switch (role) {
    case "researcher":
      return "Researcher";
    case "startup_founder":
      return "Startup Founder";
    case "innovation_manager":
      return "Innovation Manager";
    case "administrator":
      return "Administrator";
    default:
      return role;
  }
}
