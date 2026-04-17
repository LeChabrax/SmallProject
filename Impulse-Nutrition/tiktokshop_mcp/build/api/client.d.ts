export interface TikTokConfig {
    appKey: string;
    appSecret: string;
    accessToken: string;
    refreshToken?: string;
    expiresAt?: number;
    shopCipher?: string;
    baseUrl?: string;
    apiVersion?: string;
    /** Path to .env file for persisting refreshed tokens. Defaults to the
     * .env at the project root (two dirs up from the compiled client.js). */
    envPath?: string;
}
export interface ApiResponse<T = unknown> {
    code: number;
    message: string;
    data: T;
    request_id?: string;
}
export declare class TikTokShopClient {
    private config;
    private refreshPromise;
    constructor(config: TikTokConfig);
    private generateSign;
    /**
     * Uses the stored refresh_token to obtain a new access_token.
     * Persists the new tokens (and new expires_at) back to the .env file.
     * Concurrent callers share the same in-flight promise so we don't
     * hammer the refresh endpoint.
     */
    private refreshAccessToken;
    private doRefresh;
    /** Update 3 keys in the .env file, preserving other lines intact. */
    private persistTokensToEnv;
    request<T = unknown>(method: "GET" | "POST" | "PUT" | "DELETE", path: string, params?: Record<string, string>, body?: Record<string, unknown>, retried?: boolean): Promise<ApiResponse<T>>;
    get<T = unknown>(path: string, params?: Record<string, string>): Promise<ApiResponse<T>>;
    post<T = unknown>(path: string, params?: Record<string, string>, body?: Record<string, unknown>): Promise<ApiResponse<T>>;
}
export declare function createClientFromEnv(): TikTokShopClient;
//# sourceMappingURL=client.d.ts.map