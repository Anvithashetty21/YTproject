import pymongo
import pandas as pd
from googleapiclient.discovery import build
import sqlalchemy as sal

# ==========================
# ✅ CONFIGURE KEYS DIRECTLY
# ==========================
API_KEY = "AIzaSyBcJPjV7FMnwAGswxcvT0dsAbtuHQZr7EU"
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "youtube_data"

# ==========================
# ✅ SQL SERVER CONFIG
# ==========================
CONNECTION_STRING = (
    "mssql+pyodbc://ASUS_ROG\\SQLEXPRESS/master?"
    "driver=ODBC+Driver+17+for+SQL+Server"
)
ENGINE = sal.create_engine(CONNECTION_STRING)

# ==========================
# ✅ BUILD YOUTUBE SERVICE
# ==========================
youtube = build("youtube", "v3", developerKey=API_KEY)

# ==========================
# ✅ UTILITY FUNCTIONS
# ==========================
def get_channel_data(channel_id):
    """Fetch basic channel details."""
    resp = youtube.channels().list(part="snippet,contentDetails,statistics", id=channel_id).execute()
    items = resp.get("items", [])

    if not items:
        return None

    item = items[0]
    stats = item.get("statistics", {})
    return {
        "channel_id": channel_id,
        "channel_name": item["snippet"].get("title", ""),
        "channel_description": item["snippet"].get("description", ""),
        "subscribers_count": int(stats.get("subscriberCount", 0)),
        "views_count": int(stats.get("viewCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
        "playlist_id": item["contentDetails"].get("relatedPlaylists", {}).get("uploads", "")
    }


def get_playlists(channel_id):
    """Fetch playlists for a given channel."""
    playlists = []
    token = None
    while True:
        resp = youtube.playlists().list(part="snippet,contentDetails",
                                         channelId=channel_id,
                                         maxResults=50,
                                         pageToken=token).execute()
        for p in resp.get("items", []):
            playlists.append({
                "playlist_id": p["id"],
                "channel_id": channel_id,
                "playlist_title": p["snippet"].get("title", ""),
                "playlist_count": int(p["contentDetails"].get("itemCount", 0))
            })
        token = resp.get("nextPageToken")
        if not token:
            break
    return playlists


def get_video_ids(playlist_id):
    """Retrieve all video ids within a playlist."""
    ids = []
    token = None
    while True:
        resp = youtube.playlistItems().list(part="contentDetails",
                                              playlistId=playlist_id,
                                              maxResults=50,
                                              pageToken=token).execute()
        for item in resp.get("items", []):
            ids.append(item["contentDetails"]["videoId"])
        token = resp.get("nextPageToken")
        if not token:
            break
    return ids


def get_video_data(video_ids, channel_id):
    """Fetch statistics and metadata for a batch of video ids, including channel_id."""
    data = []
    for i in range(0, len(video_ids), 50):  # YouTube API limit
        chunk = video_ids[i:i + 50]
        resp = youtube.videos().list(part="snippet,contentDetails,statistics",
                                      id=",".join(chunk)).execute()
        for v in resp.get("items", []):
            data.append({
                "video_id": v["id"],
                "channel_id": channel_id,
                "title": v["snippet"].get("title", ""),
                "published_at": v["snippet"].get("publishedAt", ""),
                "view_count": int(v["statistics"].get("viewCount", 0)),
                "like_count": int(v["statistics"].get("likeCount", 0)),
                "comment_count": int(v["statistics"].get("commentCount", 0)),
                "duration": v["contentDetails"].get("duration", "")
            })
    return data


def get_comment_data(video_ids):
    """Retrieve the top-level comments for each video id."""
    comments = []
    for vid in video_ids:
        token = None
        while True:
            try:
                resp = youtube.commentThreads().list(part="snippet",
                                                      videoId=vid,
                                                      maxResults=100,
                                                      pageToken=token).execute()
                for c in resp.get("items", []):
                    snip = c["snippet"]["topLevelComment"]["snippet"]
                    comments.append({
                        "video_id": vid,
                        "comment_id": c.get("id"),
                        "author": snip.get("authorDisplayName", ""),
                        "text": snip.get("textDisplay", ""),
                        "likes": snip.get("likeCount", 0),
                        "published_at": snip.get("publishedAt", "")
                    })
                token = resp.get("nextPageToken")
                if not token:
                    break
            except Exception:
                break
    return comments


# ==========================
# ✅ MONGO UTILITY
# ==========================
client = pymongo.MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

def store_to_mongo(data, key):
    """Store a dict or list of dicts to a MongoDB collection."""
    db[key].insert_many(data if isinstance(data, list) else [data])

# ==========================
# ✅ MIGRATION FUNCTION
# ==========================
def migrate_data_from_mongo(db):
    """Migrate channel, playlist, video, and comment data from MongoDB to SQL Server."""
    channels_df = pd.DataFrame(list(db.channel_details.find()))
    playlists_df = pd.DataFrame(list(db.playlist_details.find()))
    videos_df = pd.DataFrame(list(db.video_details.find()))
    comments_df = pd.DataFrame(list(db.comment_details.find()))

    for df in [channels_df, playlists_df, videos_df, comments_df]:
        if "_id" in df.columns:
            df.drop(columns=["_id"], inplace=True)

    channels_df.to_sql("channels", con=ENGINE, if_exists="replace", index=False)
    playlists_df.to_sql("playlists", con=ENGINE, if_exists="replace", index=False)
    videos_df.to_sql("videos", con=ENGINE, if_exists="replace", index=False)
    comments_df.to_sql("comments", con=ENGINE, if_exists="replace", index=False)

