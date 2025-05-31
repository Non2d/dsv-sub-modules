This is a module for converting audio to text.

## Environment Setup

Set python version to 3.11.5.

Install pytorch here: https://pytorch.org/get-started/locally/
- The version of torch, torchvision, torchaudio version can vary based on the machine's GPU environment. Hence, these libraries are not included in requiments.txt.

Install ffmpeg here: https://ffmpeg.org/download.html or "winget install --id=Gyan.FFmpeg -e"
- This is required by yt-dlp, which downloads audio from YouTube.

Install basic dependencies by:
- cd audio-to-text
- pip install -r requirements.txt
