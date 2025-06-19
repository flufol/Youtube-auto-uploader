#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Upload Video
# @raycast.mode fullOutput

# Optional parameters:
# @raycast.icon 🤖

# Documentation:
# @raycast.author fluffychocobot
# @raycast.authorURL https://raycast.com/fluffychocobot

import yt_dlp
from yt_dlp import YoutubeDL
import random
import os
import json
import re
from video_uploader import YouTubeUploader
from colorama import init, Fore

init(autoreset=True)

HISTORY_FILE = 'downloaded_videos.json'

channels = ["https://www.youtube.com/@ChengyuMovies",
            "https://www.youtube.com/@Goodstory87",
            "https://www.youtube.com/@AiByteStudio-572",
            "https://www.youtube.com/@PhantomSparks6m/shorts",
            "https://www.youtube.com/@wildlifecuties/shorts",
            "https://www.youtube.com/@cuteduckLele/shorts",
            "https://www.youtube.com/@Hmminds/shorts",
            "https://www.youtube.com/@Kittenjourney-f2n/shorts",
            "https://www.youtube.com/@WhiteDogCatsss/shorts",
            "https://www.youtube.com/@MeowMotion950/shorts"]


def load_download_log():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "downloaded_videos": [],
            "fully_downloaded_channels": []
        }


def save_download_log(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def mark_video_downloaded(video_id, log):
    if video_id not in log["downloaded_videos"]:
        log["downloaded_videos"].append(video_id)


def mark_channel_fully_downloaded(channel_id, log):
    if channel_id not in log["fully_downloaded_channels"]:
        log["fully_downloaded_channels"].append(channel_id)


def get_video_list(channel_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        return info.get('entries', [])


def download_video(video_url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        # Construct the full file path of the downloaded video
        filename = ydl.prepare_filename(info_dict)
    return filename


def get_all_video_entries(channel_url):
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'skip_download': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        # Some channels are nested in 'entries', others are returned flat
        entries = info.get('entries', [])
        return entries


def main(privacy):
    channel_url = random.choice(channels)

    video_entries = get_video_list(channel_url)
    video_entries = [v for v in video_entries if 'id' in v and 'url' in v]

    log = load_download_log()
    downloaded_video_ids = set(log.get("downloaded_videos", []))
    fully_downloaded_channels = set(log.get("fully_downloaded_channels", []))

    new_videos = [
        v for v in video_entries
        if v.get('id') not in downloaded_video_ids and v.get('url') and '/shorts/' in v['url'] and v.get("channel_id") not in fully_downloaded_channels
    ]

    if not new_videos:
        print(Fore.RED + f"All videos from {channel_url} have already been downloaded.\n Removing this channel from options {Fore.RESET} \n {Fore.LIGHTGREEN_EX} Selecting new channel {Fore.RESET}")
        mark_channel_fully_downloaded(channel_url, log)
        save_download_log(log)
        main(privacy)
        return

    selected_video = random.choice(new_videos)
    print(f"Selected: {selected_video['title']} ({selected_video['url']})")

    filename = download_video(selected_video['url'])

    mark_video_downloaded(selected_video['id'], log)
    save_download_log(log)

    title = os.path.basename(filename)
    title = re.sub(r'\.mp4$', '', title, flags=re.IGNORECASE)

    description = ""

    uploader = YouTubeUploader()
    uploader.upload_video(
        file_path=filename,
        title=title,
        description=description,
        category="22",  # Category ID for "People & Blogs"
        keywords="short,stories,cute,cuteanimals,animals,rescue",
        privacy_status=privacy
    )

    print(Fore.RED + "deleting video file" + Fore.RESET)
    os.remove(filename)


if __name__ == "__main__":
    log = load_download_log()
    fully_downloaded_channels = set(log.get("fully_downloaded_channels", []))
    channels = [item for item in channels if item not in fully_downloaded_channels]

    main("public")