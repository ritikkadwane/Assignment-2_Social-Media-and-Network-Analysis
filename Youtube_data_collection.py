"""
YouTube Data Collection Script

Purpose:
Pulling YouTube videos and their comment threads on the Samsung vs
iPhone debate so we can use the data later for sentiment analysis,
topic modelling and a reply-based social network.
 
Dataset Scope:
- Hand-picked videos covering comparisons, switching stories and reviews
- Keeping the full reply chain so we can build a proper reply network
- This file only does the raw pull, cleaning happens in another script
 
Output:
youtube_data.json
 
References:
YouTube Data API v3:
https://developers.google.com/youtube/v3/docs
 
Google API Python Client:
https://github.com/googleapis/google-api-python-client
 
YouTube:
https://www.youtube.com/
 
Notes:
- API key has to be set up first in Google Cloud Console
- Reading the key from an environment variable so it doesn't sit in the file
- One pull uses a tiny fraction of the daily 10,000 unit free quota
- Output JSON is shaped to line up with the Reddit collection file
"""
 
import json
import time
import os
import re
from datetime import datetime, timezone
 
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
 
 
API_KEY = ""
OUTPUT_FILE = "youtube_data.json"
 
YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=fmThG8pnnmA",
    "https://www.youtube.com/watch?v=nHkKJ87FS6s",
    "https://www.youtube.com/watch?v=eCR17sBh-Qw"
]
 
SAMSUNG_KW = ["samsung", "galaxy", "s26", "s25", "s24", "one ui", "oneui", "snapdragon"]
IPHONE_KW = ["iphone", "ios", "apple", "a19", "a18", "dynamic island", "face id"]
 
 
def extract_video_id(url):
    # extracting the video id from the YouTube URL
    pattern = r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None
 
 
def to_iso(date_string):
    # converting YouTube ISO timestamp into a consistent format
    if not date_string:
        return None
    try:
        cleaned = date_string.replace("Z", "+00:00")
        dt = datetime.fromisoformat(cleaned)
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return date_string
 
 
def label_brand(text):
    # labelling each comment based on brand mentions
    if not isinstance(text, str) or not text.strip():
        return "unknown"
 
    text_lower = text.lower()
    has_samsung = any(kw in text_lower for kw in SAMSUNG_KW)
    has_iphone = any(kw in text_lower for kw in IPHONE_KW)
 
    if has_samsung and has_iphone:
        return "both"
    if has_samsung:
        return "samsung"
    if has_iphone:
        return "iphone"
    return "general"
 
 
def fetch_video(youtube, video_id):
    # fetching metadata for one YouTube video
    try:
        response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id
        ).execute()
 
        items = response.get("items", [])
        return items[0] if items else {}
 
    except HttpError as error:
        print(f"Video fetch failed for {video_id}: {error}")
        return {}
    except Exception as error:
        print(f"Video fetch failed for {video_id}: {error}")
        return {}
 
 
def fetch_comments(youtube, video_id, batch_size=100):
    # fetching all available comments and replies for one YouTube video
    all_comments = []
    next_page_token = None
 
    while True:
        try:
            response = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=batch_size,
                pageToken=next_page_token,
                textFormat="plainText",
                order="time"
            ).execute()
 
        except HttpError as error:
            if "commentsDisabled" in str(error):
                print(f"Comments disabled for {video_id}")
            else:
                print(f"Comment fetch failed for {video_id}: {error}")
            break
        except Exception as error:
            print(f"Comment fetch failed for {video_id}: {error}")
            break
 
        items = response.get("items", [])
 
        if not items:
            break
 
        for item in items:
            top_level = item.get("snippet", {}).get("topLevelComment", {})
            all_comments.append(top_level)
 
            # the thread only returns up to 5 inline replies
            inline_replies = item.get("replies", {}).get("comments", [])
            total_replies = item.get("snippet", {}).get("totalReplyCount", 0)
 
            if total_replies > len(inline_replies):
                # fetching the rest with a separate call
                extra_replies = fetch_replies(youtube, top_level.get("id"))
                all_comments.extend(extra_replies)
            else:
                all_comments.extend(inline_replies)
 
        next_page_token = response.get("nextPageToken")
 
        if not next_page_token:
            break
 
        time.sleep(1)
 
    return all_comments
 
 
