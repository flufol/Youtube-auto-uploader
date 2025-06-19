import random
import os
import re
import sys
import argparse
from video_uploader import YouTubeUploader
from video_downloader import VideoDownloader
from colorama import init, Fore

init(autoreset=True)


def main(privacy, upload_video = True, channel_url = None):
    downloader = VideoDownloader()
    
    if channel_url is None and downloader.channels:
        channel_url = random.choice(downloader.channels)
    else:
        print(f"{Fore.RED} There are no more channels to download videos from, stopping script {Fore.RESET}")
        return

    videos = downloader.get_filtered_videos(channel_url)
    if not videos:
        main(privacy, upload_video)
        return

    selected_video = random.choice(videos)
    print(f"Selected: \"{Fore.LIGHTGREEN_EX}{selected_video['title']}{Fore.RESET}\" {Fore.YELLOW}({selected_video['url']}){Fore.RESET}")

    filename = downloader.download_video(selected_video)

    title = os.path.basename(filename)
    title = re.sub(r'\.mp4$', '', title, flags=re.IGNORECASE)

    if upload_video:
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
    parser = argparse.ArgumentParser(description="Video Downloader and Video Uploader")

    parser.add_argument('--privacy', '-p', type=str, help="Privacy status", choices=['public', 'private', 'unlisted'], default='public')
    parser.add_argument('--upload', '-u', action='store_true', help="Upload randomly downloaded video to YouTube")
    parser.add_argument('--channel-url', 'c', type=str, help="Specify a channel URL instead of choosing randomly")

    subparsers = parser.add_subparsers(dest='command')

    parser_add_channel = subparsers.add_parser('add-channel', help='Add a channel to the channel list and txt file')
    parser_add_channel.add_argument('channel_url', type=str, help="Channel URL to add")

    args = parser.parse_args()

    if args.command == 'add-channel':
        downloader = VideoDownloader()
        downloader.add_channel(args.channel_url)
    else:
        main(args.privacy, args.upload, args.channel_url)