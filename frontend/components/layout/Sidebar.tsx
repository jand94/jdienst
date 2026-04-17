"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useAuth } from "@/hooks/use-auth";
import type { AppRole } from "@/lib/auth/session-types";
import { cn } from "@/lib/utils";

type NavigationItem = {
  href: string;
  label: string;
  description: string;
  requiresAuth?: boolean;
  requiredRoles?: AppRole[];
};

export const navigationItems: NavigationItem[] = [
  { href: "/", label: "Dashboard", description: "Startseite und Uebersicht", requiresAuth: true },
  { href: "/audit", label: "Audit Events", description: "Pruefung von Sicherheitsereignissen", requiresAuth: true, requiredRoles: ["audit_reader"] },
  {
    href: "/audit/ops",
    label: "Audit Ops",
    description: "Integritaet, SIEM und Retention",
    requiresAuth: true,
    requiredRoles: ["audit_operator"],
  },
  { href: "/reports", label: "Reports", description: "Auswertungen und Kennzahlen", requiresAuth: true },
  { href: "/settings", label: "Einstellungen", description: "Konfiguration und Profile", requiresAuth: true },
];

function NavigationList({ compact = false }: { compact?: boolean }) {
  const pathname = usePathname();
  const auth = useAuth();

  const isActiveLink = (href: string) =>
    href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);

  const visibleItems = navigationItems.filter((item) => {
    if (item.requiresAuth && auth.status !== "authenticated") {
      return false;
    }
    if (item.requiredRoles && !auth.hasRole(...item.requiredRoles)) {
      return false;
    }
    return true;
  });

  if (visibleItems.length === 0) {
    return <p className="px-3 py-2 text-sm text-muted-foreground">Melde dich an, um Navigationseintraege zu sehen.</p>;
  }

  return (
    <ul className="space-y-1">
      {visibleItems.map((item) => {
        const isActive = isActiveLink(item.href);

        return (
          <li key={item.href}>
            <Link
              href={item.href}
              aria-current={isActive ? "page" : undefined}
              className={cn(
                "block border-l-2 border-l-transparent px-3 py-2 text-sm text-muted-foreground transition-colors hover:border-l-border hover:bg-accent/40 hover:text-foreground",
                isActive && "border-l-primary font-medium text-foreground",
                compact ? "pl-2" : "",
              )}
            >
              <span className="font-medium">{item.label}</span>
              <p className="text-xs text-muted-foreground">{item.description}</p>
            </Link>
          </li>
        );
      })}
    </ul>
  );
}

export function MobileSidebarMenu() {
  return (
    <nav aria-label="Mobile Navigation" className="w-full">
      <NavigationList compact />
    </nav>
  );
}

export default function Sidebar() {
  const auth = useAuth();

  return (
    <aside className="hidden w-72 border-r bg-card px-4 py-6 md:block" aria-label="Hauptnavigation">
      <div className="mb-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">Navigation</h2>
        {auth.status === "authenticated" && (
          <p className="mt-1 text-xs text-muted-foreground">Tenant: {auth.tenantSlug || "nicht gesetzt"}</p>
        )}
      </div>
      <nav aria-label="Desktop Navigation">
        <NavigationList />
      </nav>
    </aside>
  );
}
