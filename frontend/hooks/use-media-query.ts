"use client";

import { useCallback, useSyncExternalStore } from "react";

type UseMediaQueryOptions = {
  defaultValue?: boolean;
};

function createNoopUnsubscribe() {
  return () => {};
}

export function useMediaQuery(query: string, options: UseMediaQueryOptions = {}): boolean {
  const { defaultValue = false } = options;

  const getServerSnapshot = useCallback(() => defaultValue, [defaultValue]);

  const getSnapshot = useCallback(() => {
    if (typeof window === "undefined") {
      return defaultValue;
    }
    return window.matchMedia(query).matches;
  }, [defaultValue, query]);

  const subscribe = useCallback((onStoreChange: () => void) => {
    if (typeof window === "undefined") {
      return createNoopUnsubscribe();
    }

    const mediaQueryList = window.matchMedia(query);
    mediaQueryList.addEventListener("change", onStoreChange);

    return () => mediaQueryList.removeEventListener("change", onStoreChange);
  }, [query]);

  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}
