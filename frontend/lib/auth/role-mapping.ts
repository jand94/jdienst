import type { AppRole, SessionUser } from "@/lib/auth/session-types";

const roleAliasMap: Record<string, AppRole> = {
  staff: "staff",
  is_staff: "staff",
  audit_reader: "audit_reader",
  "audit.reader": "audit_reader",
  audit_operator: "audit_operator",
  "audit.operator": "audit_operator",
};

const permissionRoleMap: Record<string, AppRole> = {
  "audit.events.read": "audit_reader",
  "audit.ops.manage": "audit_operator",
};

export function deriveRoles(user: SessionUser | null): AppRole[] {
  if (!user) {
    return [];
  }
  const resolved = new Set<AppRole>();
  if (user.is_staff) {
    resolved.add("staff");
    resolved.add("audit_reader");
    resolved.add("audit_operator");
  }
  for (const candidate of user.roles ?? []) {
    const mapped = roleAliasMap[candidate.trim().toLowerCase()];
    if (mapped) {
      resolved.add(mapped);
    }
  }
  for (const permission of user.permissions ?? []) {
    const mapped = permissionRoleMap[permission.trim().toLowerCase()];
    if (mapped) {
      resolved.add(mapped);
    }
  }
  return [...resolved];
}

export function hasAnyRole(userRoles: AppRole[], required: AppRole[]): boolean {
  if (required.length === 0) {
    return true;
  }
  const roleSet = new Set(userRoles);
  return required.some((role) => roleSet.has(role));
}
