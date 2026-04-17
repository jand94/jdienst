"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "@/hooks/use-auth";

type RequireAuthProps = {
  children: React.ReactNode;
};

export default function RequireAuth({ children }: RequireAuthProps) {
  const auth = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (auth.status === "unauthenticated" || auth.status === "error") {
      const nextPath = pathname ? `?next=${encodeURIComponent(pathname)}` : "";
      router.replace(`/login${nextPath}`);
    }
  }, [auth.status, pathname, router]);

  if (auth.status === "loading") {
    return <p className="text-sm text-muted-foreground">Sitzung wird geladen...</p>;
  }

  if (auth.status !== "authenticated") {
    return null;
  }

  return <>{children}</>;
}
