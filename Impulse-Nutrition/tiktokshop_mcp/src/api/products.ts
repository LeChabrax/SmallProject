import type { TikTokShopClient } from "./client.js";

export interface ProductSearchParams {
  page_size?: number;
  page_token?: string;
  status?: string;
}

export async function searchProducts(
  client: TikTokShopClient,
  params: ProductSearchParams
) {
  const queryParams: Record<string, string> = {
    page_size: String(params.page_size ?? 20),
  };
  if (params.page_token) queryParams.page_token = params.page_token;
  if (params.status) queryParams.status = params.status;

  const response = await client.post(
    "product/202309/products/search",
    queryParams
  );

  if (response.code !== 0) {
    throw new Error(`TikTok API error (${response.code}): ${response.message}`);
  }

  return response.data;
}

export async function getProductDetail(
  client: TikTokShopClient,
  productIds: string[]
) {
  const response = await client.get(
    "product/202309/products",
    { ids: productIds.join(",") }
  );

  if (response.code !== 0) {
    throw new Error(`TikTok API error (${response.code}): ${response.message}`);
  }

  return response.data;
}
