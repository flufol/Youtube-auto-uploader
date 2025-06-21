import yt_dlp
from yt_dlp import YoutubeDL
import os
from colorama import init, Fore

init(autoreset=True)

class VideoDownloader():
    def __init__(self):
        self.channels_path = "channels.txt"
        self.videos_path = "videos.txt"
        self.downloads_path = "downloads"
        self._check_and_make_files()
        
        self.channels = self._get_channels()
        
        
    def _check_and_make_files(self):
        if not os.path.exists(self.channels_path):
            open(self.channels_path, "a").close()
        
        if not os.path.exists(self.videos_path):
            open(self.videos_path, "a").close()
        
        if not os.path.exists(self.downloads_path):
            os.makedirs(self.downloads_path)
            
    
    def _get_channels(self):
        self._check_and_make_files()
        with open(self.channels_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    
    
    def _remove_channel(self, channel_url):
        with open(self.channels_path, 'r') as file:
            lines = file.readlines()

        lines = [line for line in lines if line.strip() != channel_url]
        
        with open(self.channels_path, 'w') as file:
            file.writelines(lines)


    def add_channel(self, channel_url):
        with open(self.channels_path, 'a') as file:
            file.write(channel_url + '\n')


    def _get_downloaded_videos(self):
        self._check_and_make_files()
        with open(self.videos_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]


    def _add_downloaded_video(self, video_id):
        with open(self.videos_path, 'a') as file:
            file.write(video_id + '\n')
            print(video_id)


    def _handle_no_videos(self, channel_url):
        print(f"{Fore.RED} All valid videos from {channel_url} have been downloaded. \n\
        Removing this channel from options. {Fore.RESET} \n\
        {Fore.LIGHTGREEN_EX} Selecting new channel {Fore.RESET}")

        self._remove_channel(channel_url)

        if self.channels:
            self.channels = self._get_channels()
            return []
        else:
            print(f"{Fore.RED} There are no more channels to download videos from, stopping script {Fore.RESET}")
            return []


    def get_channels_videos(self, channel_url):
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            videos = info.get('entries', [])
        videos = [
            video for video in videos
            if video.get('id')
            and video.get('url')
        ]
        if videos:
            return videos
        else:
            print(f"{Fore.RED}No videos found{Fore.RESET}")
            return []


    def get_channels_filtered_videos(self, channel_url):
        downloaded_videos = self._get_downloaded_videos()

        videos = self.get_channels_videos(channel_url)
        filtered_videos = [
            video for video in videos
            if video.get('id') not in downloaded_videos
            and not '/shorts/' in video['url']
        ]
        if filtered_videos:
            return filtered_videos
        else:
            self._handle_no_videos(channel_url)
            return []


    def get_channels_shorts(self, channel_url):
        videos = self.get_channels_videos(channel_url)
        shorts = [
            short for short in videos
            if short.get('id')
               and short.get('url')
               and '/shorts/' in short['url']
        ]
        if shorts:
            return shorts
        else:
            print(f"{Fore.RED}No shorts found{Fore.RESET}")
            return []


    def get_channels_filtered_shorts(self, channel_url):
        downloaded_videos = self._get_downloaded_videos()

        shorts = self.get_channels_shorts(channel_url)
        filtered_shorts = [
            short for short in shorts
            if short.get('id') not in downloaded_videos
        ]
        if shorts:
            return shorts
        else:
            self._handle_no_videos(channel_url)
            return []


    def download_video(self, video):
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'ffmpeg_location': '/opt/homebrew/bin/ffmpeg',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }
            video_url = video['url']
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                filename = ydl.prepare_filename(info)
                video_id = info.get('id')
                
            self._add_downloaded_video(video_id)
            
            return filename


    def download_video_from_url(self, video_url):
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'ffmpeg_location': '/opt/homebrew/bin/ffmpeg',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            video_id = info.get('id')

        self._add_downloaded_video(video_id)

        return filename