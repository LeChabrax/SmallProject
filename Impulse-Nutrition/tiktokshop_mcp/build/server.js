import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { createClientFromEnv } from "./api/client.js";
import { registerOrderTools } from "./tools/orders.js";
import { registerConversationTools } from "./tools/conversations.js";
import { registerProductTools } from "./tools/products.js";
export function createServer() {
    const server = new McpServer({
        name: "mcp-tiktokshop",
        version: "0.2.0",
    });
    const client = createClientFromEnv();
    registerOrderTools(server, client);
    registerConversationTools(server, client);
    registerProductTools(server, client);
    return server;
}
//# sourceMappingURL=server.js.map