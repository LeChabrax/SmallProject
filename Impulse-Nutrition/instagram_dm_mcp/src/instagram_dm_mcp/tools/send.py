"""send_message, send_photo_message, send_video_message."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict


def register(mcp, client) -> None:
    @mcp.tool()
    def send_message(username: str, message: str) -> Dict[str, Any]:
        """Send an Instagram direct message to a user by username.

        Args:
            username: Instagram username of the recipient.
            message: The message text to send.
        Returns:
            A dictionary with success status and a status message.
        """
        if not username or not message:
            return {"success": False, "message": "Username and message must be provided."}
        try:
            user_id = client.user_id_from_username(username)
            if not user_id:
                return {"success": False, "message": f"User '{username}' not found."}
            dm = client.direct_send(message, [user_id])
            if dm:
                return {"success": True, "message": "Message sent to user.", "direct_message_id": getattr(dm, 'id', None)}
            else:
                return {"success": False, "message": "Failed to send message."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def send_photo_message(username: str, photo_path: str) -> Dict[str, Any]:
        """Send a photo via Instagram direct message to a user by username.

        Args:
            username: Instagram username of the recipient.
            photo_path: Path to the photo file to send.
            message: Optional message text to accompany the photo.
        Returns:
            A dictionary with success status and a status message.
        """
        if not username or not photo_path:
            return {"success": False, "message": "Username and photo_path must be provided."}

        if not os.path.exists(photo_path):
            return {"success": False, "message": f"Photo file not found: {photo_path}"}

        try:
            user_id = client.user_id_from_username(username)
            if not user_id:
                return {"success": False, "message": f"User '{username}' not found."}

            result = client.direct_send_photo(Path(photo_path), [user_id])
            if result:
                return {"success": True, "message": "Photo sent successfully.", "direct_message_id": getattr(result, 'id', None)}
            else:
                return {"success": False, "message": "Failed to send photo."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def send_video_message(username: str, video_path: str) -> Dict[str, Any]:
        """Send a video via Instagram direct message to a user by username.

        Args:
            username: Instagram username of the recipient.
            video_path: Path to the video file to send.
        Returns:
            A dictionary with success status and a status message.
        """
        if not username or not video_path:
            return {"success": False, "message": "Username and video_path must be provided."}

        if not os.path.exists(video_path):
            return {"success": False, "message": f"Video file not found: {video_path}"}

        try:
            user_id = client.user_id_from_username(username)
            if not user_id:
                return {"success": False, "message": f"User '{username}' not found."}

            result = client.direct_send_video(Path(video_path), [user_id])
            if result:
                return {"success": True, "message": "Video sent successfully.", "direct_message_id": getattr(result, 'id', None)}
            else:
                return {"success": False, "message": "Failed to send video."}
        except Exception as e:
            return {"success": False, "message": str(e)}
