"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { MenuIcon, Star } from "lucide-react";

import { useAuth } from "@/hooks/use-auth";
import { getVisibleNavigationItems } from "@/lib/navigation/navigation-policy";
import { getNavigationIcon } from "@/lib/navigation/icons";
import { getNavigationGroupColors } from "@/lib/navigation/group-colors";
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
  const visibleItems = getVisibleNavigationItems(auth);
  const topLevelItems = visibleItems.map((item) => ({ ...item, children: [] }));
  const favoriteSet = new Set(auth.navigationFavorites);

  return (
    <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur" data-breakpoint={currentBreakpoint}>
      <div className={cn(responsiveTokens.container, "flex h-16 items-center justify-between")}>
        <Link href="/" className="text-base font-semibold">
          jdienst
        </Link>

        <nav aria-label="Top Navigation" className="hidden items-center gap-5 md:flex">
          {topLevelItems.map((item) => {
            const isActive = isActiveLink(item.href);
            const NavIcon = getNavigationIcon(item.icon);
            const colorClasses = getNavigationGroupColors(item.group);

            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                className={cn(
                  "inline-flex items-center gap-2 border-b-2 border-transparent pb-1 text-sm text-muted-foreground transition-colors hover:text-foreground",
                  isActive && "border-b-primary font-medium",
                  isActive && colorClasses.activeText,
                )}
              >
                <NavIcon className={cn("h-4 w-4", colorClasses.icon)} />
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
                      const NavIcon = getNavigationIcon(item.icon);
                      const colorClasses = getNavigationGroupColors(item.group);

                      return (
                        <li key={item.href}>
                          <SheetClose asChild>
                            <Link
                              href={item.href}
                              aria-current={isActive ? "page" : undefined}
                              className={cn(
                                "block border-l-2 border-l-transparent px-3 py-2 text-sm text-muted-foreground transition-colors hover:border-l-border hover:bg-accent/40 hover:text-foreground",
                                isActive && cn("font-medium", colorClasses.activeBorder, colorClasses.activeText),
                              )}
                            >
                              <span className="inline-flex items-center gap-2 font-medium">
                                <NavIcon className={cn("h-4 w-4", colorClasses.icon)} />
                                {item.label}
                              </span>
                              <p className="text-xs text-muted-foreground">{item.description}</p>
                            </Link>
                          </SheetClose>
                          {auth.status === "authenticated" && (
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              className="mt-1 h-8 w-8 shrink-0"
                              aria-label={favoriteSet.has(item.href) ? "Favorit entfernen" : "Als Favorit markieren"}
                              onClick={() => {
                                void auth.toggleNavigationFavorite(item.href);
                              }}
                            >
                              <Star className={cn("h-4 w-4", favoriteSet.has(item.href) && "fill-current text-amber-500")} />
                            </Button>
                          )}
                          {item.children && item.children.length > 0 && (
                            <ul className="mt-1 space-y-1 pl-6">
                              {item.children.map((child) => {
                                const isChildActive = isActiveLink(child.href);
                                const ChildIcon = getNavigationIcon(child.icon);
                                const childColorClasses = getNavigationGroupColors(child.group);
                                return (
                                  <li key={child.href}>
                                    <SheetClose asChild>
                                      <Link
                                        href={child.href}
                                        aria-current={isChildActive ? "page" : undefined}
                                        className={cn(
                                          "block border-l-2 border-l-transparent px-3 py-2 text-sm text-muted-foreground transition-colors hover:border-l-border hover:bg-accent/40 hover:text-foreground",
                                          isChildActive &&
                                            cn("font-medium", childColorClasses.activeBorder, childColorClasses.activeText),
                                        )}
                                      >
                                        <span className="inline-flex items-center gap-2 font-medium">
                                          <ChildIcon className={cn("h-4 w-4", childColorClasses.icon)} />
                                          {child.label}
                                        </span>
                                        <p className="text-xs text-muted-foreground">{child.description}</p>
                                      </Link>
                                    </SheetClose>
                                    {auth.status === "authenticated" && (
                                      <Button
                                        type="button"
                                        variant="ghost"
                                        size="icon"
                                        className="mt-1 h-8 w-8 shrink-0"
                                        aria-label={favoriteSet.has(child.href) ? "Favorit entfernen" : "Als Favorit markieren"}
                                        onClick={() => {
                                          void auth.toggleNavigationFavorite(child.href);
                                        }}
                                      >
                                        <Star
                                          className={cn(
                                            "h-4 w-4",
                                            favoriteSet.has(child.href) && "fill-current text-amber-500",
                                          )}
                                        />
                                      </Button>
                                    )}
                                  </li>
                                );
                              })}
                            </ul>
                          )}
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
