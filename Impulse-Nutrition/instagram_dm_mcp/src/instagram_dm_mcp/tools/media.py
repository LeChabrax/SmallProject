"""Media tools: get_media_info, list_media_messages, downloads."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ._helpers import (
    extract_clips_audio_from_dict,
    extract_location,
    extract_sponsor_tags_info,
    extract_usertags,
)


def register(mcp, client) -> None:
    def _ensure_download_directory(download_path: str) -> None:
        Path(download_path).mkdir(parents=True, exist_ok=True)

    def _download_single_media(media, download_path: str) -> str:
        media_type = media.media_type
        if media_type == 1:
            return str(client.photo_download(media.pk, download_path))
        elif media_type == 2:
            return str(client.video_download(media.pk, download_path))
        else:
            raise ValueError(f"Unsupported media type: {media_type}")

    def _find_message_in_thread(thread_id: str, message_id: str):
        messages = client.direct_messages(thread_id, 100)
        return next((m for m in messages if str(m.id) == message_id), None)

    @mcp.tool()
    def get_media_info(media_id: str = "", shortcode: str = "") -> Dict[str, Any]:
        """Get detailed info for a single Instagram post/reel by media ID or shortcode.

        Returns full metadata including sponsor_tags (paid partnerships),
        music/audio info, usertags, location, etc.

        Args:
            media_id: The numeric media ID (pk). Provide either this or shortcode.
            shortcode: The shortcode from an Instagram URL (e.g. 'DWTkcmdCS7n' from instagram.com/reel/DWTkcmdCS7n/). Provide either this or media_id.
        Returns:
            A dictionary with full media details.
        """
        if not media_id and not shortcode:
            return {"success": False, "message": "Provide either media_id or shortcode."}

        try:
            if shortcode and not media_id:
                media_id = str(client.media_pk_from_code(shortcode))

            media = client.media_info(int(media_id))

            result = {
                "media_id": str(media.pk),
                "code": getattr(media, "code", None),
                "media_type": media.media_type,
                "product_type": getattr(media, "product_type", None),
                "caption": media.caption_text if media.caption_text else "",
                "like_count": media.like_count,
                "comment_count": media.comment_count,
                "taken_at": str(media.taken_at),
                "media_url": str(media.thumbnail_url) if media.thumbnail_url else None,
                "title": getattr(media, "title", None),
            }

            if media.media_type == 2 and media.video_url:
                result["video_url"] = str(media.video_url)
                result["video_duration"] = media.video_duration
                result["view_count"] = getattr(media, "view_count", None)

            result["sponsor_tags"] = extract_sponsor_tags_info(media)

            usertags = extract_usertags(media)
            if usertags is not None:
                result["usertags"] = usertags

            location = extract_location(media)
            if location is not None:
                result["location"] = location

            audio = extract_clips_audio_from_dict(getattr(media, "clips_metadata", None))
            if audio is not None:
                result["audio"] = audio

            return {"success": True, "media": result}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def list_media_messages(thread_id: str, limit: int = 100) -> Dict[str, Any]:
        """List all messages containing media in an Instagram direct message thread.
        Args:
            thread_id: The ID of the thread to check for media messages
            limit: Maximum number of messages to check (default 100, max 200)
        Returns:
            A dictionary containing success status and list of all media messages found
        """
        try:
            limit = min(limit, 200)
            messages = client.direct_messages(thread_id, limit)
            media_messages = []
            for message in messages:
                if message.media:
                    media_messages.append({
                        "message_id": str(message.id),
                        "media_type": "photo" if message.media.media_type == 1 else "video",
                        "timestamp": str(message.timestamp) if hasattr(message, 'timestamp') else None,
                        "sender_user_id": message.user_id if hasattr(message, 'user_id') else None
                    })
            return {
                "success": True,
                "message": f"Found {len(media_messages)} messages with media",
                "total_messages_checked": len(messages),
                "media_messages": media_messages
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to list media messages: {str(e)}"
            }

    @mcp.tool()
    def download_media_from_message(message_id: str, thread_id: str, download_path: str = "./downloads") -> Dict[str, Any]:
        """Download media from a specific Instagram direct message and get the local file path.
        Args:
            message_id: The ID of the message containing the media
            thread_id: The ID of the thread containing the message
            download_path: Directory to save the downloaded file (default: ./downloads)
        Returns:
            A dictionary containing success status, a status message, and the file path if successful
        """
        try:
            _ensure_download_directory(download_path)
            target_message = _find_message_in_thread(thread_id, message_id)
            if not target_message:
                return {
                    "success": False,
                    "message": f"Message {message_id} not found in thread {thread_id}"
                }
            if not target_message.media:
                return {
                    "success": False,
                    "message": "This message does not contain media"
                }
            file_path = _download_single_media(target_message.media, download_path)
            return {
                "success": True,
                "message": "Media downloaded successfully",
                "file_path": file_path,
                "media_type": "photo" if target_message.media.media_type == 1 else "video",
                "message_id": message_id,
                "thread_id": thread_id
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to download media: {str(e)}"
            }

    @mcp.tool()
    def download_shared_post_from_message(message_id: str, thread_id: str, download_path: str = "./downloads") -> Dict[str, Any]:
        """Download media from a shared post/reel/clip in a DM message and get the local file path.
        Args:
            message_id: The ID of the message containing the shared post/reel/clip
            thread_id: The ID of the thread containing the message
            download_path: Directory to save the downloaded file (default: ./downloads)
        Returns:
            A dictionary containing success status, a status message, and the file path if successful
        """
        try:
            _ensure_download_directory(download_path)
            target_message = _find_message_in_thread(thread_id, message_id)
            if not target_message:
                return {"success": False, "message": f"Message {message_id} not found in thread {thread_id}"}
            item_type = getattr(target_message, 'item_type', None)
            shared_url = None
            shared_code = None
            shared_obj = None
            if item_type in ["clip", "media_share", "reel_share", "xma_media_share", "post_share", "story_share"]:
                for attr in ['clip', 'media_share', 'xma_media_share', 'post_share', 'story_share']:
                    obj = getattr(target_message, attr, None)
                    if obj:
                        shared_code = obj.get('code') or obj.get('pk')
                        shared_url = obj.get('url') or (f"https://www.instagram.com/reel/{shared_code}/" if shared_code else None)
                        shared_obj = obj
                        break
            if not shared_url:
                return {"success": False, "message": "This message does not contain a supported shared post/reel/clip"}
            try:
                media_pk = client.media_pk_from_url(shared_url)
                media = client.media_info(media_pk)
                if media.media_type == 1:
                    file_path = str(client.photo_download(media_pk, download_path))
                    media_type = "photo"
                elif media.media_type == 2:
                    file_path = str(client.video_download(media_pk, download_path))
                    media_type = "video"
                elif media.media_type == 8:
                    album_paths = client.album_download(media_pk, download_path)
                    file_path = str(album_paths)
                    media_type = "album"
                else:
                    return {"success": False, "message": f"Unsupported media type: {media.media_type}"}
                return {
                    "success": True,
                    "message": "Shared post/reel/clip downloaded successfully",
                    "file_path": file_path,
                    "media_type": media_type,
                    "shared_post_url": shared_url,
                    "message_id": message_id,
                    "thread_id": thread_id
                }
            except Exception as e:
                return {"success": False, "message": f"Failed to download shared post/reel/clip: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"Failed to process message: {str(e)}"}
