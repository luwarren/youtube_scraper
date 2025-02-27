from youtube_transcript_api import YouTubeTranscriptApi

def get_youtube_transcript(video_id):
    """
    Fetches the transcript of a YouTube video using YouTubeTranscriptApi.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = "\n".join([entry['text'] for entry in transcript])
        return transcript_text
    except Exception as e:
        return f"Error fetching transcript: {e}"
