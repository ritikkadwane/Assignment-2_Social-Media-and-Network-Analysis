"""
Reddit Data Collection Script
COSC2671 Social Media and Network Analysis
Assignment 2 – Samsung vs iPhone Analysis

Authors:
Ritik Kadwane
Ngoc Anh Thu Nguyen

Institution:
RMIT University

Purpose:
Collecting Reddit discussion threads and comments related to
Samsung vs iPhone debates using the Arctic Shift Reddit API.

Dataset Scope:
- Manually selected high engagement Reddit threads
- Multiple smartphone-related subreddits
- Parent-child reply structure preserved for network analysis
- Raw data collection before preprocessing

Output:
reddit_raw.json

References:
Arctic Shift API:
https://github.com/ArthurHeitmann/arctic_shift

Reddit:
https://www.reddit.com/

Python Requests Documentation:
https://requests.readthedocs.io/

Notes:
- Collecting raw Reddit data before preprocessing
- Performing preprocessing in a separate workflow stage
- Using collected data for sentiment analysis, topic modelling,
  social network analysis, community detection, and diffusion analysis
"""

import requests
import json
import time
import os
import re
from datetime import datetime, timezone


BASE_URL = "https://arctic-shift.photon-reddit.com/api"
OUTPUT_FILE = "reddit_data.json"

REDDIT_URLS = [
    # r/Smartphones - direct comparisons
    "https://www.reddit.com/r/Smartphones/comments/1l0i3nb/iphones_are_so_overrated/",
    "https://www.reddit.com/r/Smartphones/comments/1nm3cgm/moving_back_to_ios_the_uncomfortable_truth/",
    "https://www.reddit.com/r/Smartphones/comments/1nzjpui/just_switched_from_android_to_ios_and/",
    "https://www.reddit.com/r/Smartphones/comments/1ou7vdg/samsung_vs_iphone/",
    "https://www.reddit.com/r/Smartphones/comments/1lkw2zi/i_dont_like_iphones_im_not_a_fan_of_samsung/",
    "https://www.reddit.com/r/Smartphones/comments/1gm2l58/iphone_16_or_samsung_s24/",
    "https://www.reddit.com/r/Smartphones/comments/1ntno62/pixel_10_vs_galaxy_s25_vs_iphone_17_im_confused/",
    "https://www.reddit.com/r/Smartphones/comments/1svldih/s26_ultra_vs_iphone_17_propro_max/",
    "https://www.reddit.com/r/Smartphones/comments/1sb4egh/should_i_buy_the_iphone_17_or_samsung_s26/",
    "https://www.reddit.com/r/Smartphones/comments/1t62ovi/iphone_17_pro_vs_samsung_s26_ultra_honest/",
    "https://www.reddit.com/r/Smartphones/comments/1s0qzsw/after_using_both_for_3_months_i_genuinely_cant/",
    "https://www.reddit.com/r/Smartphones/comments/1rggrjo/s26_ultra_vs_iphone_17_pro_max_which_will_survive/",
    "https://www.reddit.com/r/Smartphones/comments/1sdxjzv/should_i_buy_the_iphone_17_or_samsung_s25_ultra/",
    "https://www.reddit.com/r/Smartphones/comments/1sqvvre/should_get_iphone_17_or_samsung_s26_plus/",
    "https://www.reddit.com/r/Smartphones/comments/1suju5w/in_2026_is_it_wise_to_say_that_iphones_continue/",
    "https://www.reddit.com/r/Smartphones/comments/1t2fdik/what_phone_to_buy_in_mid_2026/",

    # r/samsunggalaxy - switching stories and comparisons
    "https://www.reddit.com/r/samsunggalaxy/comments/1tcqxh4/bye_iphone_hope_worth_the_switch/",
    "https://www.reddit.com/r/samsunggalaxy/comments/1sxqktf/yeah_i_finally_left_iphone_no_regrets/",
    "https://www.reddit.com/r/samsunggalaxy/comments/1mi09sp/after_13_yrs_on_iphone/",
    "https://www.reddit.com/r/samsunggalaxy/comments/1kpeof8/jumped_ship_to_s25_from_iphone_was_blown_away/",
    "https://www.reddit.com/r/samsunggalaxy/comments/1rn9ydv/galaxy_s26_ultra_after_one_day/",
    "https://www.reddit.com/r/samsunggalaxy/comments/1swhjpz/after_12_years_with_apple/",
    "https://www.reddit.com/r/samsunggalaxy/comments/17r17jw/what_would_make_an_iphone_user_want_to_switch/",
    "https://www.reddit.com/r/samsunggalaxy/comments/1fxxa5s/what_does_your_phone_timeline_look_like/",
    "https://www.reddit.com/r/samsunggalaxy/comments/1fyx4sz/it_finally_came_goodbye_iphone/",
    "https://www.reddit.com/r/samsunggalaxy/comments/1i9ne00/samsung_galaxy_s25_ultra_vs_iphone_16_pro_max/",
    "https://www.reddit.com/r/samsunggalaxy/comments/1oeptl6/regret_switching_to_iphone/",

    # r/iphone - switching stories and comparisons
    "https://www.reddit.com/r/iphone/comments/1i928mv/what_keeps_you_with_an_iphone/",
    "https://www.reddit.com/r/iphone/comments/1sgw6m9/iphone_users_that_switched_from_samsung_what_is/",
    "https://www.reddit.com/r/iphone/comments/1t124r3/going_back_to_iphone_after_1_year_on_android_my/",
    "https://www.reddit.com/r/iphone/comments/1rciek2/10_years_android_user_switched_iphone/",
    "https://www.reddit.com/r/iphone/comments/1hx5y6m/anyone_switched_from_samsung_to_iphone/",
    "https://www.reddit.com/r/iphone/comments/1jaumlf/i_tried_android_and_switched_back_within_a_month/",
    "https://www.reddit.com/r/iphone/comments/1jyubrg/people_who_switched_to_an_android_and_then_came/",
    "https://www.reddit.com/r/iphone/comments/1rqr0cm/switched_from_s24_ultra_to_iphone_17_pro_after_10/",

    # r/apple - comparisons
    "https://www.reddit.com/r/apple/comments/1b3scws/android_users_switching_to_iphone_prefer_value/",
    "https://www.reddit.com/r/apple/comments/ulom3s/camera_comparison_samsungs_galaxy_s22_ultra_vs/",

    # r/Android - comparisons
    "https://www.reddit.com/r/Android/comments/1r2qfxa/samsungs_obsession_with_apple_is_getting_out_of/",
    "https://www.reddit.com/r/Android/comments/1q3dh24/at_what_point_does_an_android_phone_make_more/",
    "https://www.reddit.com/r/Android/comments/1llz6ye/everyone_who_was_on_android_and_then_switched_to/",
    "https://www.reddit.com/r/Android/comments/1os08az/those_who_migrated_from_a_newer_iphone_12_or/",
    "https://www.reddit.com/r/Android/comments/157nsvc/young_koreans_favor_iphones_over_samsung_galaxy/",
]

