import youtube_dl


url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
output_dir = "C:\\Users\\User\\Downloads\\"

# youtube-dl --prefer-ffmpeg --extract-audio --audio-format mp3 --audio-quality 0 --embed-thumbnail <VIDEO_SONG_OR_PLAYLIST_URL>

ytdl_options = {
    'outtmpl': output_dir + '%(title)s.%(ext)s'
}

with youtube_dl.YoutubeDL(ytdl_options) as ytdl:
    ytdl.download([url])