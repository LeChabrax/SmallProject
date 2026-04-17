export async function listConversations(client, pageSize, pageToken) {
    const params = {
        page_size: String(pageSize ?? 20),
    };
    if (pageToken)
        params.page_token = pageToken;
    const response = await client.get("customer_service/202309/conversations", params);
    if (response.code !== 0) {
        throw new Error(`TikTok API error (${response.code}): ${response.message}`);
    }
    return response.data;
}
export async function getConversationMessages(client, conversationId, pageSize, pageToken) {
    const params = {
        page_size: String(pageSize ?? 20),
    };
    if (pageToken)
        params.page_token = pageToken;
    const response = await client.get(`customer_service/202309/conversations/${conversationId}/messages`, params);
    if (response.code !== 0) {
        throw new Error(`TikTok API error (${response.code}): ${response.message}`);
    }
    return response.data;
}
export async function sendMessage(client, conversationId, content) {
    // Two bugs fixed 2026-04-13 after empirical testing against the live API:
    //
    // 1. `conversation_id` must NOT be in the body — it lives only in the URL
    //    path. A body field was being interpreted as a *short* conv_id and
    //    triggered `45101003: invalid conv_short_id`.
    //
    // 2. For `type: "TEXT"`, the `content` field must itself be a JSON-string
    //    `{"content": "<text>"}`, NOT plain text. TikTok stores messages as
    //    typed payloads (TEXT / IMAGE / PRODUCT_CARD / ...) where the `content`
    //    holds the payload of the chosen type. Plain text triggers
    //    `45101001: input params err`. Confirmed by reading the shape of
    //    stored messages in `read_conversation` responses and by a direct
    //    HTTPS POST test that succeeded with wrapping (code:0, Success).
    const response = await client.post(`customer_service/202309/conversations/${conversationId}/messages`, {}, {
        type: "TEXT",
        content: JSON.stringify({ content }),
    });
    if (response.code !== 0) {
        throw new Error(`TikTok API error (${response.code}): ${response.message}`);
    }
    return response.data;
}
//# sourceMappingURL=conversations.js.map