def fetch_replies(youtube, parent_comment_id, batch_size=100):
    # fetching the remaining replies for one comment thread
    all_replies = []
    next_page_token = None
 
    while True:
        try:
            response = youtube.comments().list(
                part="snippet",
                parentId=parent_comment_id,
                maxResults=batch_size,
                pageToken=next_page_token,
                textFormat="plainText"
            ).execute()
 
        except HttpError as error:
            print(f"Reply fetch failed for {parent_comment_id}: {error}")
            break
        except Exception as error:
            print(f"Reply fetch failed for {parent_comment_id}: {error}")
            break
 
        items = response.get("items", [])
 
        if not items:
            break
 
        all_replies.extend(items)
        next_page_token = response.get("nextPageToken")
 
        if not next_page_token:
            break
 
        time.sleep(0.5)
 
    return all_replies
 
 
def build_comment(raw_comment, video_id):
    # building a standard comment dictionary
    snippet = raw_comment.get("snippet", {})
    text = snippet.get("textDisplay", "") or snippet.get("textOriginal", "")
 
    # authorChannelId is returned as a small dict
    author_channel = snippet.get("authorChannelId", {})
    if isinstance(author_channel, dict):
        author_channel_id = author_channel.get("value")
    else:
        author_channel_id = author_channel
 
    # working out parentId and whether this is the top of a thread
    parent_id = snippet.get("parentId")
    is_top_level = parent_id is None
 
    if is_top_level:
        parent_id = video_id
 
    return {
        "commentId": raw_comment.get("id"),
        "author": snippet.get("authorDisplayName", "[unknown]"),
        "authorChannelId": author_channel_id,
        "text": text,
        "publishedAt": to_iso(snippet.get("publishedAt")),
        "updatedAt": to_iso(snippet.get("updatedAt")),
        "score": int(snippet.get("likeCount", 0) or 0),
        "parentId": parent_id,
        "isTopLevel": is_top_level,
        "brand_label": label_brand(text)
    }
 
 
def build_video(video_data, video_id, url):
    # building a standard video dictionary
    snippet = video_data.get("snippet", {})
    statistics = video_data.get("statistics", {})
    content_details = video_data.get("contentDetails", {})
 
    return {
        "title": snippet.get("title", ""),
        "videoId": video_id,
        "channelId": snippet.get("channelId", ""),
        "channelTitle": snippet.get("channelTitle", ""),
        "publishedAt": to_iso(snippet.get("publishedAt")),
        "duration": content_details.get("duration", ""),
        "viewCount": int(statistics.get("viewCount", 0) or 0),
        "likeCount": int(statistics.get("likeCount", 0) or 0),
        "numComments": int(statistics.get("commentCount", 0) or 0),
        "description": snippet.get("description", ""),
        "tags": snippet.get("tags", []),
        "url": url,
        "comments": []
    }
 
 
def main():
    print("Collecting selected YouTube videos...")
 
    if API_KEY == "PASTE_YOUR_API_KEY_HERE":
        print("API key is missing, set YOUTUBE_API_KEY or paste it into API_KEY.")
        return
 
    youtube = build("youtube", "v3", developerKey=API_KEY)
 
    videos = []
    seen_comment_ids = set()
 
    for url in YOUTUBE_URLS:
        video_id = extract_video_id(url)
 
        if not video_id:
            print(f"Skipping invalid URL: {url}")
            continue
 
        video_data = fetch_video(youtube, video_id)
 
        if not video_data:
            print(f"Skipping {video_id}, no metadata returned")
            continue
 
        video_obj = build_video(video_data, video_id, url)
        comments = fetch_comments(youtube, video_id)
 
        for raw_comment in comments:
            comment_id = raw_comment.get("id")
 
            if comment_id and comment_id not in seen_comment_ids:
                seen_comment_ids.add(comment_id)
                video_obj["comments"].append(build_comment(raw_comment, video_id))
 
        # removing empty and removed comments
        video_obj["comments"] = [
            c for c in video_obj["comments"]
            if c["text"].strip() not in ["", "[removed]", "[deleted]"]
        ]
 
        videos.append(video_obj)
        print(f"Collected {len(video_obj['comments'])} comments from {video_obj['channelTitle']}")
        time.sleep(0.5)
 
    total_comments = sum(len(video["comments"]) for video in videos)
 
    output = {
        "platform": "youtube",
        "source": "YouTube Data API v3",
        "collectedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "totalVideos": len(videos),
        "totalComments": total_comments,
        "videos": videos
    }
 
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)
 
    size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
 
    print("\nCollection complete")
    print(f"Videos collected: {len(videos)}")
    print(f"Total comments: {total_comments:,}")
    print(f"Saved file: {OUTPUT_FILE}")
    print(f"File size: {size_mb:.1f} MB")
 
 
if __name__ == "__main__":
    main()
