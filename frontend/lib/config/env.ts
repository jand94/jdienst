const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
const defaultTenantSlug = process.env.NEXT_PUBLIC_DEFAULT_TENANT_SLUG;

export const env = {
  apiBaseUrl: (apiBaseUrl || "http://localhost:8000").replace(/\/+$/, ""),
  defaultTenantSlug: defaultTenantSlug?.trim() || "",
};
