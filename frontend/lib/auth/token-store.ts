let accessToken: string | null = null;
let tokenType = "Bearer";

export function setAccessToken(token: string, type = "Bearer"): void {
  accessToken = token;
  tokenType = type || "Bearer";
}

export function getAccessToken(): string | null {
  return accessToken;
}

export function getAuthorizationHeader(): string | null {
  if (!accessToken) {
    return null;
  }
  return `${tokenType} ${accessToken}`;
}

export function clearAccessToken(): void {
  accessToken = null;
  tokenType = "Bearer";
}
