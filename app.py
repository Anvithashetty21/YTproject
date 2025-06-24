import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import isodate
from youtube_utils import (
    get_channel_data, get_playlists, get_video_ids,
    get_video_data, get_comment_data,
    store_to_mongo, migrate_data_from_mongo,
    db, ENGINE, API_KEY
)

st.set_page_config(page_title="YouTube Data Harvesting", layout="wide")
with st.sidebar:
    choice = option_menu(None, ["Home", "Extract", "View"],
                         icons=["house", "cloud-download", "table"],
                         default_index=0)

if choice == "Home":
    st.title("YouTube Data Harvesting & Warehousing 👩‍💻")
    st.markdown("""
    **Domain:** Social Media | **Skills:** Python, Streamlit, MongoDB, SQL Server  
    👇 GitHub: [Anvithashetty21](https://github.com/Anvithashetty21)
    """)

elif choice == "Extract":
    st.header("Extract & Store Data from YouTube Channels 📥")
    channel_ids = st.text_area("Enter one or more YouTube Channel IDs (one per line):",
                               help="Paste one channel ID per line.")
    ids = [line.strip() for line in channel_ids.splitlines() if line.strip()]
    if ids:
        for cid in ids:
            st.write(f"### 🔍 Channel Info for ID: `{cid}`")
            ch = get_channel_data(cid)

            if ch is None:
                st.warning(f"Channel ID `{cid}` is invalid or has no data.")
                continue

            # ✅ Display basic channel information
            st.write(f"**Name:** {ch['channel_name']}")
            st.write(f"**Subscribers:** {ch['subscribers_count']:,}")
            st.write(f"**Views:** {ch['views_count']:,}")
            st.write(f"**Videos:** {ch['video_count']:,}")

            if st.button(f"✅ Fetch and Save this channel ({cid})"):
                pl = get_playlists(cid)
                vids = get_video_ids(ch["playlist_id"])
                vdata = get_video_data(vids, cid)  # ✅ IMPORTANT
                cdata = get_comment_data(vids)

                store_to_mongo([ch], "channel_details")
                store_to_mongo(pl, "playlist_details")
                store_to_mongo(vdata, "video_details")  # ✅ Includes channel_id
                store_to_mongo(cdata, "comment_details")
                st.success(f"Data for channel `{cid}` saved to MongoDB! ✅")

elif choice == "View":
    st.header("Query & Visualize 🔍")

    # ✅ SHOW EXISTING CHANNELS IN SQL
    try:
        existing_channels = pd.read_sql("SELECT channel_id, channel_name, subscribers_count, views_count, video_count FROM channels", con=ENGINE)
        if not existing_channels.empty:
            st.markdown("### 🗂️ Channels already saved in the database")
            st.dataframe(existing_channels)
        else:
            st.warning("No channel data found in SQL database.")
    except Exception as e:
        st.error(f"Error retrieving channel data: {e}")

    if st.button("Migrate to SQL Server"):
        try:
            migrate_data_from_mongo(db)
        except Exception as e:
            st.error(f"Error migrating data: {e}")

    query_choice = st.selectbox("Choose a query:", [
        "Names of all videos and their corresponding channels",
        "Channel with the most number of videos",
        "Top 10 most viewed videos and their channels",
        "Number of comments for each video",
        "Videos with highest number of likes and their channel names",
        "Total likes for each video",
        "Total views for each channel",
        "Names of all channels that published videos in 2022",
        "Average duration of all videos in each channel",
        "Videos with the highest number of comments and their channel names"
    ])

    if st.button("Run Query") and query_choice:
        if query_choice == "Average duration of all videos in each channel":
            df_videos = pd.read_sql("SELECT channel_id, title, duration FROM videos", con=ENGINE)
            df_channels = pd.read_sql("SELECT channel_id, channel_name FROM channels", con=ENGINE)

            merged = df_videos.merge(df_channels, on="channel_id", how="left")
            merged["duration_minutes"] = merged["duration"].apply(lambda x: isodate.parse_duration(x).total_seconds() / 60)

            results = merged.groupby("channel_name")["duration_minutes"].mean().reset_index()
            results["average_minutes"] = results["duration_minutes"].round(2)

            st.write(f"### Results for: {query_choice}")
            st.dataframe(results[["channel_name", "average_minutes"]])

        else:
            query_mapping = {
                "Names of all videos and their corresponding channels": """
                    SELECT v.title, c.channel_name
                    FROM videos v
                    LEFT JOIN channels c ON v.channel_id = c.channel_id
                """,
                "Channel with the most number of videos": """
                    SELECT TOP 1 channel_name, COUNT(video_id) AS video_count
                    FROM videos v
                    LEFT JOIN channels c ON v.channel_id = c.channel_id
                    GROUP BY channel_name
                    ORDER BY video_count DESC
                """,
                "Top 10 most viewed videos and their channels": """
                    SELECT TOP 10 v.title, c.channel_name, v.view_count
                    FROM videos v
                    LEFT JOIN channels c ON v.channel_id = c.channel_id
                    ORDER BY v.view_count DESC
                """,
                "Number of comments for each video": """
                    SELECT v.title, COUNT(cm.comment_id) AS comment_count
                    FROM videos v
                    LEFT JOIN comments cm ON v.video_id = cm.video_id
                    GROUP BY v.title
                """,
                "Videos with highest number of likes and their channel names": """
                    SELECT TOP 10 v.title, c.channel_name, v.like_count
                    FROM videos v
                    LEFT JOIN channels c ON v.channel_id = c.channel_id
                    ORDER BY v.like_count DESC
                """,
                "Total likes for each video": """
                    SELECT title, like_count
                    FROM videos
                """,
                "Total views for each channel": """
                    SELECT channel_name, SUM(view_count) AS total_views
                    FROM videos v
                    LEFT JOIN channels c ON v.channel_id = c.channel_id
                    GROUP BY channel_name
                """,
                "Names of all channels that published videos in 2022": """
                    SELECT DISTINCT c.channel_name
                    FROM videos v
                    LEFT JOIN channels c ON v.channel_id = c.channel_id
                    WHERE YEAR(v.published_at) = 2022
                """,
                "Videos with the highest number of comments and their channel names": """
                    SELECT TOP 10 v.title, c.channel_name, v.comment_count
                    FROM videos v
                    LEFT JOIN channels c ON v.channel_id = c.channel_id
                    ORDER BY v.comment_count DESC
                """
            }
            sql = query_mapping.get(query_choice)
            results = pd.read_sql(sql, con=ENGINE)
            st.write(f"### Results for: {query_choice}")
            st.dataframe(results)

st.write(f"🚀 Current API_KEY in use: {API_KEY[:5]}...{API_KEY[-5:]}")

