import os
import sys
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

PROJECT_DIR = r"C:\AI_MCP_Server"
os.chdir(PROJECT_DIR)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRET = os.path.join(PROJECT_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(PROJECT_DIR, "youtube_token.pickle")


def get_youtube_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET):
                raise FileNotFoundError("client_secret.json not found in C:\\AI_MCP_Server")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
    return build("youtube", "v3", credentials=creds)


def upload_video(video_path, title, description, tags_csv="", privacy="private"):
    youtube = get_youtube_service()
    tags = [t.strip() for t in tags_csv.split(",") if t.strip()]
    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": "27"
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = request.next_chunk()
    video_id = response.get("id")
    return f"https://youtube.com{video_id}"


if __name__ == "__main__":
    args = sys.argv
    v_file = args.__getitem__(1) if len(args) > 1 else os.path.join(PROJECT_DIR, "Tamil_Shorts.mp4")
    v_title = args.__getitem__(2) if len(args) > 2 else "Amazing Space Secrets in Tamil #Shorts"
    v_desc = args.__getitem__(3) if len(args) > 3 else "Mind-blowing facts in Tamil! #Shorts #TamilFacts"
    v_tags = args.__getitem__(4) if len(args) > 4 else "tamil shorts,space facts tamil,tamil facts"
    v_priv = args.__getitem__(5) if len(args) > 5 else "private"
    url = upload_video(v_file, v_title, v_desc, v_tags, v_priv)
    print(f"UPLOAD_SUCCESS: {url}")
