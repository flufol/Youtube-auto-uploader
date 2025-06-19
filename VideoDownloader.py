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
        
        self.channels = self.get_channels()
        
        
    def _check_and_make_files(self):
        if not os.path.exists(self.channels_path):
            open(self.channels_path, "a").close()
        
        if not os.path.exists(self.videos_path):
            open(self.videos_path, "a").close()
        
        if not os.path.exists(self.downloads_path):
            os.makedirs(self.downloads_path)
            
    
    def _get_channels(self):
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
        with open(self.videos_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]


    def _add_downloaded_video(self, video_id):
        with open(self.videos_path, 'w') as file:
            file.writelines(video_id + '\n')
    
    
    def _get_channels_videos(self, channel_url):
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            return info.get('entries', [])


    def get_filtered_videos(self, channel_url):
        downloaded_videos = self._get_downloaded_videos()
        
        videos = self._get_channels_videos(channel_url)
        filtered_videos = [
            video for video in videos
            if video.get('id') 
            and video.get('id') not in downloaded_videos
            and video.get('url') 
            and '/shorts/' in video['url']
        ]
        if filtered_videos:
            print("not filltered videos")
            return filtered_videos
        else:
            print(f"{Fore.RED} All valid shorts from {channel_url} have been downloaded. \n\
            Removing this channel from options. {Fore.RESET} \n\
            {Fore.LIGHTGREEN_EX} Selecting new channel {Fore.RESET}")

            self.remove_channel(channel_url)
            
            if self.channels:
                self.channels = self.get_channels()
                print("if channels")
            else:
                print(f"{Fore.RED} There are no more channels to download videos from, stopping script {Fore.RESET}")
                return
    

    def download_video(self, video):
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
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
                
            self.add_downloaded_video(video_id)
            
            return filename
