"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { MenuIcon } from "lucide-react";

import { navigationItems } from "@/components/layout/Sidebar";
import { useAuth } from "@/hooks/use-auth";
import { useCurrentBreakpoint, useResponsiveValue } from "@/hooks/use-breakpoint";
import { responsiveTokens } from "@/lib/responsive-tokens";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Sheet, SheetClose, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const auth = useAuth();
  const currentBreakpoint = useCurrentBreakpoint();
  const mobileSheetWidth = useResponsiveValue(
    {
      xs: "w-full",
      sm: "w-80",
    },
    "w-80",
  );
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

  return (
    <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur" data-breakpoint={currentBreakpoint}>
      <div className={cn(responsiveTokens.container, "flex h-16 items-center justify-between")}>
        <Link href="/" className="text-base font-semibold">
          jdienst
        </Link>

        <nav aria-label="Top Navigation" className="hidden items-center gap-5 md:flex">
          {visibleItems.map((item) => {
            const isActive = isActiveLink(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                className={cn(
                  "border-b-2 border-transparent pb-1 text-sm text-muted-foreground transition-colors hover:text-foreground",
                  isActive && "border-b-primary font-medium text-foreground",
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          {auth.status === "authenticated" ? (
            <>
              <span className="hidden text-sm text-muted-foreground md:inline">
                {auth.user?.username}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  void auth.signOut().then(() => {
                    router.replace("/login");
                  });
                }}
              >
                Logout
              </Button>
            </>
          ) : (
            <Button asChild variant="default" size="sm">
              <Link href="/login">Login</Link>
            </Button>
          )}

          <Sheet>
            <SheetTrigger asChild>
              <Button variant="outline" size="sm" className="md:hidden" aria-label="Mobile Navigation oeffnen">
                <MenuIcon />
                Menue
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className={cn("p-0", mobileSheetWidth)}>
              <SheetHeader className={responsiveTokens.mobilePanelHeaderPadding}>
                <SheetTitle>Navigation</SheetTitle>
                <SheetDescription>Schnellzugriff auf die wichtigsten Bereiche.</SheetDescription>
              </SheetHeader>
              <div className={responsiveTokens.mobilePanelPadding}>
                <nav aria-label="Mobile Navigation" className="w-full">
                  <ul className="space-y-1">
                    {visibleItems.map((item) => {
                      const isActive = isActiveLink(item.href);

                      return (
                        <li key={item.href}>
                          <SheetClose asChild>
                            <Link
                              href={item.href}
                              aria-current={isActive ? "page" : undefined}
                              className={cn(
                                "block border-l-2 border-l-transparent px-3 py-2 text-sm text-muted-foreground transition-colors hover:border-l-border hover:bg-accent/40 hover:text-foreground",
                                isActive && "border-l-primary font-medium text-foreground",
                              )}
                            >
                              <span className="font-medium">{item.label}</span>
                              <p className="text-xs text-muted-foreground">{item.description}</p>
                            </Link>
                          </SheetClose>
                        </li>
                      );
                    })}
                  </ul>
                </nav>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}
