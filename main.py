import json
import yt_dlp
import os
import concurrent.futures
from yt_dlp.utils import ExtractorError
from tqdm import tqdm  # Progress bar
from comment_scrape import get_top_comments
from transcript_scrape import get_transcript

def extract_video_metadata(video_url, channel_name, progress_bar):
    """
    Extracts metadata and top comments for a given YouTube video.
    Updates progress bar on completion.
    """
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(video_url, download=False)

            video_id = video_info.get('id')
            transcript_text = get_transcript(video_id)
            top_comments = get_top_comments(video_url)

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

            channel_dir = os.path.join("output", channel_name)
            os.makedirs(channel_dir, exist_ok=True)

            json_file = os.path.join(channel_dir, f"{video_id}.json")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(filtered_info, f, indent=4, ensure_ascii=False)

    except ExtractorError as e:
        print(f"Error extracting video info: {e}")

    progress_bar.update(1)  # Update progress bar after processing each video

def get_youtube_data():
    """
    Extracts video metadata and comments from a YouTube channel.
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

    channel_name = info.get('title', 'Unknown_Channel').replace(" ", "_")
    video_urls = [entry['url'] for entry in info.get('entries', []) if 'url' in entry]

    # Initialize progress bar
    with tqdm(total=len(video_urls), desc=f"Processing Videos from {channel_name}", unit="video") as progress_bar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(extract_video_metadata, video_url, channel_name, progress_bar) for video_url in video_urls]
            concurrent.futures.wait(futures)  # Wait for all tasks to finish

if __name__ == "__main__":
    get_youtube_data()
