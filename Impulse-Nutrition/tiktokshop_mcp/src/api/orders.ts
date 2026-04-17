import type { TikTokShopClient } from "./client.js";

export interface OrderSearchParams {
  page_size?: number;
  page_token?: string;
  order_status?: string;
  sort_field?: string;
  sort_order?: string;
}

export async function searchOrders(
  client: TikTokShopClient,
  params: OrderSearchParams
) {
  const queryParams: Record<string, string> = {
    page_size: String(params.page_size ?? 20),
  };
  if (params.page_token) queryParams.page_token = params.page_token;
  if (params.order_status) queryParams.order_status = params.order_status;
  if (params.sort_field) queryParams.sort_field = params.sort_field;
  if (params.sort_order) queryParams.sort_order = params.sort_order;

  const response = await client.post(
    "order/202309/orders/search",
    queryParams
  );

  if (response.code !== 0) {
    throw new Error(`TikTok API error (${response.code}): ${response.message}`);
  }

  return response.data;
}

export async function getOrderDetail(
  client: TikTokShopClient,
  orderIds: string[]
) {
  const response = await client.get(
    "order/202309/orders",
    { ids: orderIds.join(",") }
  );

  if (response.code !== 0) {
    throw new Error(`TikTok API error (${response.code}): ${response.message}`);
  }

  return response.data;
}
