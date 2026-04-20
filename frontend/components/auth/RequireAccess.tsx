"use client";

import { useAuth } from "@/hooks/use-auth";

type AccessMode = "any" | "all";

type RequireAccessProps = {
  permissions: string[];
  mode?: AccessMode;
  children: React.ReactNode;
  fallback?: React.ReactNode;
};

export default function RequireAccess({ permissions, mode = "any", children, fallback }: RequireAccessProps) {
  const auth = useAuth();

  if (auth.status !== "authenticated") {
    return null;
  }

  const hasAccess =
    mode === "all" ? permissions.every((permission) => auth.can(permission)) : auth.canAny(...permissions);
  if (!hasAccess) {
    return (
      fallback ?? <p className="rounded-md border border-dashed p-4 text-sm">Keine Berechtigung fuer diesen Bereich.</p>
    );
  }

  return <>{children}</>;
}
