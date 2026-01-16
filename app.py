"""
Hebrew Video/Audio Downloader - Streamlit Cloud App
====================================================
A modern, RTL Hebrew web application for downloading video/audio content.
Built for deployment on Streamlit Cloud.
"""

import streamlit as st
import yt_dlp
import tempfile
import os
import re
import logging
from datetime import datetime
from pathlib import Path

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

def setup_logging():
    """Configure logging for terminal and browser console output."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def log_to_console(message: str, level: str = "info"):
    """Log message to both terminal and inject into browser console."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted = f"[{timestamp}] {message}"
    
    if level == "error":
        logger.error(message)
        st.markdown(f'<script>console.error("{formatted}")</script>', unsafe_allow_html=True)
    elif level == "warning":
        logger.warning(message)
        st.markdown(f'<script>console.warn("{formatted}")</script>', unsafe_allow_html=True)
    else:
        logger.info(message)
        st.markdown(f'<script>console.log("{formatted}")</script>', unsafe_allow_html=True)

# =============================================================================
# CSS STYLING - Modern RTL Hebrew Design
# =============================================================================

def inject_custom_css():
    """Inject modern RTL CSS styling with Hebrew fonts."""
    st.markdown("""
    <style>
        /* Google Font - Heebo for Hebrew */
        @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800&display=swap');
        
        /* Global Styles */
        * {
            font-family: 'Heebo', sans-serif !important;
        }
        
        html, body, [class*="css"] {
            direction: rtl !important;
            text-align: right !important;
        }
        
        .stApp {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
        }
        
        /* Hide Streamlit branding */
        #MainMenu, footer, header {
            visibility: hidden;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.1);
        }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #667eea, #764ba2);
            border-radius: 4px;
        }
        
        /* Main Container */
        .main-container {
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* Hero Section */
        .hero-section {
            text-align: center;
            padding: 3rem 0;
            margin-bottom: 2rem;
        }
        
        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1rem;
            text-shadow: 0 0 40px rgba(102, 126, 234, 0.3);
        }
        
        .hero-subtitle {
            font-size: 1.3rem;
            color: rgba(255, 255, 255, 0.7);
            font-weight: 300;
            margin-bottom: 2rem;
        }
        
        /* Glass Card Effect */
        .glass-card {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 24px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
            border-color: rgba(102, 126, 234, 0.3);
        }
        
        /* Metadata Card */
        .metadata-card {
            display: flex;
            gap: 1.5rem;
            align-items: center;
            flex-direction: row-reverse;
        }
        
        .metadata-thumbnail {
            width: 200px;
            height: 112px;
            border-radius: 12px;
            object-fit: cover;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }
        
        .metadata-info {
            flex: 1;
        }
        
        .metadata-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.75rem;
            line-height: 1.4;
        }
        
        .metadata-detail {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(255, 255, 255, 0.1);
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.8);
            margin-left: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        /* Section Title */
        .section-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        /* Input styling */
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.1) !important;
            border: 2px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 16px !important;
            color: white !important;
            padding: 1rem 1.5rem !important;
            font-size: 1.1rem !important;
            direction: ltr !important;
            text-align: left !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.3) !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: rgba(255, 255, 255, 0.4) !important;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 0.75rem 2rem !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4) !important;
            width: 100%;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 30px rgba(102, 126, 234, 0.6) !important;
        }
        
        /* Download button special styling */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 1rem 2rem !important;
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 20px rgba(56, 239, 125, 0.4) !important;
            width: 100%;
        }
        
        .stDownloadButton > button:hover {
            transform: translateY(-2px) scale(1.02) !important;
            box-shadow: 0 8px 30px rgba(56, 239, 125, 0.6) !important;
        }
        
        /* Select box styling */
        .stSelectbox > div > div {
            background: rgba(255, 255, 255, 0.1) !important;
            border: 2px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
            color: white !important;
        }
        
        .stSelectbox > div > div:hover {
            border-color: #667eea !important;
        }
        
        /* Radio button styling */
        .stRadio > div {
            background: rgba(255, 255, 255, 0.05);
            padding: 1rem;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .stRadio > div > label, .stRadio label {
            color: white !important;
        }
        
        /* Radio button option text - force white */
        .stRadio div[data-testid="stRadio"] label,
        .stRadio div[role="radiogroup"] label,
        [data-testid="stRadio"] span,
        .stRadio span,
        .stRadio p {
            color: white !important;
        }
        
        /* Video title in metadata - force white */
        h3, h2, h4, [data-testid="stMarkdownContainer"] h3 {
            color: white !important;
        }
        
        /* All paragraph and span text */
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] span {
            color: white !important;
        }
        
        /* Spinner */
        .stSpinner > div {
            border-color: #667eea !important;
        }
        
        /* Success/Error messages */
        .stSuccess, .stError, .stWarning, .stInfo {
            border-radius: 12px !important;
            padding: 1rem !important;
        }
        
        /* Progress bar */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #667eea, #764ba2, #f093fb) !important;
        }
        
        /* Columns */
        [data-testid="column"] {
            padding: 0.5rem;
        }
        
        /* Labels */
        .stSelectbox label, .stRadio label, .stTextInput label {
            color: rgba(255, 255, 255, 0.9) !important;
            font-weight: 500 !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background: rgba(255, 255, 255, 0.05) !important;
            border-radius: 12px !important;
            color: white !important;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem;
            color: rgba(255, 255, 255, 0.4);
            font-size: 0.9rem;
        }
        
        .footer a {
            color: #667eea;
            text-decoration: none;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .hero-title {
                font-size: 2rem;
            }
            .metadata-card {
                flex-direction: column;
            }
            .metadata-thumbnail {
                width: 100%;
                height: auto;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def validate_url(url: str) -> bool:
    """Validate if the URL is a valid video/audio URL."""
    if not url or not url.strip():
        return False
    
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url.strip()))

def format_duration(seconds) -> str:
    """Format duration in seconds to HH:MM:SS or MM:SS."""
    if not seconds:
        return "לא ידוע"
    
    # Convert to int in case it's a float
    seconds = int(seconds)
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def get_platform_name(url: str) -> str:
    """Extract platform name from URL."""
    platforms = {
        'youtube.com': 'YouTube',
        'youtu.be': 'YouTube',
        'tiktok.com': 'TikTok',
        'instagram.com': 'Instagram',
        'facebook.com': 'Facebook',
        'twitter.com': 'X (Twitter)',
        'x.com': 'X (Twitter)',
        'vimeo.com': 'Vimeo',
        'dailymotion.com': 'Dailymotion',
        'twitch.tv': 'Twitch',
        'reddit.com': 'Reddit',
        'soundcloud.com': 'SoundCloud',
        'spotify.com': 'Spotify',
    }
    
    for domain, name in platforms.items():
        if domain in url.lower():
            return name
    return "אחר"

def get_platform_emoji(platform: str) -> str:
    """Get emoji for platform."""
    emojis = {
        'YouTube': '🎬',
        'TikTok': '🎵',
        'Instagram': '📸',
        'Facebook': '👥',
        'X (Twitter)': '🐦',
        'Vimeo': '🎥',
        'Dailymotion': '📺',
        'Twitch': '🎮',
        'Reddit': '🤖',
        'SoundCloud': '🔊',
        'Spotify': '🎧',
    }
    return emojis.get(platform, '🌐')

# =============================================================================
# YT-DLP FUNCTIONS
# =============================================================================

def extract_metadata(url: str) -> dict:
    """Extract video/audio metadata without downloading."""
    log_to_console(f"Extracting metadata from: {url}")
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'skip_download': True,
        'socket_timeout': 30,
        'retries': 3,
        'fragment_retries': 3,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
            }
        },
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info:
                metadata = {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'platform': get_platform_name(url),
                    'url': url,
                    'formats': info.get('formats', []),
                }
                log_to_console(f"Metadata extracted: {metadata['title']}")
                return metadata
    except Exception as e:
        log_to_console(f"Error extracting metadata: {str(e)}", "error")
        raise e
    
    return None

def build_ydl_options(temp_dir: str, download_type: str, extension: str, quality: str) -> dict:
    """Build yt-dlp options based on user selection."""
    
    base_opts = {
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'merge_output_format': extension if download_type == 'video' else None,
        'postprocessor_args': ['-y'],  # Overwrite without asking
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        },
    }
    
    if download_type == 'video':
        # Video quality mapping
        quality_map = {
            'הכי טוב': 'bestvideo+bestaudio/best',
            '4K (2160p)': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]',
            '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        }
        
        base_opts['format'] = quality_map.get(quality, 'bestvideo+bestaudio/best')
        
        # Post-processing for video
        if extension == 'mp4':
            base_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]
        elif extension == 'mkv':
            base_opts['merge_output_format'] = 'mkv'
        elif extension == 'webm':
            base_opts['merge_output_format'] = 'webm'
            
    else:  # Audio
        # Audio quality mapping
        quality_map = {
            'הכי טוב': '0',
            '192kbps': '192',
            '128kbps': '128',
        }
        
        audio_quality = quality_map.get(quality, '0')
        
        # Audio format mapping
        format_map = {
            'mp3': 'mp3',
            'm4a': 'm4a',
            'wav': 'wav',
        }
        
        audio_format = format_map.get(extension, 'mp3')
        
        base_opts['format'] = 'bestaudio/best'
        base_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
            'preferredquality': audio_quality,
        }]
    
    return base_opts

def download_content(url: str, download_type: str, extension: str, quality: str) -> tuple:
    """Download video/audio content and return file path and bytes."""
    log_to_console(f"Starting download: type={download_type}, ext={extension}, quality={quality}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        ydl_opts = build_ydl_options(temp_dir, download_type, extension, quality)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Find the downloaded file
            files = list(Path(temp_dir).glob('*'))
            if files:
                downloaded_file = files[0]
                log_to_console(f"Download complete: {downloaded_file.name}")
                
                # Read file into memory
                with open(downloaded_file, 'rb') as f:
                    file_bytes = f.read()
                
                return downloaded_file.name, file_bytes
            else:
                raise Exception("לא נמצא קובץ שהורד")
                
        except Exception as e:
            log_to_console(f"Download error: {str(e)}", "error")
            raise e

# =============================================================================
# STREAMLIT APP
# =============================================================================

def main():
    """Main application entry point."""
    
    # Page config
    st.set_page_config(
        page_title="הורדת סרטונים ושמע",
        page_icon="📥",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Inject CSS
    inject_custom_css()
    
    # Initialize session state
    if 'metadata' not in st.session_state:
        st.session_state.metadata = None
    if 'file_ready' not in st.session_state:
        st.session_state.file_ready = None
    if 'file_name' not in st.session_state:
        st.session_state.file_name = None
    
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">📥 הורדת סרטונים ושמע</div>
        <div class="hero-subtitle">הורידו סרטונים ושמע מכל פלטפורמה בקלות</div>
    </div>
    """, unsafe_allow_html=True)
    
    # URL Input Section
    st.markdown('<div class="section-title">🔗 הזינו קישור</div>', unsafe_allow_html=True)
    
    url = st.text_input(
        "כתובת URL",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed",
        key="url_input"
    )
    
    analyze_btn = st.button("🔍 נתח קישור", key="analyze_btn", use_container_width=True)
    
    # Handle URL analysis
    if analyze_btn and url:
        if not validate_url(url):
            st.error("❌ הקישור שהוזן אינו תקין. אנא הזינו קישור מלא.")
        else:
            with st.spinner("🔄 מנתח קישור..."):
                try:
                    metadata = extract_metadata(url)
                    if metadata:
                        st.session_state.metadata = metadata
                        st.session_state.file_ready = None
                        st.success("✅ הקישור נותח בהצלחה!")
                    else:
                        st.error("❌ לא ניתן לנתח את הקישור. נסו קישור אחר.")
                except Exception as e:
                    error_msg = str(e)
                    if "login" in error_msg.lower() or "cookies" in error_msg.lower():
                        st.error("� פלטפורמה זו דורשת התחברות. נסו פלטפורמה אחרת (YouTube, TikTok ציבורי, וכו').")
                    elif "instagram" in error_msg.lower():
                        st.error("📸 אינסטגרם דורש התחברות. נסו סרטון ציבורי מפלטפורמה אחרת.")
                    elif "403" in error_msg or "blocked" in error_msg.lower() or "rate" in error_msg.lower():
                        st.error("🚫 הגישה נחסמה זמנית. המתינו דקה ונסו שוב.")
                    elif "not available" in error_msg.lower():
                        st.error("❌ התוכן אינו זמין או פרטי. נסו קישור אחר.")
                    else:
                        st.error(f"❌ שגיאה: {error_msg[:100]}")
    
    # Display metadata and download options
    if st.session_state.metadata:
        metadata = st.session_state.metadata
        
        # Metadata Section
        st.markdown('<div class="section-title">📋 פרטי התוכן</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if metadata.get('thumbnail'):
                st.image(metadata['thumbnail'], use_container_width=True)
        
        with col2:
            st.markdown(f"### {metadata['title']}")
            
            platform = metadata['platform']
            emoji = get_platform_emoji(platform)
            duration = format_duration(metadata['duration'])
            uploader = metadata.get('uploader', 'לא ידוע')
            
            st.markdown(f"""
            <div style="margin-top: 1rem;">
                <span class="metadata-detail">{emoji} {platform}</span>
                <span class="metadata-detail">⏱️ {duration}</span>
                <span class="metadata-detail">👤 {uploader}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Configuration Section
        st.markdown('<div class="section-title">⚙️ הגדרות הורדה</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            download_type = st.radio(
                "סוג הורדה",
                options=["וידאו", "אודיו"],
                horizontal=False,
                key="download_type"
            )
        
        with col2:
            if download_type == "וידאו":
                extension = st.selectbox(
                    "פורמט",
                    options=["mp4", "mkv", "webm"],
                    key="extension_video"
                )
            else:
                extension = st.selectbox(
                    "פורמט",
                    options=["mp3", "m4a", "wav"],
                    key="extension_audio"
                )
        
        with col3:
            if download_type == "וידאו":
                quality = st.selectbox(
                    "איכות",
                    options=["הכי טוב", "4K (2160p)", "1080p", "720p"],
                    key="quality_video"
                )
            else:
                quality = st.selectbox(
                    "איכות",
                    options=["הכי טוב", "192kbps", "128kbps"],
                    key="quality_audio"
                )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Download button
        download_btn = st.button(
            "📥 הכן קובץ להורדה",
            key="download_btn",
            use_container_width=True
        )
        
        # Handle download
        if download_btn:
            with st.spinner("⏳ מוריד ומעבד את הקובץ... אנא המתינו"):
                try:
                    dl_type = 'video' if download_type == "וידאו" else 'audio'
                    file_name, file_bytes = download_content(
                        metadata['url'],
                        dl_type,
                        extension,
                        quality
                    )
                    st.session_state.file_ready = file_bytes
                    st.session_state.file_name = file_name
                    st.success("✅ הקובץ מוכן להורדה!")
                except Exception as e:
                    error_msg = str(e)
                    if "403" in error_msg:
                        st.error("🚫 הגישה נחסמה. נסו קישור אחר או פלטפורמה אחרת.")
                    else:
                        st.error(f"❌ שגיאה בהורדה: {error_msg}")
        
        # Show download button if file is ready
        if st.session_state.file_ready:
            st.markdown('<div class="section-title">✨ הקובץ מוכן!</div>', unsafe_allow_html=True)
            
            # Determine MIME type
            ext = Path(st.session_state.file_name).suffix.lower()
            mime_types = {
                '.mp4': 'video/mp4',
                '.mkv': 'video/x-matroska',
                '.webm': 'video/webm',
                '.mp3': 'audio/mpeg',
                '.m4a': 'audio/mp4',
                '.wav': 'audio/wav',
            }
            mime_type = mime_types.get(ext, 'application/octet-stream')
            
            st.download_button(
                label="📥 הורד עכשיו",
                data=st.session_state.file_ready,
                file_name=st.session_state.file_name,
                mime=mime_type,
            )
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>🚀 נבנה עם Streamlit ו-yt-dlp</p>
        <p>⚠️ השתמשו בכלי זה רק להורדת תוכן שיש לכם זכות להוריד</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
