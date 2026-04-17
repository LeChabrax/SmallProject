#!/usr/bin/env node

/**
 * Interactive OAuth setup script for TikTok Shop MCP.
 *
 * Usage:
 *   npm run auth
 *
 * Steps:
 *   1. Opens the TikTok authorization page in your browser
 *   2. You authorize and get redirected (copy the code from the URL)
 *   3. Paste the code here — the script exchanges it for tokens
 *   4. Fetches your shop_cipher automatically
 *   5. Writes everything to .env
 */

import { createInterface } from "node:readline";
import { writeFileSync, existsSync, readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ENV_PATH = resolve(__dirname, "../../.env");

function prompt(question: string): Promise<string> {
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

function loadExistingEnv(): Record<string, string> {
  if (!existsSync(ENV_PATH)) return {};
  const content = readFileSync(ENV_PATH, "utf-8");
  const env: Record<string, string> = {};
  for (const line of content.split("\n")) {
    const match = line.match(/^([^=]+)=(.*)$/);
    if (match) env[match[1]] = match[2];
  }
  return env;
}

function saveEnv(vars: Record<string, string>) {
  const lines = Object.entries(vars)
    .map(([k, v]) => `${k}=${v}`)
    .join("\n");
  writeFileSync(ENV_PATH, lines + "\n");
}

async function getAccessToken(
  appKey: string,
  appSecret: string,
  authCode: string
): Promise<{ access_token: string; refresh_token: string; expires_at: number }> {
  // TikTok Shop uses GET with query params for token exchange
  const params = new URLSearchParams({
    app_key: appKey,
    app_secret: appSecret,
    auth_code: authCode,
    grant_type: "authorized_code",
  });

  const url = `https://auth.tiktok-shops.com/api/v2/token/get?${params}`;
  console.error(`  Calling: ${url.replace(appSecret, "***")}`);

  const response = await fetch(url, { method: "GET" });
  const rawText = await response.text();

  console.error(`  Response status: ${response.status}`);

  let data: Record<string, unknown>;
  try {
    data = JSON.parse(rawText);
  } catch {
    throw new Error(`Response is not JSON (${response.status}): ${rawText.slice(0, 200)}`);
  }

  if ((data as { code?: number }).code !== 0) {
    throw new Error(`Token exchange failed: ${(data as { message?: string }).message} (code ${(data as { code?: number }).code})`);
  }

  const tokenData = (data as { data: Record<string, unknown> }).data;
  console.error(`  Token length: ${(tokenData.access_token as string).length} chars`);
  // Show all fields returned (may include shop info)
  const fieldNames = Object.keys(tokenData).filter(k => k !== "access_token" && k !== "refresh_token");
  if (fieldNames.length > 0) {
    console.log("\n  Extra fields from token response:");
    for (const key of fieldNames) {
      console.log(`    ${key}: ${JSON.stringify(tokenData[key])}`);
    }
  }

  const expireIn = (tokenData.access_token_expire_in as number | undefined) ?? 0;
  return {
    access_token: tokenData.access_token as string,
    refresh_token: (tokenData.refresh_token as string) ?? "",
    expires_at: expireIn ? Math.floor(Date.now() / 1000) + expireIn : 0,
  };
}

async function getAuthorizedShops(
  appKey: string,
  appSecret: string,
  accessToken: string
): Promise<Array<{ shop_id: string; shop_name: string; shop_cipher: string; region: string }>> {
  // Build signed request for /authorization/202309/shops
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const path = "/authorization/202309/shops";

  const { createHmac } = await import("node:crypto");

  // Params to include in signing (exclude sign and access_token)
  const params: Record<string, string> = {
    app_key: appKey,
    timestamp,
  };

  const sortedEntries = Object.entries(params).sort(([a], [b]) =>
    a.localeCompare(b)
  );
  const paramString = sortedEntries.map(([k, v]) => `${k}${v}`).join("");

  // TikTok Shop sign: secret + path + params + secret
  const signString = appSecret + path + paramString + appSecret;
  console.error(`  Sign string: ${appSecret.slice(0, 4)}...${path}${paramString}${appSecret.slice(0, 4)}...`);

  const sign = createHmac("sha256", appSecret)
    .update(signString)
    .digest("hex");

  const queryParams = new URLSearchParams({
    ...params,
    sign,
    access_token: accessToken,
  });

  const url = `https://open-api.tiktokglobalshop.com${path}?${queryParams}`;
  console.error(`  Calling: ${url.slice(0, 100)}...`);

  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "x-tts-access-token": accessToken,
    },
  });

  const rawText = await response.text();
  console.error(`  Response (${response.status}): ${rawText.slice(0, 300)}`);

  let data: Record<string, unknown>;
  try {
    data = JSON.parse(rawText);
  } catch {
    throw new Error(`Response is not JSON (${response.status}): ${rawText.slice(0, 200)}`);
  }

  if ((data as { code?: number }).code !== 0) {
    throw new Error(`Get shops failed: ${(data as { message?: string }).message} (code ${(data as { code?: number }).code})`);
  }

  // Handle different response formats
  const responseData = (data as { data?: Record<string, unknown> }).data ?? {};
  const shops = (responseData.shops ?? responseData.shop_list ?? []) as Array<Record<string, string>>;

  return shops.map((s) => ({
    shop_id: s.id ?? s.shop_id ?? "",
    shop_name: s.name ?? s.shop_name ?? "",
    shop_cipher: s.cipher ?? s.shop_cipher ?? "",
    region: s.region ?? "",
  }));
}