SAMSUNG_KW = ["samsung", "galaxy", "s26", "s25", "s24", "one ui", "oneui", "snapdragon"]
IPHONE_KW = ["iphone", "ios", "apple", "a19", "a18", "dynamic island", "face id"]


def extract_post_id(url):
    # extracting the post id from the Reddit URL
    match = re.search(r"/comments/([a-zA-Z0-9]+)/", url)
    return match.group(1) if match else None


def to_iso(utc_val):
    # converting Unix timestamp into ISO date format
    try:
        return datetime.fromtimestamp(int(float(utc_val)), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return None


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


def fetch_post(post_id):
    # fetching metadata for one Reddit post
    params = {"ids": f"t3_{post_id}"}

    try:
        response = requests.get(f"{BASE_URL}/posts/ids", params=params, timeout=20)

        if response.status_code == 200:
            data = response.json().get("data", [])
            return data[0] if data else {}

        print(f"Post fetch failed for {post_id}")
        print(response.text[:300])
        return {}

    except Exception as error:
        print(f"Post fetch failed for {post_id}: {error}")
        return {}


def fetch_comments(post_id, batch_size=100):
    # fetching all available comments for one Reddit post
    all_comments = []
    before_utc = None

    while True:
        params = {
            "link_id": f"t3_{post_id}",
            "limit": batch_size
        }

        if before_utc:
            params["before"] = before_utc

        try:
            response = requests.get(f"{BASE_URL}/comments/search", params=params, timeout=30)

            if response.status_code != 200:
                print(f"Comment fetch failed for {post_id}: {response.status_code}")
                print(response.text[:300])
                break

            data = response.json().get("data", [])

            if not data:
                break

            all_comments.extend(data)
            before_utc = data[-1].get("created_utc")

            if len(data) < batch_size:
                break

            time.sleep(1)

        except Exception as error:
            print(f"Comment fetch failed for {post_id}: {error}")
            break

    return all_comments


def build_comment(raw_comment):
    # building a standard comment dictionary
    text = raw_comment.get("body", "")

    return {
        "commentId": raw_comment.get("id"),
        "author": raw_comment.get("author", "[deleted]"),
        "text": text,
        "publishedAt": to_iso(raw_comment.get("created_utc")),
        "score": raw_comment.get("score", 0),
        "parentId": raw_comment.get("parent_id"),
        "isTopLevel": str(raw_comment.get("parent_id", "")).startswith("t3_"),
        "brand_label": label_brand(text)
    }


def main():
    print("Collecting selected Reddit threads...")

    posts = []
    seen_comment_ids = set()

    for url in REDDIT_URLS:
        post_id = extract_post_id(url)

        if not post_id:
            print(f"Skipping invalid URL: {url}")
            continue

        post_data = fetch_post(post_id)
        comments = fetch_comments(post_id)

        post_obj = {
            "title": post_data.get("title", ""),
            "postId": post_id,
            "subreddit": post_data.get("subreddit", ""),
            "author": post_data.get("author", ""),
            "publishedAt": to_iso(post_data.get("created_utc")),
            "score": post_data.get("score", 0),
            "numComments": int(post_data.get("num_comments", 0) or 0),
            "url": url,
            "comments": []
        }

        for comment in comments:
            comment_id = comment.get("id")

            if comment_id and comment_id not in seen_comment_ids:
                seen_comment_ids.add(comment_id)
                post_obj["comments"].append(build_comment(comment))

        # removing deleted and removed comments
        post_obj["comments"] = [
            c for c in post_obj["comments"]
            if c["author"] != "[deleted]"
            and c["text"].strip() not in ["[removed]", "[deleted]"]
        ]

        posts.append(post_obj)
        print(f"Collected {len(post_obj['comments'])} comments from r/{post_obj['subreddit']}")
        time.sleep(0.5)

    total_comments = sum(len(post["comments"]) for post in posts)

    output = {
        "platform": "reddit",
        "source": "Arctic Shift API",
        "collectedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "totalPosts": len(posts),
        "totalComments": total_comments,
        "posts": posts
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)

    size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)

    print("\nCollection complete")
    print(f"Posts collected: {len(posts)}")
    print(f"Total comments: {total_comments:,}")
    print(f"Saved file: {OUTPUT_FILE}")
    print(f"File size: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()