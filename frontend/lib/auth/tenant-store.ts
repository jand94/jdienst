import { env } from "@/lib/config/env";

const TENANT_STORAGE_KEY = "jdienst.active-tenant";

let inMemoryTenantSlug = env.defaultTenantSlug;

function canUseStorage(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

export function getTenantSlug(): string {
  if (canUseStorage()) {
    const stored = window.localStorage.getItem(TENANT_STORAGE_KEY)?.trim();
    if (stored) {
      inMemoryTenantSlug = stored;
      return stored;
    }
  }
  return inMemoryTenantSlug;
}

export function setTenantSlug(tenantSlug: string): void {
  const value = tenantSlug.trim();
  inMemoryTenantSlug = value;
  if (!canUseStorage()) {
    return;
  }
  if (!value) {
    window.localStorage.removeItem(TENANT_STORAGE_KEY);
    return;
  }
  window.localStorage.setItem(TENANT_STORAGE_KEY, value);
}
