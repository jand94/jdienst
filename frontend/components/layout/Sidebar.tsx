"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

type NavigationItem = {
  href: string;
  label: string;
  description: string;
};

export const navigationItems: NavigationItem[] = [
  { href: "/", label: "Dashboard", description: "Startseite und Uebersicht" },
  { href: "/reports", label: "Reports", description: "Auswertungen und Kennzahlen" },
  { href: "/settings", label: "Einstellungen", description: "Konfiguration und Profile" },
];

function NavigationList({ compact = false }: { compact?: boolean }) {
  const pathname = usePathname();

  const isActiveLink = (href: string) =>
    href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);

  return (
    <ul className="space-y-1">
      {navigationItems.map((item) => {
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
  return (
    <aside className="hidden w-72 border-r bg-card px-4 py-6 md:block" aria-label="Hauptnavigation">
      <div className="mb-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">Navigation</h2>
      </div>
      <nav aria-label="Desktop Navigation">
        <NavigationList />
      </nav>
    </aside>
  );
}
