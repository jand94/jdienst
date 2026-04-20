export const responsiveTokens = {
  container: "w-full px-4 sm:px-6 lg:px-10",
  shellContainer: "flex w-full flex-1",
  pageContentPadding: "flex-1 px-4 py-6 sm:px-6 lg:px-10",
  mobilePanelPadding: "px-3 py-4",
  mobilePanelHeaderPadding: "border-b px-4 py-3",
  cardGrid: "grid gap-4 sm:grid-cols-2 xl:grid-cols-3",
  sectionSpacing: "space-y-6",
  headerSpacing: "space-y-2",
} as const;

export const containerWidthClasses = {
  narrow: "max-w-5xl",
  default: "max-w-7xl",
  wide: "max-w-screen-2xl",
  full: "max-w-none",
} as const;

export type ContainerWidth = keyof typeof containerWidthClasses;

type ContainerClassOptions = {
  width?: ContainerWidth;
  includePadding?: boolean;
  includeCentering?: boolean;
};

export function getResponsiveContainerClass(options: ContainerClassOptions = {}): string {
  const { width = "default", includePadding = true, includeCentering = true } = options;

  const parts: string[] = ["w-full", containerWidthClasses[width]];

  if (includeCentering) {
    parts.push("mx-auto");
  }

  if (includePadding) {
    parts.push("px-4", "sm:px-6", "lg:px-10");
  }

  return parts.join(" ");
}

export function getResponsiveMainPadding(compact = false): string {
  if (compact) {
    return "px-3 py-4 sm:px-5";
  }
  return "px-4 py-6 sm:px-6 lg:px-10";
}
