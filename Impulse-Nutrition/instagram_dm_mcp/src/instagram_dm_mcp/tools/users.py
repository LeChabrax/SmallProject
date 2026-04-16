"""User lookup tools: id<->username, user info, online status, search."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def register(mcp, client) -> None:
    @mcp.tool()
    def get_user_id_from_username(username: str) -> Dict[str, Any]:
        """Get the Instagram user ID for a given username.

        Args:
            username: Instagram username.
        Returns:
            A dictionary with success status and the user ID or error message.
        """
        if not username:
            return {"success": False, "message": "Username must be provided."}
        try:
            user_id = client.user_id_from_username(username)
            if user_id:
                return {"success": True, "user_id": user_id}
            else:
                return {"success": False, "message": f"User '{username}' not found."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def get_username_from_user_id(user_id: str) -> Dict[str, Any]:
        """Get the Instagram username for a given user ID.

        Args:
            user_id: Instagram user ID.
        Returns:
            A dictionary with success status and the username or error message.
        """
        if not user_id:
            return {"success": False, "message": "User ID must be provided."}
        try:
            username = client.username_from_user_id(user_id)
            if username:
                return {"success": True, "username": username}
            else:
                return {"success": False, "message": f"User ID '{user_id}' not found."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def get_user_info(username: str) -> Dict[str, Any]:
        """Get detailed information about an Instagram user.

        Args:
            username: Instagram username to get information about.
        Returns:
            A dictionary with success status and user information.
        """
        if not username:
            return {"success": False, "message": "Username must be provided."}

        try:
            user = client.user_info_by_username(username)
            if user:
                user_data = {
                    "user_id": str(user.pk),
                    "username": user.username,
                    "full_name": user.full_name,
                    "biography": user.biography,
                    "follower_count": user.follower_count,
                    "following_count": user.following_count,
                    "media_count": user.media_count,
                    "is_private": user.is_private,
                    "is_verified": user.is_verified,
                    "profile_pic_url": str(user.profile_pic_url) if user.profile_pic_url else None,
                    "external_url": str(user.external_url) if user.external_url else None,
                    "category": user.category,
                }
                return {"success": True, "user_info": user_data}
            else:
                return {"success": False, "message": f"User '{username}' not found."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def check_user_online_status(usernames: List[str]) -> Dict[str, Any]:
        """Check the online status of Instagram users.

        Args:
            usernames: List of Instagram usernames to check status for.
        Returns:
            A dictionary with success status and users' presence information.
        """
        if not usernames or not isinstance(usernames, list):
            return {"success": False, "message": "A list of usernames must be provided."}

        try:
            user_ids = []
            username_to_id = {}

            for username in usernames:
                try:
                    user_id = client.user_id_from_username(username)
                    if user_id:
                        user_ids.append(int(user_id))
                        username_to_id[user_id] = username
                except Exception as e:
                    logger.warning("username lookup failed for %s: %s", username, e)
                    continue

            if not user_ids:
                return {"success": False, "message": "No valid users found."}

            presence_data = client.direct_users_presence(user_ids)

            result = {}
            for user_id_str, presence in presence_data.items():
                username = username_to_id.get(user_id_str, f"user_{user_id_str}")
                result[username] = presence

            return {"success": True, "presence_data": result}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def search_users(query: str) -> Dict[str, Any]:
        """Search for Instagram users by name or username.

        Args:
            query: Search term (name or username).
            count: Maximum number of users to return (default 10, max 50).
        Returns:
            A dictionary with success status and search results.
        """
        if not query:
            return {"success": False, "message": "Search query must be provided."}

        try:
            users = client.search_users(query)

            user_results = []
            for user in users:
                user_data = {
                    "user_id": str(user.pk),
                    "username": user.username,
                    "full_name": user.full_name,
                    "is_private": user.is_private,
                    "profile_pic_url": str(user.profile_pic_url) if user.profile_pic_url else None,
                    "follower_count": getattr(user, 'follower_count', None),
                }
                user_results.append(user_data)

            return {"success": True, "users": user_results, "count": len(user_results)}
        except Exception as e:
            return {"success": False, "message": str(e)}
