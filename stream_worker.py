import sys
import subprocess
import time

if len(sys.argv) < 3:
    print("Error: Missing arguments")
    sys.exit(1)

STREAM_KEY = sys.argv[1]
VIDEO_URL = sys.argv[2]
RTMP_URL = "rtmp://a.rtmp.youtube.com/live2"


def get_direct_link(url):
    """Fetch direct 720p stream links."""
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "--get-url",
        url
    ]
    try:
        return subprocess.check_output(cmd, text=True).strip().split("\n")
    except:
        return None


def stream_loop():
    print(f"Worker Started: Key ••••{STREAM_KEY[-4:]}")

    while True:
        try:
            cmd = ["yt-dlp", "--flat-playlist", "--print", "url", VIDEO_URL]
            playlist = subprocess.check_output(cmd, text=True).strip().split("\n")
            playlist = [x for x in playlist if x]
        except:
            playlist = []

        if not playlist:
            playlist = [VIDEO_URL]

        for video in playlist:
            print("→ Streaming:", video)

            links = get_direct_link(video)
            if not links:
                print("Invalid Link, Skipping...")
                time.sleep(2)
                continue

            ffmpeg_cmd = [
                "ffmpeg", "-re",
                "-thread_queue_size", "4096",
                "-i", links[0]
            ]

            if len(links) > 1:
                ffmpeg_cmd.extend(["-thread_queue_size", "4096", "-i", links[1]])

            ffmpeg_cmd.extend([
                "-map", "0:v",
                "-map", f"{1 if len(links) > 1 else 0}:a",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-tune", "zerolatency",
                "-vf", "scale=1280:720,format=yuv420p,fps=30",
                "-b:v", "2500k", "-maxrate", "3000k", "-bufsize", "6000k",
                "-g", "60",
                "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
                "-f", "flv",
                f"{RTMP_URL}/{STREAM_KEY}"
            ])

            subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)


if __name__ == "__main__":
    stream_loop()
