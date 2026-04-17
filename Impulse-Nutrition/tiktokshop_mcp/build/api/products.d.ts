import type { TikTokShopClient } from "./client.js";
export interface ProductSearchParams {
    page_size?: number;
    page_token?: string;
    status?: string;
}
export declare function searchProducts(client: TikTokShopClient, params: ProductSearchParams): Promise<unknown>;
export declare function getProductDetail(client: TikTokShopClient, productIds: string[]): Promise<unknown>;
//# sourceMappingURL=products.d.ts.map