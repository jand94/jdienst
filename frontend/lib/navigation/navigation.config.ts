import type { AppPermission } from "@/lib/auth/session-types";
import type { LucideIcon } from "lucide-react";
import { BarChart3, LayoutDashboard, Settings, ShieldCheck, Users, Wrench } from "lucide-react";

/**
 * Navigation-Konfiguration (Single Source of Truth)
 *
 * Vorgehen fuer neue Eintraege:
 * 1) Neues Icon definieren:
 *    - NavigationIconKey erweitern
 *    - navigationIconRegistry ergaenzen
 * 2) Neue Gruppe (falls noetig):
 *    - NavigationGroupKey erweitern
 *    - navigationGroupColors ergaenzen
 * 3) Navigationseintrag in navigationItems ergaenzen:
 *    - href, label, description, icon, group, requiredPermissions
 *    - optional children fuer Dropdown-Unterseiten
 *
 * Hinweise:
 * - Reihenfolge im Menue entspricht der Reihenfolge in navigationItems.
 * - Unterseiten werden in Sidebar/Mobile als Child-Links dargestellt.
 * - Favoriten (Top-Level + Child) nutzen dieselben href-Werte und werden backend-persistent gespeichert.
 */
export type NavigationGroupKey = "core" | "audit" | "reports" | "settings";
export type NavigationIconKey = "dashboard" | "auditEvents" | "auditOps" | "reports" | "settings" | "users" | "crm";

export type NavigationGroupColorClasses = {
  icon: string;
  activeBorder: string;
  activeText: string;
  badgeBg: string;
};

export type NavigationChildItem = {
  href: string;
  label: string;
  description: string;
  icon: NavigationIconKey;
  group: NavigationGroupKey;
  requiredPermissions?: AppPermission[];
};

export type NavigationItem = {
  href: string;
  label: string;
  description: string;
  icon: NavigationIconKey;
  group: NavigationGroupKey;
  requiresAuth?: boolean;
  requiredPermissions?: AppPermission[];
  children?: NavigationChildItem[];
};

export const navigationIconRegistry: Record<NavigationIconKey, LucideIcon> = {
  dashboard: LayoutDashboard,
  auditEvents: ShieldCheck,
  auditOps: Wrench,
  reports: BarChart3,
  settings: Settings,
  users: Users,
  crm: BarChart3,
};

export const navigationGroupColors: Record<NavigationGroupKey, NavigationGroupColorClasses> = {
  core: {
    icon: "text-sky-600",
    activeBorder: "border-l-sky-600",
    activeText: "text-sky-700",
    badgeBg: "bg-sky-100",
  },
  audit: {
    icon: "text-violet-600",
    activeBorder: "border-l-violet-600",
    activeText: "text-violet-700",
    badgeBg: "bg-violet-100",
  },
  reports: {
    icon: "text-emerald-600",
    activeBorder: "border-l-emerald-600",
    activeText: "text-emerald-700",
    badgeBg: "bg-emerald-100",
  },
  settings: {
    icon: "text-amber-600",
    activeBorder: "border-l-amber-600",
    activeText: "text-amber-700",
    badgeBg: "bg-amber-100",
  },
};

export const navigationItems: NavigationItem[] = [
  {
    href: "/",
    label: "Dashboard",
    description: "Startseite und Uebersicht",
    icon: "dashboard",
    group: "core",
    requiresAuth: true,
    requiredPermissions: ["dashboard.view"],
  },
  {
    href: "/audit",
    label: "Audit Events",
    description: "Pruefung von Sicherheitsereignissen",
    icon: "auditEvents",
    group: "audit",
    requiresAuth: true,
    requiredPermissions: ["audit.events.read", "audit.ops.manage"],
  },
  {
    href: "/audit/ops",
    label: "Audit Ops",
    description: "Integritaet, SIEM und Retention",
    icon: "auditOps",
    group: "audit",
    requiresAuth: true,
    requiredPermissions: ["audit.ops.manage"],
  },
  {
    href: "/reports",
    label: "Reports",
    description: "Auswertungen und Kennzahlen",
    icon: "reports",
    group: "reports",
    requiresAuth: true,
    requiredPermissions: ["reports.view"],
  },
  {
    href: "/settings",
    label: "Einstellungen",
    description: "Konfiguration und Profile",
    icon: "settings",
    group: "settings",
    requiresAuth: true,
    requiredPermissions: ["settings.view"],
    children: [
      {
        href: "/settings/users",
        label: "Benutzer",
        description: "Benutzerverwaltung und Rollen",
        icon: "users",
        group: "settings",
        requiredPermissions: ["settings.view"],
      },
      {
        href: "/settings/crm",
        label: "CRM",
        description: "CRM-Module und Integrationen",
        icon: "crm",
        group: "settings",
        requiredPermissions: ["settings.view"],
      },
    ],
  },
];
