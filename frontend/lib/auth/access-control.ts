export function hasPermission(permissions: string[], requiredPermission: string): boolean {
  if (!requiredPermission.trim()) {
    return true;
  }
  const permissionSet = new Set(permissions);
  return permissionSet.has(requiredPermission);
}

export function hasAnyPermission(permissions: string[], requiredPermissions: string[]): boolean {
  if (requiredPermissions.length === 0) {
    return true;
  }
  const permissionSet = new Set(permissions);
  return requiredPermissions.some((permission) => permissionSet.has(permission));
}

export function hasAllPermissions(permissions: string[], requiredPermissions: string[]): boolean {
  if (requiredPermissions.length === 0) {
    return true;
  }
  const permissionSet = new Set(permissions);
  return requiredPermissions.every((permission) => permissionSet.has(permission));
}

export function hasFeatureFlag(featureFlags: string[], featureFlag: string): boolean {
  if (!featureFlag.trim()) {
    return true;
  }
  const featureSet = new Set(featureFlags);
  return featureSet.has(featureFlag);
}
