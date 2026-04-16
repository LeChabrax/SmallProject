"""Misc thread ops: delete_message, mute_conversation."""

from __future__ import annotations

from typing import Any, Dict


def register(mcp, client) -> None:
    @mcp.tool()
    def delete_message(thread_id: str, message_id: str) -> Dict[str, Any]:
        """Delete a message from a direct message thread.

        Args:
            thread_id: The thread ID containing the message.
            message_id: The ID of the message to delete.
        Returns:
            A dictionary with success status and a status message.
        """
        if not thread_id or not message_id:
            return {"success": False, "message": "Both thread_id and message_id must be provided."}

        try:
            result = client.direct_message_delete(int(thread_id), int(message_id))
            if result:
                return {"success": True, "message": "Message deleted successfully."}
            else:
                return {"success": False, "message": "Failed to delete message."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def mute_conversation(thread_id: str, mute: bool = True) -> Dict[str, Any]:
        """Mute or unmute a direct message conversation.

        Args:
            thread_id: The thread ID to mute/unmute.
            mute: True to mute, False to unmute the conversation.
        Returns:
            A dictionary with success status and a status message.
        """
        if not thread_id:
            return {"success": False, "message": "Thread ID must be provided."}

        try:
            if mute:
                result = client.direct_thread_mute(int(thread_id))
                action = "muted"
            else:
                result = client.direct_thread_unmute(int(thread_id))
                action = "unmuted"

            if result:
                return {"success": True, "message": f"Conversation {action} successfully."}
            else:
                return {"success": False, "message": f"Failed to {action.rstrip('d')} conversation."}
        except Exception as e:
            return {"success": False, "message": str(e)}
