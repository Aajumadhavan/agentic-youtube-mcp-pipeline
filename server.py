from mcp.server.fastmcp import FastMCP
import subprocess
import os
import json

PROJECT_DIR = r"C:\AI_MCP_Server"
VIDEO_SCRIPT = os.path.join(PROJECT_DIR, "create_video.py")
UPLOAD_SCRIPT = os.path.join(PROJECT_DIR, "upload_youtube.py")
VIDEO_FILE = os.path.join(PROJECT_DIR, "Tamil_Shorts.mp4")

mcp = FastMCP("AI Video Automation")

@mcp.tool()
def create_story(topic: str) -> str:
    """Create a Tamil AI story based on a topic."""
    return f"Create an interesting Tamil AI story about {topic}. Include a title, introduction, main story, and conclusion."

@mcp.tool()
def create_video_script(topic: str) -> str:
    """Generate a Tamil video script based on a topic."""
    return f"Create a short Tamil YouTube Shorts script about {topic}. Use an interesting hook, simple Tamil language, engaging facts, and a strong ending."

@mcp.tool()
def create_video(topic: str, script: str) -> str:
    """Create a viral Tamil YouTube Shorts video locally using create_video.py."""
    if not os.path.exists(VIDEO_SCRIPT):
        return f"Error: Video creation script not found: {VIDEO_SCRIPT}"
    try:
        result = subprocess.run(
            ["py", "-3.13", VIDEO_SCRIPT, topic, script],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=600
        )
        if result.returncode == 0:
            return f"Video created successfully at: {VIDEO_FILE}\n{result.stdout}"
        return f"Video creation failed.\nError:\n{result.stderr}"
    except Exception as e:
        return f"Error creating video: {str(e)}"

@mcp.tool()
def upload_to_youtube(title: str, description: str, tags: str = "tamil shorts,tamil facts", privacy: str = "private", video_path: str = VIDEO_FILE) -> str:
    """Upload the generated MP4 video directly to YouTube. privacy can be 'private', 'unlisted', or 'public'."""
    if not os.path.exists(UPLOAD_SCRIPT):
        return f"Error: Upload script not found: {UPLOAD_SCRIPT}"
    if not os.path.exists(video_path):
        return f"Error: Video file not found: {video_path}"
    try:
        result = subprocess.run(
            ["py", "-3.13", UPLOAD_SCRIPT, video_path, title, description, tags, privacy],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=600
        )
        if result.returncode == 0:
            return f"YouTube Upload Complete!\n{result.stdout}"
        return f"YouTube Upload Failed.\nError:\n{result.stderr}"
    except Exception as e:
        return f"Error uploading to YouTube: {str(e)}"

@mcp.tool()
def get_video_info(filename: str = "Tamil_Shorts.mp4") -> str:
    """Get technical metadata of a generated video."""
    video_path = os.path.join(PROJECT_DIR, filename)
    if not os.path.exists(video_path):
        return f"Video not found: {video_path}"
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", video_path],
            capture_output=True, text=True, check=True
        )
        return json.dumps(json.loads(result.stdout), indent=2)
    except Exception as e:
        return f"Error getting video info: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
