Cecilio Music Player

Cecilio Music Player is a small and convenient music player with support for local files, streaming (YouTube, Spotify, SoundCloud), and a unique music visualization system. The program supports common functions such as shuffling tracks, repeating, volume control, and various visualization modes. I plan to further develop this small project when I have free time and :) mood. Note that the streaming function might not work as intended.

Features

Local File Playback

Add audio files to the playlist (supports .mp3, .wav, .flac).
Playback controls:
Play/Pause
Next/Previous
Shuffle — Shuffle the tracks in the playlist.
Repeat — Repeat the current track.

Streaming Playback

Add tracks and playlists via URL:
YouTube (using pytube).
SoundCloud (using soundcloud API).
Spotify (using spotipy).

Music Visualization

Four unique visualization modes:
Polygons — Dynamic polygons reacting to the music.
Waves — Vibrant waves.
Stars — Star-shaped visual effects.
Lines — Frequency-responsive lines.
Visualizations are influenced by:
Current volume.
Active features (Shuffle, Repeat).

Intuitive Interface

Two-language support: English and Russian.
Sliders for controlling:
Volume
Track progress

Development Timeline

2025-01-07

Initial development of the program.
Basic playback features implemented:
Adding files to the playlist.
Playback controls: Play, Pause, Next, Previous.
Basic ring-shaped visualization.

2025-01-08

Logic for Shuffle and Repeat buttons added.
Fixed issue with auto-playing tracks after switching to the next or previous track.

2025-01-09

Visualization improved:
Added new modes: Polygons, Waves, Stars, Lines.
Visualization now reacts to volume, Shuffle, and Repeat modes.
Increased the number of waves in Waves mode.
Optimized visualization to reduce CPU usage.

2025-01-10

Streaming functionality added:
YouTube integration (via pytube): Add tracks or playlists via URL.
SoundCloud integration (via soundcloud API).
Spotify integration (via spotipy).

Improved user interface:
Added a Streaming menu for managing streaming platforms.
Translated all interface elements into both English and Russian.
Updated the requirements.txt file for program dependencies.

Installation

1.  Clone the repository:
git clone https://github.com/yourusername/cecilio-music-player.git cd cecilio-music-player
2.	Install dependencies:
pip install -r requirements.txt
3.	Run the program:
python cecilio_main.py

License

This project is licensed under the MIT License.

