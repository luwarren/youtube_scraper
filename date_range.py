import yt_dlp
import json
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi


def scrape_youtube():
    channel_url = input("Enter YouTube channel URL: ")
    end_date = input("Enter end date (YYYY-MM-DD): ")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    results = []

    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlistend': 50,  # Scrape 50 at a time
        'force_generic_extractor': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        reached_end_date = False  # Flag to track stopping condition

        while not reached_end_date:
            info = ydl.extract_info(channel_url, download=False)
            if 'entries' not in info or not info['entries']:
                break

            for video in info['entries']:
                video_id = video.get('id')
                upload_date_str = video.get('upload_date')  # Format: YYYYMMDD

                if not video_id or not upload_date_str:
                    continue

                upload_date = datetime.strptime(upload_date_str, "%Y%m%d")

                if upload_date < end_date:
                    reached_end_date = True
                    break  # Exit loop when the end date is surpassed

                results.append({
                    'video_id': video_id,
                    'upload_date': upload_date.strftime("%Y-%m-%d")
                })

    if results:
        with open("output.json", 'w') as f:
            json.dump(results, f, indent=4)
        print("Scraped data saved to output.json")
    else:
        print("No videos found within the specified date range.")


def get_transcript(video_id):
    """
    Fetches the transcript of a YouTube video using YouTubeTranscriptApi.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = "\n".join([entry['text'] for entry in transcript])
        return transcript_text
    except Exception as e:
        return f"Error fetching transcript: {e}"

if __name__ == "__main__":
    scrape_youtube()
