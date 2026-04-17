import { z } from "zod";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { TikTokShopClient } from "../api/client.js";
import { searchOrders, getOrderDetail } from "../api/orders.js";

export function registerOrderTools(server: McpServer, client: TikTokShopClient) {
  server.registerTool(
    "list_orders",
    {
      title: "List Orders",
      description:
        "List TikTok Shop orders with optional filters. Returns order summaries including status, total amount, items, and buyer info.",
      inputSchema: {
        page_size: z.number().min(1).max(50).optional().describe("Number of orders per page (1-50, default 20)"),
        page_token: z.string().optional().describe("Pagination token from a previous response"),
        order_status: z.string().optional().describe("Filter by status: UNPAID, ON_HOLD, AWAITING_SHIPMENT, AWAITING_COLLECTION, PARTIALLY_SHIPPING, IN_TRANSIT, DELIVERED, COMPLETED, CANCELLED"),
        sort_field: z.enum(["create_time", "update_time"]).optional().describe("Sort field"),
        sort_order: z.enum(["ASC", "DESC"]).optional().describe("Sort direction"),
      },
    },
    async (args) => {
      try {
        const result = await searchOrders(client, args);
        return {
          content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }],
        };
      } catch (error) {
        return {
          content: [{ type: "text" as const, text: `Error: ${error instanceof Error ? error.message : String(error)}` }],
          isError: true,
        };
      }
    }
  );

  server.registerTool(
    "get_order_detail",
    {
      title: "Get Order Details",
      description:
        "Get detailed information about one or more orders by their IDs.",
      inputSchema: {
        order_ids: z.array(z.string()).min(1).max(50).describe("List of order IDs to retrieve (max 50)"),
      },
    },
    async ({ order_ids }) => {
      try {
        const result = await getOrderDetail(client, order_ids);
        return {
          content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }],
        };
      } catch (error) {
        return {
          content: [{ type: "text" as const, text: `Error: ${error instanceof Error ? error.message : String(error)}` }],
          isError: true,
        };
      }
    }
  );
}
