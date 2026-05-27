import trafilatura
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import re

def extract_from_url(url):
    """
    Extracts main text content from a blog or news article URL.
    """
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        text = trafilatura.extract(downloaded)
        return text
    return None

def extract_from_youtube(url):
    """
    Extracts transcript from a YouTube video URL.
    """
    video_id = None
    # Parse video ID from different types of YT links
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        video_id = parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            video_id = parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.path[:7] == '/embed/':
            video_id = parsed_url.path[7:]
        elif parsed_url.path[:3] == '/v/':
            video_id = parsed_url.path[3:]

    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([item['text'] for item in transcript_list])
        return transcript
    except Exception as e:
        print(f"Error fetching YouTube transcript: {e}")
        return None

def get_content_from_link(link):
    """
    Dispatcher to determine if link is YouTube or General Web.
    """
    if 'youtube.com' in link or 'youtu.be' in link:
        return extract_from_youtube(link)
    else:
        return extract_from_url(link)
