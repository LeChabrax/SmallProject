"""User content tools: stories, posts, followers/following, like."""

from __future__ import annotations

from typing import Any, Dict


def register(mcp, client) -> None:
    @mcp.tool()
    def get_user_stories(username: str) -> Dict[str, Any]:
        """Get Instagram stories from a user.

        Args:
            username: Instagram username to get stories from.
        Returns:
            A dictionary with success status and stories information.
        """
        if not username:
            return {"success": False, "message": "Username must be provided."}

        try:
            user_id = client.user_id_from_username(username)
            if not user_id:
                return {"success": False, "message": f"User '{username}' not found."}

            stories = client.user_stories(user_id)

            story_results = []
            for story in stories:
                story_data = {
                    "story_id": str(story.pk),
                    "media_type": story.media_type,
                    "taken_at": str(story.taken_at),
                    "user": {
                        "username": story.user.username,
                        "full_name": story.user.full_name,
                        "user_id": str(story.user.pk)
                    },
                    "media_url": str(story.thumbnail_url) if story.thumbnail_url else None,
                }

                if story.media_type == 2 and story.video_url:
                    story_data["video_url"] = str(story.video_url)
                    story_data["video_duration"] = story.video_duration

                story_results.append(story_data)

            return {"success": True, "stories": story_results, "count": len(story_results)}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def like_media(media_url: str, like: bool = True) -> Dict[str, Any]:
        """Like or unlike an Instagram post.

        Args:
            media_url: URL of the Instagram post.
            like: True to like, False to unlike the post.
        Returns:
            A dictionary with success status and a status message.
        """
        if not media_url:
            return {"success": False, "message": "Media URL must be provided."}

        try:
            media_pk = client.media_pk_from_url(media_url)
            if not media_pk:
                return {"success": False, "message": "Invalid media URL or post not found."}

            if like:
                result = client.media_like(media_pk)
                action = "liked"
            else:
                result = client.media_unlike(media_pk)
                action = "unliked"

            if result:
                return {"success": True, "message": f"Post {action} successfully."}
            else:
                return {"success": False, "message": f"Failed to {action.rstrip('d')} post."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def get_user_followers(username: str, count: int = 20) -> Dict[str, Any]:
        """Get followers of an Instagram user.

        Args:
            username: Instagram username to get followers for.
            count: Maximum number of followers to return (default 20).
        Returns:
            A dictionary with success status and followers list.
        """
        if not username:
            return {"success": False, "message": "Username must be provided."}

        try:
            user_id = client.user_id_from_username(username)
            if not user_id:
                return {"success": False, "message": f"User '{username}' not found."}

            followers = client.user_followers(user_id, amount=count)

            follower_results = []
            for follower_id, follower in followers.items():
                follower_data = {
                    "user_id": str(follower.pk),
                    "username": follower.username,
                    "full_name": follower.full_name,
                    "is_private": follower.is_private,
                    "profile_pic_url": str(follower.profile_pic_url) if follower.profile_pic_url else None,
                }
                follower_results.append(follower_data)

            return {"success": True, "followers": follower_results, "count": len(follower_results)}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def get_user_following(username: str, count: int = 20) -> Dict[str, Any]:
        """Get users that an Instagram user is following.

        Args:
            username: Instagram username to get following list for.
            count: Maximum number of following to return (default 20).
        Returns:
            A dictionary with success status and following list.
        """
        if not username:
            return {"success": False, "message": "Username must be provided."}

        try:
            user_id = client.user_id_from_username(username)
            if not user_id:
                return {"success": False, "message": f"User '{username}' not found."}

            following = client.user_following(user_id, amount=count)

            following_results = []
            for following_id, followed_user in following.items():
                following_data = {
                    "user_id": str(followed_user.pk),
                    "username": followed_user.username,
                    "full_name": followed_user.full_name,
                    "is_private": followed_user.is_private,
                    "profile_pic_url": str(followed_user.profile_pic_url) if followed_user.profile_pic_url else None,
                }
                following_results.append(following_data)

            return {"success": True, "following": following_results, "count": len(following_results)}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def get_user_posts(username: str, count: int = 12) -> Dict[str, Any]:
        """Get recent posts from an Instagram user.

        Args:
            username: Instagram username to get posts from.
            count: Maximum number of posts to return (default 12).
        Returns:
            A dictionary with success status and posts list.
        """
        if not username:
            return {"success": False, "message": "Username must be provided."}

        try:
            user_id = client.user_id_from_username(username)
            if not user_id:
                return {"success": False, "message": f"User '{username}' not found."}

            medias = client.user_medias(user_id, amount=count)

            media_results = []
            for media in medias:
                media_data = {
                    "media_id": str(media.pk),
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
                    media_data["video_url"] = str(media.video_url)
                    media_data["video_duration"] = media.video_duration
                    media_data["view_count"] = getattr(media, "view_count", None)

                sponsor_tags = getattr(media, "sponsor_tags", None)
                if sponsor_tags:
                    media_data["sponsor_tags"] = [
                        {
                            "username": getattr(s, "username", None) or getattr(getattr(s, "user", None), "username", None),
                            "full_name": getattr(s, "full_name", None) or getattr(getattr(s, "user", None), "full_name", None),
                        }
                        for s in sponsor_tags
                    ]

                clips_metadata = getattr(media, "clips_metadata", None)
                if clips_metadata:
                    music_info = {}
                    if hasattr(clips_metadata, "music_info"):
                        mi = clips_metadata.music_info
                        if mi:
                            music_canonical = getattr(mi, "music_asset_info", None) or getattr(mi, "music_canonical", None) or mi
                            music_info["title"] = getattr(music_canonical, "title", None)
                            music_info["artist"] = getattr(music_canonical, "display_artist", None) or getattr(music_canonical, "artist_name", None)
                    elif hasattr(clips_metadata, "original_sound_info"):
                        osi = clips_metadata.original_sound_info
                        if osi:
                            music_info["title"] = getattr(osi, "original_audio_title", None)
                            music_info["artist"] = None
                    if any(music_info.values()):
                        media_data["music"] = music_info

                usertags = getattr(media, "usertags", None)
                if usertags:
                    media_data["usertags"] = [
                        getattr(ut, "username", None) or getattr(getattr(ut, "user", None), "username", None)
                        for ut in usertags
                    ]

                location = getattr(media, "location", None)
                if location:
                    media_data["location"] = getattr(location, "name", str(location))

                media_results.append(media_data)

            return {"success": True, "posts": media_results, "count": len(media_results)}
        except Exception as e:
            return {"success": False, "message": str(e)}
