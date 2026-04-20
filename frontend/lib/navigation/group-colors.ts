import { navigationGroupColors } from "@/lib/navigation/navigation.config";
import type { NavigationGroupColorClasses, NavigationGroupKey } from "@/lib/navigation/navigation.config";

export function getNavigationGroupColors(group: NavigationGroupKey): NavigationGroupColorClasses {
  return navigationGroupColors[group];
}
