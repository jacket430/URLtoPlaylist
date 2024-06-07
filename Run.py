import os
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CLIENT_SECRETS_FILE = "/Secret/secret.json"

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_authenticated_service():
    credentials = None
    if os.path.exists('token.json'):
        credentials = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(credentials.to_json())

    return build('youtube', 'v3', credentials=credentials)

def list_playlists(youtube):
    request = youtube.playlists().list(
        part="snippet,contentDetails",
        mine=True,
        maxResults=25
    )
    response = request.execute()

    playlists = response.get('items', [])
    for i, playlist in enumerate(playlists):
        print(f"{i + 1}. Title: {playlist['snippet']['title']}, Playlist ID: {playlist['id']}")
    
    return playlists

def add_video_to_playlist(youtube, playlist_id, video_id):
    try:
        request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        )
        response = request.execute()
        return response
    except HttpError as e:
        print(f"An error occurred: {e}")
        print(f"Skipping video ID {video_id}")

def read_video_urls(file_path):
    with open(file_path, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]
    return urls

def main():
    youtube = get_authenticated_service()
    playlists = list_playlists(youtube)

    choice = int(input("Enter the number of the playlist you want to add videos to: ")) - 1
    selected_playlist_id = playlists[choice]['id']

    video_urls = read_video_urls("URLs.txt")

    for url in video_urls:
        video_id = url.split("v=")[-1]
        add_video_to_playlist(youtube, selected_playlist_id, video_id)
        print(f"Attempted to add video {video_id} to playlist {selected_playlist_id}")

if __name__ == '__main__':
    main()
