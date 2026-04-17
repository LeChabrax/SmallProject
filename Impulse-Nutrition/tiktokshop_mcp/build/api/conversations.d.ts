import type { TikTokShopClient } from "./client.js";
export declare function listConversations(client: TikTokShopClient, pageSize?: number, pageToken?: string): Promise<unknown>;
export declare function getConversationMessages(client: TikTokShopClient, conversationId: string, pageSize?: number, pageToken?: string): Promise<unknown>;
export declare function sendMessage(client: TikTokShopClient, conversationId: string, content: string): Promise<unknown>;
//# sourceMappingURL=conversations.d.ts.map