async function doOAuthFlow(
  appKey: string,
  appSecret: string
): Promise<{ access_token: string; refresh_token: string; expires_at: number }> {
  const authUrl = `https://services.tiktokshop.com/open/authorize?app_key=${appKey}&state=mcp_setup`;

  console.log("\n--- Authorize your shop ---");
  console.log("Open this URL in your browser:\n");
  console.log(`  ${authUrl}\n`);
  console.log("After authorizing, copy the 'code' parameter from the redirect URL.\n");

  const authCode = await prompt("Paste the authorization code here: ");
  if (!authCode) {
    console.error("Authorization code is required.");
    process.exit(1);
  }

  console.log("\nExchanging code for access token...");
  const tokens = await getAccessToken(appKey, appSecret, authCode);
  console.log("Access token obtained!");
  return tokens;
}

async function main() {
  console.log("\n🔐 TikTok Shop MCP — OAuth Setup\n");

  const env = loadExistingEnv();

  // Step 1: Get app credentials
  const appKey =
    env.TIKTOK_SHOP_APP_KEY ||
    (await prompt("App Key (from Partner Center): "));
  const appSecret =
    env.TIKTOK_SHOP_APP_SECRET ||
    (await prompt("App Secret (from Partner Center): "));

  if (!appKey || !appSecret) {
    console.error("App Key and App Secret are required.");
    process.exit(1);
  }

  // Step 2: Get access token (reuse existing or get new one)
  let tokens: { access_token: string; refresh_token: string; expires_at: number };

  if (env.TIKTOK_SHOP_ACCESS_TOKEN) {
    console.log("\nExisting access token found in .env");
    const reuse = await prompt("Reuse it? (y/n): ");
    if (reuse.toLowerCase() === "y") {
      tokens = {
        access_token: env.TIKTOK_SHOP_ACCESS_TOKEN,
        refresh_token: env.TIKTOK_SHOP_REFRESH_TOKEN || "",
        expires_at: env.TIKTOK_SHOP_EXPIRES_AT
          ? parseInt(env.TIKTOK_SHOP_EXPIRES_AT, 10)
          : 0,
      };
      console.log("Using existing access token.");
    } else {
      tokens = await doOAuthFlow(appKey, appSecret);
    }
  } else {
    tokens = await doOAuthFlow(appKey, appSecret);
  }

  // Step 4: Get shop cipher
  let shopCipher = "";

  console.log("\n--- Step 3: Fetching your shops... ---");
  try {
    const shops = await getAuthorizedShops(
      appKey,
      appSecret,
      tokens.access_token
    );

    if (shops.length === 1) {
      console.log(`Found shop: ${shops[0].shop_name} (${shops[0].region})`);
      shopCipher = shops[0].shop_cipher;
    } else if (shops.length > 1) {
      console.log("\nMultiple shops found:");
      shops.forEach((s, i) =>
        console.log(`  ${i + 1}. ${s.shop_name} (${s.region})`)
      );
      const choice = await prompt(`\nChoose a shop (1-${shops.length}): `);
      const index = parseInt(choice, 10) - 1;
      if (index >= 0 && index < shops.length) {
        shopCipher = shops[index].shop_cipher;
      }
    }
  } catch (error) {
    console.log(`\n  Could not fetch shops automatically: ${error instanceof Error ? error.message : String(error)}`);
  }

  if (!shopCipher) {
    console.log("\n  To find your shop_cipher manually:");
    console.log("  1. Go to TikTok Shop Seller Center");
    console.log("  2. Check the URL or use the API Testing Tool in Partner Center");
    console.log("  3. Or leave empty for now (some endpoints work without it)\n");
    shopCipher = await prompt("Shop cipher (or press Enter to skip): ");
  }

  // Step 5: Save to .env
  const newEnv: Record<string, string> = {
    TIKTOK_SHOP_APP_KEY: appKey,
    TIKTOK_SHOP_APP_SECRET: appSecret,
    TIKTOK_SHOP_ACCESS_TOKEN: tokens.access_token,
    TIKTOK_SHOP_REFRESH_TOKEN: tokens.refresh_token,
    TIKTOK_SHOP_EXPIRES_AT: String(tokens.expires_at),
    TIKTOK_SHOP_SHOP_CIPHER: shopCipher,
  };

  saveEnv(newEnv);
  console.log(`\n✅ Configuration saved to ${ENV_PATH}`);
  console.log("\nYou can now use the MCP server:");
  console.log("  npm run build && npm start");
  console.log(
    "\nOr add it to your Claude Desktop/Claude Code configuration."
  );
}

main().catch((error) => {
  console.error("\nError:", error.message);
  process.exit(1);
});
