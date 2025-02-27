import json
import yt_dlp
import os
import concurrent.futures
from yt_dlp.utils import ExtractorError
from youtube_transcript_api import YouTubeTranscriptApi
from tqdm import tqdm  # Progress bar

# Ensure output directory exists
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_youtube_transcript(video_id):
    """
    Fetches the transcript of a YouTube video using YouTubeTranscriptApi.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return "\n".join([entry['text'] for entry in transcript])
    except Exception as e:
        return f"Error fetching transcript: {e}"

def extract_video_metadata(video_url, progress_bar):
    """
    Extracts metadata and top comments for a given YouTube video.
    Updates progress bar on completion.
    """
    ydl_opts = {
        'quiet': True,
        'getcomments': True,
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(video_url, download=False)

            comments = video_info.get('comments', [])
            sorted_comments = sorted(comments, key=lambda x: x.get('like_count', 0), reverse=True)
            top_comments = [
                {
                    "parent": comment.get("parent"),
                    "text": comment.get("text"),
                    "like_count": comment.get("like_count"),
                    "author": comment.get("author"),
                    "author_is_uploader": comment.get("author_is_uploader"),
                    "is_favorited": comment.get("is_favorited"),
                    "is_pinned": comment.get("is_pinned"),
                }
                for comment in sorted_comments[:10]
            ]

            video_id = video_info.get('id')
            transcript_text = get_youtube_transcript(video_id)

            filtered_info = {
                'channel': video_info.get('channel'),
                'uploader': video_info.get('uploader_id'),
                'upload_date': video_info.get('upload_date'),
                'title': video_info.get('title'),
                'description': video_info.get('description'),
                'total_views': video_info.get('view_count'),
                'like_count': video_info.get('like_count'),
                'comment_count': video_info.get('comment_count'),
                'top_comments': top_comments,
                'transcript': transcript_text
            }

            json_file = os.path.join(OUTPUT_DIR, f"{video_id}.json")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(filtered_info, f, indent=4, ensure_ascii=False)

    except ExtractorError as e:
        print(f"Error extracting video info: {e}")

    progress_bar.update(1)  # Update progress bar after processing each video

def get_youtube_data():
    """
    Extracts video metadata and comments from a YouTube channel efficiently.
    Allows user input for channel URL and number of videos.
    """
    channel_url = input("Enter the YouTube channel URL: ")
    max_videos = int(input("Enter the number of videos to process: "))

    ydl_opts = {
        'quiet': False,
        'extract_flat': True,
        'playlistend': max_videos,
        'force_generic_extractor': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
    except ExtractorError as e:
        print(f"Error extracting channel info: {e}")
        return

    video_urls = [entry['url'] for entry in info.get('entries', []) if 'url' in entry]

    # Initialize progress bar
    with tqdm(total=len(video_urls), desc="Processing Videos", unit="video") as progress_bar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(extract_video_metadata, video_url, progress_bar) for video_url in video_urls]
            concurrent.futures.wait(futures)  # Wait for all tasks to finish

if __name__ == "__main__":
    get_youtube_data()
