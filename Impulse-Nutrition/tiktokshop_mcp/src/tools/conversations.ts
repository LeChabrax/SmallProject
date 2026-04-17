import { z } from "zod";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { TikTokShopClient } from "../api/client.js";
import { listConversations, getConversationMessages, sendMessage } from "../api/conversations.js";

export function registerConversationTools(server: McpServer, client: TikTokShopClient) {
  server.registerTool(
    "list_conversations",
    {
      title: "List Conversations",
      description: "List customer service conversations with last message, unread count, and participant info.",
      inputSchema: {
        page_size: z.number().min(1).max(50).optional().describe("Number of conversations per page (1-50, default 20)"),
        page_token: z.string().optional().describe("Pagination token from a previous response"),
      },
    },
    async ({ page_size, page_token }) => {
      try {
        const result = await listConversations(client, page_size, page_token);
        return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
      } catch (error) {
        return { content: [{ type: "text" as const, text: `Error: ${error instanceof Error ? error.message : String(error)}` }], isError: true };
      }
    }
  );

  server.registerTool(
    "read_conversation",
    {
      title: "Read Conversation Messages",
      description: "Read messages in a specific customer service conversation.",
      inputSchema: {
        conversation_id: z.string().describe("The conversation ID to read messages from"),
        page_size: z.number().min(1).max(10).optional().describe("Number of messages per page (1-10, default 10)"),
        page_token: z.string().optional().describe("Pagination token from a previous response"),
      },
    },
    async ({ conversation_id, page_size, page_token }) => {
      try {
        const result = await getConversationMessages(client, conversation_id, page_size, page_token);
        return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
      } catch (error) {
        return { content: [{ type: "text" as const, text: `Error: ${error instanceof Error ? error.message : String(error)}` }], isError: true };
      }
    }
  );

  server.registerTool(
    "reply_to_conversation",
    {
      title: "Reply to Conversation",
      description: "Send a text message reply in a customer service conversation.",
      inputSchema: {
        conversation_id: z.string().describe("The conversation ID to reply to"),
        content: z.string().min(1).describe("The text message to send to the customer"),
      },
    },
    async ({ conversation_id, content }) => {
      try {
        const result = await sendMessage(client, conversation_id, content);
        return { content: [{ type: "text" as const, text: `Message sent successfully. ${JSON.stringify(result)}` }] };
      } catch (error) {
        return { content: [{ type: "text" as const, text: `Error: ${error instanceof Error ? error.message : String(error)}` }], isError: true };
      }
    }
  );
}
