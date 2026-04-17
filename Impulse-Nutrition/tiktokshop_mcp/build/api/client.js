import crypto from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
export class TikTokShopClient {
    config;
    refreshPromise = null;
    constructor(config) {
        const defaultEnvPath = resolve(dirname(fileURLToPath(import.meta.url)), "../../.env");
        this.config = {
            baseUrl: "https://open-api.tiktokglobalshop.com",
            apiVersion: "202309",
            envPath: defaultEnvPath,
            ...config,
        };
    }
    generateSign(path, params, body) {
        // 1. Exclude 'sign' and 'access_token' from params
        const filteredParams = Object.entries(params)
            .filter(([key]) => key !== "sign" && key !== "access_token")
            .sort(([a], [b]) => a.localeCompare(b));
        // 2. Concatenate sorted key-value pairs
        const paramString = filteredParams.map(([k, v]) => `${k}${v}`).join("");
        // 3. Include body for POST requests (required by TikTok API)
        const bodyString = body ? JSON.stringify(body) : "";
        // 4. Build sign string: secret + path + params + body + secret
        const signString = this.config.appSecret + path + paramString + bodyString + this.config.appSecret;
        // 5. HMAC-SHA256 hex
        return crypto
            .createHmac("sha256", this.config.appSecret)
            .update(signString)
            .digest("hex");
    }
    /**
     * Uses the stored refresh_token to obtain a new access_token.
     * Persists the new tokens (and new expires_at) back to the .env file.
     * Concurrent callers share the same in-flight promise so we don't
     * hammer the refresh endpoint.
     */
    async refreshAccessToken() {
        if (this.refreshPromise) {
            return this.refreshPromise;
        }
        this.refreshPromise = this.doRefresh().finally(() => {
            this.refreshPromise = null;
        });
        return this.refreshPromise;
    }
    async doRefresh() {
        if (!this.config.refreshToken) {
            throw new Error("No refresh_token available. Run `npm run auth` in tiktokshop_mcp/ to re-authenticate.");
        }
        const params = new URLSearchParams({
            app_key: this.config.appKey,
            app_secret: this.config.appSecret,
            refresh_token: this.config.refreshToken,
            grant_type: "refresh_token",
        });
        const url = `https://auth.tiktok-shops.com/api/v2/token/refresh?${params}`;
        console.error("[TikTokShopClient] Refreshing access_token…");
        const response = await fetch(url, { method: "GET" });
        const text = await response.text();
        let data;
        try {
            data = JSON.parse(text);
        }
        catch {
            throw new Error(`Token refresh failed: non-JSON response (${response.status}): ${text.slice(0, 200)}`);
        }
        if (data.code !== 0 || !data.data) {
            throw new Error(`Token refresh failed (code=${data.code}): ${data.message ?? "unknown"}. ` +
                `The refresh_token itself may have expired — run \`npm run auth\` in tiktokshop_mcp/.`);
        }
        this.config.accessToken = data.data.access_token;
        this.config.refreshToken = data.data.refresh_token;
        this.config.expiresAt =
            Math.floor(Date.now() / 1000) + data.data.access_token_expire_in;
        this.persistTokensToEnv();
        console.error(`[TikTokShopClient] access_token refreshed, new expiry at ${new Date(this.config.expiresAt * 1000).toISOString()}`);
    }
    /** Update 3 keys in the .env file, preserving other lines intact. */
    persistTokensToEnv() {
        const envPath = this.config.envPath;
        const existing = existsSync(envPath) ? readFileSync(envPath, "utf-8") : "";
        const lines = existing.split("\n");
        const updates = {
            TIKTOK_SHOP_ACCESS_TOKEN: this.config.accessToken,
            TIKTOK_SHOP_REFRESH_TOKEN: this.config.refreshToken ?? "",
            TIKTOK_SHOP_EXPIRES_AT: String(this.config.expiresAt ?? ""),
        };
        const result = [...lines];
        for (const [key, value] of Object.entries(updates)) {
            const idx = result.findIndex((l) => l.startsWith(`${key}=`));
            const line = `${key}=${value}`;
            if (idx >= 0)
                result[idx] = line;
            else
                result.push(line);
        }
        // Strip trailing empty lines, then end with exactly one newline.
        while (result.length > 0 && result[result.length - 1].trim() === "") {
            result.pop();
        }
        writeFileSync(envPath, result.join("\n") + "\n");
    }
    async request(method, path, params, body, retried = false) {
        // Proactive refresh if token is known to be expiring within 60s.
        const now = Math.floor(Date.now() / 1000);
        if (this.config.expiresAt &&
            this.config.expiresAt < now + 60 &&
            this.config.refreshToken) {
            await this.refreshAccessToken();
        }
        const timestamp = Math.floor(Date.now() / 1000).toString();
        const queryParams = {
            app_key: this.config.appKey,
            timestamp,
            access_token: this.config.accessToken,
            ...params,
        };
        if (this.config.shopCipher) {
            queryParams.shop_cipher = this.config.shopCipher;
        }
        const fullPath = `/${path}`;
        const sign = this.generateSign(fullPath, queryParams, body);
        queryParams.sign = sign;
        const queryString = new URLSearchParams(queryParams).toString();
        const url = `${this.config.baseUrl}${fullPath}?${queryString}`;
        const headers = {
            "Content-Type": "application/json",
            "x-tts-access-token": this.config.accessToken,
        };
        const fetchOptions = { method, headers };
        if (body) {
            fetchOptions.body = JSON.stringify(body);
        }
        if (method === "POST") {
            console.error("[DEBUG] POST URL:", url);
            console.error("[DEBUG] POST body:", fetchOptions.body);
        }
        const response = await fetch(url, fetchOptions);
        const responseText = await response.text();
        if (method === "POST") {
            console.error("[DEBUG] POST response:", responseText);
        }
        let data;
        try {
            data = JSON.parse(responseText);
        }
        catch {
            throw new Error(`TikTok Shop API error: ${response.status} - ${responseText.slice(0, 200)}`);
        }
        // Reactive refresh: 105002 = expired access_token. Retry once.
        if (data.code === 105002 && !retried && this.config.refreshToken) {
            console.error("[TikTokShopClient] Got 105002 expired token — refreshing and retrying once.");
            await this.refreshAccessToken();
            return this.request(method, path, params, body, true);
        }
        return data;
    }
    async get(path, params) {
        return this.request("GET", path, params);
    }
    async post(path, params, body) {
        return this.request("POST", path, params, body);
    }
}
export function createClientFromEnv() {
    const appKey = process.env.TIKTOK_SHOP_APP_KEY;
    const appSecret = process.env.TIKTOK_SHOP_APP_SECRET;
    const accessToken = process.env.TIKTOK_SHOP_ACCESS_TOKEN;
    const refreshToken = process.env.TIKTOK_SHOP_REFRESH_TOKEN;
    const shopCipher = process.env.TIKTOK_SHOP_SHOP_CIPHER;
    const expiresAtStr = process.env.TIKTOK_SHOP_EXPIRES_AT;
    if (!appKey || !appSecret || !accessToken) {
        throw new Error("Missing required environment variables: TIKTOK_SHOP_APP_KEY, TIKTOK_SHOP_APP_SECRET, TIKTOK_SHOP_ACCESS_TOKEN");
    }
    return new TikTokShopClient({
        appKey,
        appSecret,
        accessToken,
        refreshToken: refreshToken || undefined,
        expiresAt: expiresAtStr ? parseInt(expiresAtStr, 10) : undefined,
        shopCipher,
    });
}
//# sourceMappingURL=client.js.map