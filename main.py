import yt_dlp
from yt_dlp import YoutubeDL
import random
import os
import re
from video_uploader import YouTubeUploader
from colorama import init, Fore

init(autoreset=True)

channels = []


def get_channels():
    with open('channels_to_download.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]


def remove_channel(channel_url):
    with open('channels_to_download.txt', 'r') as file:
        lines = file.readlines()

    lines = [line for line in lines if line.strip() != channel_url]
    
    with open('channels_to_download.txt', 'w') as file:
        file.writelines(lines)


def get_downloaded_videos():
    with open('downloaded_videos.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]


def add_downloaded_video(video_id):
    with open('downloaded_videos.txt', 'w') as file:
        file.writelines(video_id)


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
        filename = ydl.prepare_filename(info_dict)
    return filename


def main(privacy, upload_video = True):
    global channels
    channel_url = random.choice(channels)

    downloaded_videos = get_downloaded_videos()

    videos = get_video_list(channel_url)
    videos = [
        video for video in videos
        if video.get('id') 
        and video.get('id') not in downloaded_videos
        and video.get('url') 
        and '/shorts/' in video['url']
    ]
    
    if not videos:
        print(f"{Fore.RED} All valid shorts from {channel_url} have been downloaded. \n\
            Removing this channel from options. {Fore.RESET} \n\
            {Fore.LIGHTGREEN_EX} Selecting new channel {Fore.RESET}")

        remove_channel(channel_url)
        
        if get_channels():
            channels = get_channels()
        else:
            print(f"{Fore.RED} There are no more channels to download videos from, stopping script {Fore.RESET}")
            return
        
        main(privacy, upload_video)
        return

    selected_video = random.choice(videos)
    print(f"Selected: \"{Fore.LIGHTGREEN_EX}{selected_video['title']}{Fore.RESET}\" {Fore.YELLOW}({selected_video['url']}){Fore.RESET}")

    filename = download_video(selected_video['url'])

    add_downloaded_video(selected_video['id'])

    title = os.path.basename(filename)
    title = re.sub(r'\.mp4$', '', title, flags=re.IGNORECASE)

    if upload_video == True:
        uploader = YouTubeUploader()
        uploader.upload_video(
            file_path=filename,
            title=title,
            description="",
            category="15",
            keywords="short,stories,cute,cuteanimals,animals,rescue",
            privacy_status=privacy
        )
    else:
        print(f"{Fore.GREEN} Skipping upload {Fore.RESET}")

    print(f"{Fore.RED}Deleting video file{Fore.RESET}")
    os.remove(filename)


if __name__ == "__main__":
    channels = get_channels()
    print(channels)
    main("public", False)