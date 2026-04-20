import { getAuthorizationHeader } from "@/lib/auth/token-store";
import { env } from "@/lib/config/env";

type HttpMethod = "GET" | "POST" | "PATCH" | "PUT" | "DELETE";

export class ApiError extends Error {
  status: number;
  payload: unknown;

  constructor(message: string, status: number, payload: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

type RequestOptions = {
  method?: HttpMethod;
  body?: unknown;
  headers?: Record<string, string>;
  auth?: boolean;
  includeCredentials?: boolean;
  tenantSlug?: string;
  retryOnAuthFailure?: boolean;
};

type RefreshHandler = () => Promise<void>;

let refreshHandler: RefreshHandler | null = null;
let refreshPromise: Promise<void> | null = null;

function normalizePath(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return `${env.apiBaseUrl}${path.startsWith("/") ? "" : "/"}${path}`;
}

async function parseBody(response: Response): Promise<unknown> {
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return response.json();
  }
  return response.text();
}

async function runRefresh(): Promise<void> {
  if (!refreshHandler) {
    throw new Error("No refresh handler registered.");
  }
  if (!refreshPromise) {
    refreshPromise = refreshHandler().finally(() => {
      refreshPromise = null;
    });
  }
  await refreshPromise;
}

async function requestInternal<T>(
  path: string,
  options: RequestOptions = {},
  allowRetry = true,
): Promise<T> {
  const method = options.method ?? "GET";
  const headers = new Headers(options.headers);
  const shouldIncludeCredentials = options.includeCredentials ?? false;

  if (!headers.has("Content-Type") && options.body !== undefined) {
    headers.set("Content-Type", "application/json");
  }

  if (options.auth) {
    const authorization = getAuthorizationHeader();
    if (authorization) {
      headers.set("Authorization", authorization);
    }
  }

  if (options.tenantSlug) {
    headers.set("X-Tenant-Slug", options.tenantSlug);
  }

  const response = await fetch(normalizePath(path), {
    method,
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
    credentials: shouldIncludeCredentials ? "include" : "same-origin",
  });

  if (response.status === 401 && options.auth && allowRetry && (options.retryOnAuthFailure ?? true)) {
    await runRefresh();
    return requestInternal<T>(path, options, false);
  }

  const payload = await parseBody(response);
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    if (typeof payload === "object" && payload !== null) {
      if ("detail" in payload) {
        message = String((payload as { detail: unknown }).detail);
      } else if ("error" in payload) {
        const errorPayload = (payload as { error?: unknown }).error;
        if (
          typeof errorPayload === "object" &&
          errorPayload !== null &&
          "message" in errorPayload &&
          typeof (errorPayload as { message?: unknown }).message === "string"
        ) {
          message = (errorPayload as { message: string }).message;
        }
      }
    }
    throw new ApiError(message, response.status, payload);
  }
  return payload as T;
}

export const httpClient = {
  setRefreshHandler(handler: RefreshHandler): void {
    refreshHandler = handler;
  },
  get<T>(path: string, options?: Omit<RequestOptions, "method" | "body">): Promise<T> {
    return requestInternal<T>(path, { ...options, method: "GET" });
  },
  post<T>(path: string, body?: unknown, options?: Omit<RequestOptions, "method" | "body">): Promise<T> {
    return requestInternal<T>(path, { ...options, method: "POST", body });
  },
  patch<T>(path: string, body?: unknown, options?: Omit<RequestOptions, "method" | "body">): Promise<T> {
    return requestInternal<T>(path, { ...options, method: "PATCH", body });
  },
  put<T>(path: string, body?: unknown, options?: Omit<RequestOptions, "method" | "body">): Promise<T> {
    return requestInternal<T>(path, { ...options, method: "PUT", body });
  },
};
