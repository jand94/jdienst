"use client";

import { useEffect, useState } from "react";

import {
  BREAKPOINTS,
  type Breakpoint,
  type BreakpointDirection,
  getBreakpointFromWidth,
  mq,
  resolveResponsiveValue,
} from "@/lib/responsiveness";
import { useMediaQuery } from "@/hooks/use-media-query";

type BreakpointOptions = {
  defaultValue?: boolean;
};

type CurrentBreakpointOptions = {
  defaultWidth?: number;
};

function getBreakpointQuery(breakpoint: Breakpoint, direction: BreakpointDirection): string {
  if (direction === "up") {
    return mq.up(breakpoint);
  }
  if (direction === "down") {
    return mq.down(breakpoint);
  }
  return mq.only(breakpoint);
}

export function useBreakpoint(
  breakpoint: Breakpoint,
  direction: BreakpointDirection = "up",
  options: BreakpointOptions = {},
): boolean {
  return useMediaQuery(getBreakpointQuery(breakpoint, direction), options);
}

export function useIsMobile(options: BreakpointOptions = {}): boolean {
  return useBreakpoint("md", "down", options);
}

export function useCurrentBreakpoint(options: CurrentBreakpointOptions = {}): Breakpoint {
  const { defaultWidth = BREAKPOINTS.md } = options;
  const [width, setWidth] = useState(defaultWidth);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    let frameId = 0;
    const updateWidth = () => {
      if (frameId) {
        window.cancelAnimationFrame(frameId);
      }
      frameId = window.requestAnimationFrame(() => {
        setWidth(window.innerWidth);
      });
    };

    updateWidth();
    window.addEventListener("resize", updateWidth);

    return () => {
      if (frameId) {
        window.cancelAnimationFrame(frameId);
      }
      window.removeEventListener("resize", updateWidth);
    };
  }, []);

  return getBreakpointFromWidth(width);
}

export function useResponsiveValue<T>(
  values: Partial<Record<Breakpoint, T>>,
  fallback: T,
  options: CurrentBreakpointOptions = {},
): T {
  const { defaultWidth = BREAKPOINTS.md } = options;
  const [width, setWidth] = useState(defaultWidth);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    let frameId = 0;
    const updateWidth = () => {
      if (frameId) {
        window.cancelAnimationFrame(frameId);
      }
      frameId = window.requestAnimationFrame(() => {
        setWidth(window.innerWidth);
      });
    };

    updateWidth();
    window.addEventListener("resize", updateWidth);

    return () => {
      if (frameId) {
        window.cancelAnimationFrame(frameId);
      }
      window.removeEventListener("resize", updateWidth);
    };
  }, []);

  return resolveResponsiveValue(values, width, fallback);
}
