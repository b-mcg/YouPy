YouPy
=====

Python program utilizing the pytube library, for the downloading and optional mp3 conversion of YouTube videos.

Requires:

https://github.com/Nficano/pytube.git

ffmpeg

Example usage:

python2 youpy.py http://www.youtube.com/video_link -f youtube_video -dir youtube_video_directory


Flags:

-c	converts the downloaded youtube video into an mp3 format

-do	deletes original video file if -c flag is given
