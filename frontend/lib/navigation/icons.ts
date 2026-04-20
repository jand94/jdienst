import type { LucideIcon } from "lucide-react";
import { navigationIconRegistry } from "@/lib/navigation/navigation.config";
import type { NavigationIconKey } from "@/lib/navigation/navigation.config";

export function getNavigationIcon(iconKey: NavigationIconKey): LucideIcon {
  return navigationIconRegistry[iconKey];
}
