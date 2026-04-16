"""DM thread tools: list_chats, list_messages, thread lookup, search, mark seen, pending."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..compact import (
    _compact_message,
    _compact_user,
    _compute_thread_signals,
    _scan_messages,
    _sort_messages_newest_first,
)

logger = logging.getLogger(__name__)


def register(mcp, client) -> None:
    @mcp.tool()
    def list_chats(
        amount: int = 20,
        selected_filter: str = "",
        thread_message_limit: Optional[int] = None,
        full: bool = False,
        fields: Optional[List[str]] = None,
        compact: bool = True,
    ) -> Dict[str, Any]:
        """Get Instagram Direct Message threads (chats) from the user's account, with optional filters and limits.

        Args:
            amount: Number of threads to fetch (default 20).
            selected_filter: Filter for threads ("", "flagged", or "unread").
            thread_message_limit: Limit for messages per thread.
            full: If True, return the full thread object for each chat (default False).
            fields: If provided, return only these fields for each thread.
            compact: If True (default), strip messages and users to essential fields only. Saves ~10x context tokens.
        Returns:
            A dictionary with success status and the list of threads or error message.
        """
        def thread_summary(thread):
            t = thread if isinstance(thread, dict) else thread.dict()
            users = t.get("users", [])
            user_summaries = [_compact_user(u) for u in users]

            # thread.messages only contains the first N messages (Instagrapi default,
            # typically 10), so using [-1] on it returns an old opening message, not
            # the real last message of the thread. Fetch 3 via API and sort desc.
            thread_id = t.get("id")
            last_msg = None
            try:
                messages = client.direct_messages(thread_id, amount=3)
                if messages:
                    msg_dicts = [
                        m.dict() if hasattr(m, 'dict') else (m if isinstance(m, dict) else {})
                        for m in messages
                    ]
                    msg_dicts = _sort_messages_newest_first(msg_dicts)
                    last_msg = _compact_message(msg_dicts[0]) if compact else msg_dicts[0]
            except Exception as e:
                logger.warning("thread_summary: failed to fetch last message for thread %s: %s", thread_id, e)

            return {
                "thread_id": thread_id,
                "thread_title": t.get("thread_title"),
                "users": user_summaries,
                "last_activity_at": t.get("last_activity_at"),
                "last_message": last_msg,
                "computed": _compute_thread_signals(last_msg, t.get("last_activity_at")),
            }

        def filter_fields(thread, fields):
            t = thread if isinstance(thread, dict) else thread.dict()
            return {field: t.get(field) for field in fields}

        try:
            threads = client.direct_threads(amount=amount, selected_filter=selected_filter, thread_message_limit=thread_message_limit)
            if full and not compact:
                return {"success": True, "threads": [t.dict() if hasattr(t, 'dict') else str(t) for t in threads]}
            elif full and compact:
                result = []
                for t in threads:
                    td = t.dict() if hasattr(t, 'dict') else t
                    td["users"] = [_compact_user(u) for u in td.get("users", [])]
                    td["messages"] = _sort_messages_newest_first(
                        [_compact_message(m) for m in td.get("messages", [])]
                    )
                    for key in ["inviter", "items", "last_permanent_item", "direct_story"]:
                        td.pop(key, None)
                    result.append(td)
                return {"success": True, "threads": result, "ordering": "newest_first"}
            elif fields:
                return {"success": True, "threads": [filter_fields(t, fields) for t in threads]}
            else:
                return {"success": True, "threads": [thread_summary(t) for t in threads]}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def list_messages(thread_id: str, amount: int = 20, compact: bool = True) -> Dict[str, Any]:
        """Get messages from a specific Instagram Direct Message thread by thread ID, with an optional limit.

        Args:
            thread_id: The thread ID to fetch messages from.
            amount: Number of messages to fetch (default 20).
            compact: If True (default), return only essential fields (id, user_id, timestamp, text, item_type, is_sent_by_viewer, shared_post_url). Saves ~10-15x context tokens.
        Returns:
            A dictionary with success status and the list of messages or error message.
        """
        if not thread_id:
            return {"success": False, "message": "Thread ID must be provided."}
        try:
            messages = client.direct_messages(thread_id, amount)
            result_msgs = []
            for m in messages:
                msg = m.dict() if hasattr(m, 'dict') else (m if isinstance(m, dict) else {})
                item_type = getattr(m, 'item_type', None) or msg.get('item_type')
                shared_info = None
                shared_url = None
                shared_code = None
                if item_type in ["clip", "media_share", "reel_share", "xma_media_share", "post_share", "story_share"]:
                    clip = getattr(m, 'clip', None) or msg.get('clip')
                    media_share = getattr(m, 'media_share', None) or msg.get('media_share')
                    xma = getattr(m, 'xma_media_share', None) or msg.get('xma_media_share')
                    post_share = getattr(m, 'post_share', None) or msg.get('post_share')
                    for obj in [clip, media_share, xma, post_share]:
                        if obj:
                            shared_code = obj.get('code') or obj.get('pk')
                            shared_url = obj.get('url') or (f"https://www.instagram.com/reel/{shared_code}/" if shared_code else None)
                            shared_info = obj
                            break
                msg['item_type'] = item_type
                msg['shared_post_info'] = shared_info
                msg['shared_post_url'] = shared_url
                msg['shared_post_code'] = shared_code

                if compact:
                    result_msgs.append(_compact_message(msg))
                else:
                    result_msgs.append(msg)
            result_msgs = _sort_messages_newest_first(result_msgs)
            scan = _scan_messages(result_msgs)
            return {
                "success": True,
                "messages": result_msgs,
                "ordering": "newest_first",
                "scan": scan,
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def mark_message_seen(thread_id: str, message_id: str) -> Dict[str, Any]:
        """Mark a message as seen in a direct message thread.

        Args:
            thread_id: The thread ID containing the message.
            message_id: The ID of the message to mark as seen.
        Returns:
            A dictionary with success status and a status message.
        """
        if not thread_id or not message_id:
            return {"success": False, "message": "Both thread_id and message_id must be provided."}

        try:
            result = client.direct_message_seen(int(thread_id), int(message_id))
            if result:
                return {"success": True, "message": "Message marked as seen."}
            else:
                return {"success": False, "message": "Failed to mark message as seen."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def list_pending_chats(amount: int = 20) -> Dict[str, Any]:
        """Get Instagram Direct Message threads (chats) from the user's pending inbox.

        Args:
            amount: Number of pending threads to fetch (default 20).
        Returns:
            A dictionary with success status and the list of pending threads or error message.
        """
        try:
            threads = client.direct_pending_inbox(amount)
            result = []
            for t in threads:
                td = t.dict() if hasattr(t, 'dict') else t
                if isinstance(td, dict):
                    td["users"] = [_compact_user(u) for u in td.get("users", [])]
                    td["messages"] = [_compact_message(m) for m in td.get("messages", [])]
                    for key in ["inviter", "items", "last_permanent_item", "direct_story"]:
                        td.pop(key, None)
                result.append(td)
            return {"success": True, "threads": result}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def search_threads(query: str) -> Dict[str, Any]:
        """Search Instagram Direct Message threads by username or keyword.

        Args:
            query: The search term (username or keyword).
        Returns:
            A dictionary with success status and the search results or error message.
        """
        if not query:
            return {"success": False, "message": "Query must be provided."}
        try:
            results = client.direct_search(query)
            return {"success": True, "results": [r.dict() if hasattr(r, 'dict') else str(r) for r in results]}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def get_thread_by_participants(user_ids: List[int]) -> Dict[str, Any]:
        """Get an Instagram Direct Message thread by participant user IDs.

        Args:
            user_ids: List of user IDs (ints).
        Returns:
            A dictionary with success status and the thread or error message.
        """
        if not user_ids or not isinstance(user_ids, list):
            return {"success": False, "message": "user_ids must be a non-empty list of user IDs."}
        try:
            thread = client.direct_thread_by_participants(user_ids)
            td = thread.dict() if hasattr(thread, 'dict') else (thread if isinstance(thread, dict) else str(thread))
            if isinstance(td, dict):
                td["users"] = [_compact_user(u) for u in td.get("users", [])]
                td["messages"] = _sort_messages_newest_first(
                    [_compact_message(m) for m in td.get("messages", [])]
                )
                for key in ["inviter", "items", "last_permanent_item", "direct_story"]:
                    td.pop(key, None)
            return {"success": True, "thread": td, "ordering": "newest_first"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def get_thread_details(thread_id: str, amount: int = 20, compact: bool = True) -> Dict[str, Any]:
        """Get details and messages for a specific Instagram Direct Message thread by thread ID, with an optional message limit.

        Args:
            thread_id: The thread ID to fetch details for.
            amount: Number of messages to fetch (default 20).
            compact: If True (default), strip messages and users to essential fields. Saves ~10-15x context tokens.
        Returns:
            A dictionary with success status and the thread details or error message.
        """
        if not thread_id:
            return {"success": False, "message": "Thread ID must be provided."}
        try:
            thread = client.direct_thread(thread_id, amount)
            td = thread.dict() if hasattr(thread, 'dict') else (thread if isinstance(thread, dict) else str(thread))
            if compact and isinstance(td, dict):
                td["users"] = [_compact_user(u) for u in td.get("users", [])]
                td["messages"] = _sort_messages_newest_first(
                    [_compact_message(m) for m in td.get("messages", [])]
                )
                for key in ["inviter", "items", "last_permanent_item", "direct_story"]:
                    td.pop(key, None)
            elif isinstance(td, dict):
                td["messages"] = _sort_messages_newest_first(td.get("messages", []))
            return {"success": True, "thread": td, "ordering": "newest_first"}
        except Exception as e:
            return {"success": False, "message": str(e)}
