"use client";

import type { AppRole } from "@/lib/auth/session-types";
import { useAuth } from "@/hooks/use-auth";

type RequireRoleProps = {
  roles: AppRole[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
};

export default function RequireRole({ roles, children, fallback }: RequireRoleProps) {
  const auth = useAuth();

  if (auth.status !== "authenticated") {
    return null;
  }

  if (!auth.hasRole(...roles)) {
    return (
      fallback ?? <p className="rounded-md border border-dashed p-4 text-sm">Keine Berechtigung fuer diesen Bereich.</p>
    );
  }

  return <>{children}</>;
}
