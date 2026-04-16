export const BREAKPOINTS = {
  xs: 0,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  "2xl": 1536,
} as const;

export type Breakpoint = keyof typeof BREAKPOINTS;
export type BreakpointDirection = "up" | "down" | "only";

const MAX_WIDTH_EPSILON = 0.02;

const breakpointEntries = Object.entries(BREAKPOINTS) as [Breakpoint, number][];
const breakpointOrder = breakpointEntries
  .sort(([, a], [, b]) => a - b)
  .map(([name]) => name);

export function getBreakpointValue(breakpoint: Breakpoint): number {
  return BREAKPOINTS[breakpoint];
}

export function getBreakpointOrder(): Breakpoint[] {
  return [...breakpointOrder];
}

export function getNextBreakpoint(breakpoint: Breakpoint): Breakpoint | null {
  const index = breakpointOrder.indexOf(breakpoint);
  if (index < 0 || index === breakpointOrder.length - 1) {
    return null;
  }
  return breakpointOrder[index + 1];
}

export function getPreviousBreakpoint(breakpoint: Breakpoint): Breakpoint | null {
  const index = breakpointOrder.indexOf(breakpoint);
  if (index <= 0) {
    return null;
  }
  return breakpointOrder[index - 1];
}

export const mq = {
  up(breakpoint: Breakpoint): string {
    return `(min-width: ${getBreakpointValue(breakpoint)}px)`;
  },

  down(breakpoint: Breakpoint): string {
    return `(max-width: ${getBreakpointValue(breakpoint) - MAX_WIDTH_EPSILON}px)`;
  },

  only(breakpoint: Breakpoint): string {
    const minWidth = getBreakpointValue(breakpoint);
    const next = getNextBreakpoint(breakpoint);

    if (!next) {
      return `(min-width: ${minWidth}px)`;
    }

    const maxWidth = getBreakpointValue(next) - MAX_WIDTH_EPSILON;
    return `(min-width: ${minWidth}px) and (max-width: ${maxWidth}px)`;
  },

  between(from: Breakpoint, to: Breakpoint): string {
    const minWidth = Math.min(getBreakpointValue(from), getBreakpointValue(to));
    const maxWidth = Math.max(getBreakpointValue(from), getBreakpointValue(to)) - MAX_WIDTH_EPSILON;
    return `(min-width: ${minWidth}px) and (max-width: ${maxWidth}px)`;
  },

  custom(query: string): string {
    return query;
  },
};

export function getBreakpointFromWidth(width: number): Breakpoint {
  let active = breakpointOrder[0];

  for (const breakpoint of breakpointOrder) {
    if (width >= getBreakpointValue(breakpoint)) {
      active = breakpoint;
    }
  }

  return active;
}

export function isWidthUp(width: number, breakpoint: Breakpoint): boolean {
  return width >= getBreakpointValue(breakpoint);
}

export function isWidthDown(width: number, breakpoint: Breakpoint): boolean {
  return width < getBreakpointValue(breakpoint);
}

export function isWidthOnly(width: number, breakpoint: Breakpoint): boolean {
  const current = getBreakpointFromWidth(width);
  return current === breakpoint;
}

export function isWidthBetween(width: number, from: Breakpoint, to: Breakpoint): boolean {
  const minWidth = Math.min(getBreakpointValue(from), getBreakpointValue(to));
  const maxWidth = Math.max(getBreakpointValue(from), getBreakpointValue(to));
  return width >= minWidth && width < maxWidth;
}

export function resolveResponsiveValue<T>(
  values: Partial<Record<Breakpoint, T>>,
  width: number,
  fallback: T,
): T {
  let resolved = fallback;

  for (const breakpoint of breakpointOrder) {
    const value = values[breakpoint];
    if (value !== undefined && width >= getBreakpointValue(breakpoint)) {
      resolved = value;
    }
  }

  return resolved;
}
