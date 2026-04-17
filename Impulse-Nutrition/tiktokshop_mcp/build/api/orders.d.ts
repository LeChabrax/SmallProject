import type { TikTokShopClient } from "./client.js";
export interface OrderSearchParams {
    page_size?: number;
    page_token?: string;
    order_status?: string;
    sort_field?: string;
    sort_order?: string;
}
export declare function searchOrders(client: TikTokShopClient, params: OrderSearchParams): Promise<unknown>;
export declare function getOrderDetail(client: TikTokShopClient, orderIds: string[]): Promise<unknown>;
//# sourceMappingURL=orders.d.ts.map