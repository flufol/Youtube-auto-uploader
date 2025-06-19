import random
import os
import re
from video_uploader import YouTubeUploader
from VideoDownloader import VideoDownloader
from colorama import init, Fore

init(autoreset=True)


def main(privacy, upload_video = True):
    downloader = VideoDownloader()
    
    channel_url = None
    if downloader.channels:
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
    main("public", False)