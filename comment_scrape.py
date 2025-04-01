import yt_dlp


def get_top_comments(video_url):
    """
    Extracts top comments from a YouTube video.
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

            return top_comments
    except Exception as e:
        print(f"Error extracting comments: {e}")
        return []
