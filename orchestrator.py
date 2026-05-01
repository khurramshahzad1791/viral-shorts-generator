import os, random, requests, logging, glob
from moviepy.editor import *
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w')
logger = logging.getLogger()

# API keys from GitHub Secrets
PEXELS_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def download_video(url, filename):
    try:
        r = requests.get(url, timeout=30)
        with open(filename, 'wb') as f:
            f.write(r.content)
        return True
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return False

def get_hook():
    # Try Pexels
    url = f"https://api.pexels.com/videos/search?query=funny+animal+fail&per_page=15"
    headers = {"Authorization": PEXELS_KEY}
    resp = requests.get(url, headers=headers).json()
    videos = resp.get('videos', [])
    if videos:
        vid = random.choice(videos)['video_files'][0]['link']
        if download_video(vid, "hook.mp4"):
            return "hook.mp4"
    # Fallback Pixabay
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q=cat&per_page=15"
    resp = requests.get(url).json()
    hits = resp.get('hits', [])
    if hits:
        vid = random.choice(hits)['videos']['medium']['url']
        if download_video(vid, "hook.mp4"):
            return "hook.mp4"
    # Ultimate fallback – use a placeholder if you commit one
    return None

def get_reaction():
    # same as get_hook but query "cat laughing"
    # ... (identical logic, just change search term)
    return None  # placeholder

def get_caption():
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = "Write a funny short caption (max 15 words) for a YouTube Shorts animal reaction video."
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except:
        return random.choice(["😂 Wait for it...", "POV: You're the main character"])

def make_video():
    hook_file = get_hook()
    reaction_file = get_reaction()
    if not hook_file or not reaction_file:
        logger.error("Missing hook or reaction")
        return

    hook = VideoFileClip(hook_file).subclip(0, min(5, VideoFileClip(hook_file).duration))
    reaction = VideoFileClip(reaction_file).subclip(0, min(3, VideoFileClip(reaction_file).duration))
    reaction = reaction.resize(0.25).set_position(("right", "bottom"))

    caption = get_caption()
    txt = TextClip(caption, fontsize=30, color='white', font='Arial', size=hook.size)
    txt = txt.set_position(('center', 'top')).set_duration(hook.duration)

    final = CompositeVideoClip([hook, reaction, txt])
    final.write_videofile("final_video.mp4", codec='libx264', audio_codec='aac')
    logger.info("Video created")

if __name__ == "__main__":
    make_video()
