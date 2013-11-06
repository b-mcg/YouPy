#!/usr/bin/env python2

# Imports
from pytube import YouTube
from pytube.utils import print_status
from pytube.exceptions import *
import subprocess
import re
import argparse
import os
from sys import exit


# Author and licensing
__Author__ = "bmcg"
__Email__ = "bmcg0890@gmail.com"
__License__ = """
Copyright (C) 2013-2015  bmcg	<bmcg0890@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

# Version number
Version		=		'v0.0.1'


def build_args():
	""" 
	Builds and returns a parser object 
	of command line arguments.

	"""
	parser			=	argparse.ArgumentParser(description='YouTube video download options.')

	# Adding url option
	parser.add_argument('url', type=str, 
				help='url of video to be downloaded(Required).', 
				metavar=''
				)
	# Adding directory to store video
	parser.add_argument('-dir', '--directory', default=os.getcwd(), type=str, 
				required=False, help='Desired directory to be stored in(Optional.  Default: CWD).',
				metavar=''
				)
	# Adding filename to store video as
	parser.add_argument('-f', '--filename', type=str, required=False, help='''Desired filename for video(Optional.  Default: 
										video title).''',
				metavar=''
				)
	# Adding conversion option
	parser.add_argument('-c', action="store_true", default=False, required=False,
				help='video to mp3 conversion of video using ffmpeg(Optional).' 
				)
	# Add delete original option
	parser.add_argument('-do', action="store_true", default=False, required=False,
				help='Deletes original video copy if -c and -do is given(Optional).'
				)

	# Returning parser object
	return parser


def arg_parser(parser):
	""" 
	Checks for command line options and returns a dictionary 
	of command line values.

	parser		:	parser object returned by build_opts()

	"""

	# Parse arguments
	args			=	parser.parse_args()
	
	# Builds and returns a dictionary
	return { 'u': args.url
	       , 'dir': args.directory
	       , 'f': args.filename if '-f' or '--filename' in args else None
	       , 'c': args.c
	       , 'do': args.do 
	       }


def menu(lst):
	"""
	Prints out available video types 
	in a menu form

	lst		:	list of strings to be printed out as a menu

	"""
	# Assign an empty list for mapping user input to list item
	item_count	=		1
	print '\n'

	# Print out items in original list to screen
	for i in xrange(len(lst)):
		print '{0:>2}) {1:<30}'.format(item_count, lst[i])

	# After each item in the list is printed, append it with the item_count number to new_lst
		lst[i]			=		lst[i].replace(lst[i], ''.join((str(item_count), lst[i])))
		item_count 		+=		1

	# Loop until the user's input corresponds to an item in new_lst
	while True:
		try:
			user_in			=		raw_input('\n> ')

	# Loop the items in new_lst and check the beginning for matching user input to item in new_lst 
			for i in xrange(len(lst)):
				if user_in in lst[i][:len(user_in)]:
					return lst[int(user_in) - 1][len(user_in):]

	# If the user's input doesn't correspond to an item in new_lst print an invalid selection message
			else:
				print '\nInvalid selection.  Try again.\n'

	# Break and quit program if keyboard interrupt signal is given
		except KeyboardInterrupt:
			print '\n\nInterrrupt signal given.\nQuitting...\n\n'
			exit(1)


def download(args):
	"""
	Downloads youtube video

	args		:	parsed command line arguments

	"""

	# Call the YoutTube Function
	youtube			=	YouTube()

	# Set the video url
	try:
		youtube.url		=	args['u']

	# Catch invalid YouTube URLs
	except YouTubeError:
		print "\n\nError:  Failed on ('{}').\nCheck for valid YouTube URL.\n\n".format(args['u'])
		exit(2)

	# Create menu of video format/resolution options
	video_option_selection	=	menu(map(str, youtube.videos))

	# Extract video types into a list of a single string
	video_format 		=	re.findall(r'\(.(\w{3,4})\)', video_option_selection)[0]
	video_resolution	=	re.findall(r'-\s*(\w{3,4})', video_option_selection)[0]

	# Set filename if -f/--filename option is given
	if args['f']:
		youtube.filename		=		args['f']

	# Set the video format	
	try:
		set_video_format_res	=	youtube.get(video_format, video_resolution)

	# Catch multiple videos returned error
	except MultipleObjectsReturned:
		print '\n\nError: More than one video returned.\n\n'
		exit(1)

	# Download video
	download_video		=	set_video_format_res.download(args['dir'],
						on_progress=print_status, 
						on_finish=video_to_mp3 if args['c'] else None)

	# Delete original video file if -do/--delete and -c/--convert is given
	if args['c'] and args['do']:
	
	# Call remove_original 
		remove_original(youtube.filename, args['dir'], video_format)
	

def check_for_mp3_codec(filename):
	"""
	Uses a subprocess call to ffprobe 
	to get audio codec output
	on flv videos.

	filename	:	filename of video to check codecs

	"""

	# Set subprocess to be called
	ffprobe_cmd		=		'ffprobe -show_streams'.split()

	# Append filename to subprocess cmd
	ffprobe_cmd.append(filename)

	# Call and return the output of the subprocess
	return subprocess.check_output(ffprobe_cmd)


def video_to_mp3(filename):
	"""
	Uses a subprocess call to FFMPEG 
	for converting the video file to mp3 format

	filename	:	filename of video to be converted

	"""

	# Split beginning of ffmpeg_cmd for subprocess calling and append filename
	ffmpeg_cmd		=		'ffmpeg -i'.split()
	ffmpeg_cmd.append(filename)

	# Checking for mp4 format
	if 'mp4' in filename:

	# Replace original extension with mp3
		ffmpeg_cmd.append(filename.replace('.mp4', '.mp3'))

	# Check for flv format
	elif 'flv' in filename:

	# Check if flv video already has an mp3 audio codec
		try:
	
	# Use a regular expression to search output of ffprobe for mp3 codec
			if 'mp3' in re.findall(r'(codec_name=mp3)', check_for_mp3_codec(filename))[0]:

	# Extend ffmpeg list with conversion instructions
				ffmpeg_cmd.extend('-acodec copy -ac 2 -ab 128k -vn -n'.split())

	# Append output filename with .mp3 extension
				ffmpeg_cmd.append(filename.replace('.flv', '.mp3'))
	
	# If mp3 isn't found in ffprobe's output use regular conversion options
		except IndexError:
			ffmpeg_cmd.append(filename.replace('.flv', '.mp3'))

	# Check for 3gp format
	elif '3gp' in filename:
		ffmpeg_cmd.append(filename.replace('.3gp', '.mp3'))

	else:
	# Otherwise should be .webm format
		ffmpeg_cmd.append(filename.replace('.webm', '.mp3'))

	# Call ffmpeg subprocess
	try:
		subprocess.call(ffmpeg_cmd)

	# Catch non-existant file and if ffmpeg is not installed
	except OSError:
		print '\n\nError: Check whether video file exists or that ffmpeg is installed.\n\n'
		exit(1)


def remove_original(filename, arg_dir, form):
	"""
	Removes original video file if both -c/--convert
	and -do/--delete options are given.

	filename	:	filename of video to be deleted

	arg_dir		:	directory containing video file

	form		:	format extension of video file

	"""

	# Join the directory and filename with extension
	pathname		=	os.path.abspath(os.path.join(arg_dir, '{0}.{1}'.format(filename, form)))

	# Remove original video
	os.remove(pathname)


def main():
	""" 
	main()

	Parses command line options and calls download.

	"""

	# Handles command line options
	args			=	arg_parser(build_args())

	# Start downloading
	print '\n\nYouPy {0} by: {1} Running...'.format(Version, __Author__)
	download(args)


if __name__ == '__main__':
	main()
