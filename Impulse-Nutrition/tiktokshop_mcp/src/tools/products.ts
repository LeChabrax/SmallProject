import { z } from "zod";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { TikTokShopClient } from "../api/client.js";
import { searchProducts, getProductDetail } from "../api/products.js";

export function registerProductTools(server: McpServer, client: TikTokShopClient) {
  server.registerTool(
    "list_products",
    {
      title: "List Products",
      description:
        "List TikTok Shop products with optional filters. Returns product summaries including title, status, SKUs, pricing, and inventory/stock quantities.",
      inputSchema: {
        page_size: z.number().min(1).max(100).optional().describe("Number of products per page (1-100, default 20)"),
        page_token: z.string().optional().describe("Pagination token from a previous response"),
        status: z.enum([
          "DRAFT",
          "PENDING",
          "FAILED",
          "ACTIVATE",
          "SELLER_DEACTIVATED",
          "PLATFORM_DEACTIVATED",
          "FREEZE",
          "DELETED",
        ]).optional().describe("Filter by product status"),
      },
    },
    async (args) => {
      try {
        const result = await searchProducts(client, args);
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
    "get_product_detail",
    {
      title: "Get Product Details",
      description:
        "Get detailed information about one or more products by their IDs, including SKUs, inventory levels, pricing, and images.",
      inputSchema: {
        product_ids: z.array(z.string()).min(1).max(50).describe("List of product IDs to retrieve (max 50)"),
      },
    },
    async ({ product_ids }) => {
      try {
        const result = await getProductDetail(client, product_ids);
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
