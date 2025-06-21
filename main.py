import random
import os
import re
import sys
import argparse
from video_uploader import YouTubeUploader
from video_downloader import VideoDownloader
from colorama import init, Fore

init(autoreset=True)

def download_random_short(upload: bool = False, privacy: str = "public", delete: bool = False):
    downloader = VideoDownloader()

    if downloader.channels:
        channel_url = random.choice(downloader.channels)
    else:
        print(f"{Fore.RED} There are no more channels to download videos from, stopping script {Fore.RESET}")
        return
    shorts = downloader.get_channels_filtered_shorts(channel_url)

    short = random.choice(shorts)
    print(f"Selected: \"{Fore.LIGHTGREEN_EX}{short['title']}{Fore.RESET}\" {Fore.YELLOW}({short['url']}){Fore.RESET}")

    filename = downloader.download_video(short)

    title = os.path.basename(filename)
    title = re.sub(r'\.mp4$', '', title, flags=re.IGNORECASE)
    if upload:
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
        print(f"{Fore.GREEN}Skipping upload{Fore.RESET}")

    if delete:
        os.remove(filename)
        print(f"{Fore.RED}Deleting video file{Fore.RESET}")
    else:
        print(f"{Fore.LIGHTGREEN_EX}File downloaded, find it at {filename}{Fore.RESET}")


def download_video(video_url: str, upload: bool = False, title: str = None, privacy: str = "public", delete: bool = False):
    downloader = VideoDownloader()

    filename = downloader.download_video_from_url(video_url)

    if title is None:
        title = os.path.basename(filename)
        title = re.sub(r'\.mp4$', '', title, flags=re.IGNORECASE)

    if upload:
        uploader = YouTubeUploader()
        uploader.upload_video(
            file_path=filename,
            title=title,
            description="",
            category="15",
            keywords="",
            privacy_status=privacy
        )

    if delete:
        os.remove(filename)
        print(f"{Fore.RED}Deleting video file{Fore.RESET}")
    else:
        print(f"{Fore.LIGHTGREEN_EX} File downloaded, find it at {filename} {Fore.RESET}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video Downloader and Video Uploader")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    parser.add_argument('--video_url', type=str, help="Video URL to download")
    parser.add_argument('--title', type=str, help="Title of the video")
    parser.add_argument('--privacy', type=str, help="Privacy status", choices=['public', 'private', 'unlisted'], default='public')
    parser.add_argument('--upload', action='store_true', help="Upload downloaded video to YouTube")
    parser.add_argument('--delete', action='store_true', help="If the file should be deleted after uploading", )

    subparsers = parser.add_subparsers(dest='command')

    parser_random_short = subparsers.add_parser('upload-random-short', help='Download a random short from the channels file and upload it to YouTube')
    parser_random_short.add_argument('--privacy', type=str, help="Privacy status", choices=['public', 'private', 'unlisted'], default='public')
    parser_random_short.add_argument('--upload', action='store_true', help="Upload downloaded video to YouTube")
    parser_random_short.add_argument('--delete', action='store_true', help="If the file should be deleted after uploading", )

    parser_add_channel = subparsers.add_parser('add-channel', help='Add a channel to the channel list and txt file')
    parser_add_channel.add_argument('channel_url', type=str, help="Channel URL to add")

    args = parser.parse_args()

    if args.command == 'add-channel':
        downloader = VideoDownloader()
        downloader.add_channel(args.channel_url)
    elif args.command == 'upload-random-short':
        download_random_short(args.upload, args.privacy, args.delete)
    else:
        download_video(args.video_url, args.upload, args.title, args.privacy, args.delete)