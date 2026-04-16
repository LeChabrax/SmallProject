"""Shared media-attribute extractors used by both media.py and posts.py.

Pull helpers out of the two big handlers (`get_media_info`,
`get_user_posts`) that do the same attr-walk dance.
"""

from __future__ import annotations

from typing import Any


def extract_usertags(media) -> list[str | None] | None:
    """Return usernames tagged on a post/media, or None if no usertags."""
    usertags = getattr(media, "usertags", None)
    if not usertags:
        return None
    return [
        getattr(ut, "username", None) or getattr(getattr(ut, "user", None), "username", None)
        for ut in usertags
    ]


def extract_location(media) -> str | None:
    """Return the location name if the media has one."""
    location = getattr(media, "location", None)
    if not location:
        return None
    return getattr(location, "name", str(location))


def extract_sponsor_tags_attr(media) -> list[dict] | None:
    """Sponsor-tag extractor for user_medias payloads (attribute-style access)."""
    sponsor_tags = getattr(media, "sponsor_tags", None)
    if not sponsor_tags:
        return None
    return [
        {
            "username": getattr(s, "username", None) or getattr(getattr(s, "user", None), "username", None),
            "full_name": getattr(s, "full_name", None) or getattr(getattr(s, "user", None), "full_name", None),
        }
        for s in sponsor_tags
    ]


def extract_sponsor_tags_info(media) -> list[dict]:
    """Sponsor-tag extractor for media_info payloads (flat attribute access).

    Returns an empty list rather than None to preserve the existing
    `get_media_info` contract (it always emits a `sponsor_tags` key).
    """
    sponsor_tags = getattr(media, "sponsor_tags", None)
    if not sponsor_tags:
        return []
    return [
        {
            "pk": str(getattr(s, "pk", "")),
            "username": getattr(s, "username", None),
            "full_name": getattr(s, "full_name", None),
        }
        for s in sponsor_tags
    ]


def extract_clips_audio_from_dict(clips_meta: dict | None) -> dict | None:
    """Extract audio/music info from a clips_metadata dict (media_info style).

    Returns a dict with `audio_type`, `title`, `artist`, or None if no
    meaningful audio metadata is present.
    """
    if not clips_meta or not isinstance(clips_meta, dict):
        return None

    audio_info: dict[str, Any] = {"audio_type": clips_meta.get("audio_type")}

    music_info = clips_meta.get("music_info")
    if music_info and isinstance(music_info, dict):
        music_asset = music_info.get("music_asset_info") or music_info.get("music_canonical") or {}
        if isinstance(music_asset, dict):
            audio_info["title"] = music_asset.get("title")
            audio_info["artist"] = music_asset.get("display_artist") or music_asset.get("artist_name")

    if not audio_info.get("title"):
        osi = clips_meta.get("original_sound_info")
        if osi and isinstance(osi, dict):
            audio_info["title"] = osi.get("original_audio_title")
            ig_artist = osi.get("ig_artist")
            if ig_artist and isinstance(ig_artist, dict):
                audio_info["artist"] = ig_artist.get("username")

    if not any(v for k, v in audio_info.items() if k != "audio_type"):
        return None
    return audio_info


def extract_clips_audio_from_attr(clips_metadata) -> dict | None:
    """Extract audio/music info from clips_metadata accessed via attributes (user_medias style)."""
    if not clips_metadata:
        return None
    music_info: dict[str, Any] = {}
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
    if not any(music_info.values()):
        return None
    return music_info
