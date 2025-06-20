import httplib2
import os
import random
import time
from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from colorama import init, Fore

CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
MAX_RETRIES = 10

init(autoreset=True)


class YouTubeUploader:
    def __init__(self, credentials_storage="youtube-oauth2.json"):
        self.credentials_storage = credentials_storage
        self.youtube = self._authenticate()


    def _authenticate(self):
        flow = flow_from_clientsecrets(
            CLIENT_SECRETS_FILE,
            scope=YOUTUBE_UPLOAD_SCOPE
        )

        storage = Storage(self.credentials_storage)
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            raise RuntimeError(Fore.RED + "OAuth credentials not found or invalid. Run the original script with args once to generate them." + Fore.RESET)

        return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                         http=credentials.authorize(httplib2.Http()))

    def upload_video(self, file_path, title="Test Title", description="Test Description",
                     category="22", keywords="", privacy_status="public"):
        if not os.path.exists(file_path):
            raise FileNotFoundError(Fore.RED + f"Video file not found: {file_path}" + Fore.RESET)

        tags = keywords.split(",") if keywords else None

        body = dict(
            snippet=dict(
                title=title,
                description=description,
                tags=tags,
                categoryId=category
            ),
            status=dict(
                privacyStatus=privacy_status,
                madeForKids=False
            )
        )

        insert_request = self.youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
        )

        self._resumable_upload(insert_request)

    def _resumable_upload(self, insert_request):
        response = None
        error = None
        retry = 0

        while response is None:
            try:
                print(Fore.YELLOW + "Uploading file to youtube" + Fore.RESET)
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        print(Fore.LIGHTGREEN_EX + f"Video id '{response['id']}' was successfully uploaded." + Fore.RESET)
                    else:
                        raise Exception(f"Unexpected response: {response}")
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = Fore.RED + f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}" + Fore.RESET
                else:
                    raise
            except Exception as e:
                error = Fore.RED + f"A retriable error occurred: {str(e)}" + Fore.RESET

            if error:
                print(error)
                retry += 1
                if retry > MAX_RETRIES:
                    raise Exception("Exceeded maximum retries.")

                sleep_time = random.random() * (2 ** retry)
                print(f"Sleeping {sleep_time:.2f} seconds and retrying...")
                time.sleep(sleep_time)