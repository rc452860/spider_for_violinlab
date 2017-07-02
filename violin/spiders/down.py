#!/usr/bin/env python
# Downloads the video and audio streams from the master json url and recombines
# it into a single file
from __future__ import print_function
import requests
import base64
from tqdm import tqdm
import sys
import subprocess as sp
import os
import distutils
import argparse
import datetime

proxies = {
    "https": "http://127.0.0.1:1080",
    "https": "http://127.0.0.1:1080"
}
session = requests.Session()
session.proxies = proxies
# Prefix for this run
# TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

# Create temp and output paths based on where the executable is located
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
for directory in (TEMP_DIR, OUTPUT_DIR):
    if not os.path.exists(directory):
        print("Creating {}...".format(directory))
        os.makedirs(directory)

# create temp directory right before we need it
# INSTANCE_TEMP = os.path.join(TEMP_DIR, TIMESTAMP)

# Check operating system
OS_WIN = True if os.name == "nt" else False

# Find ffmpeg executable
if OS_WIN:
    FFMPEG_BIN = 'C:\\Users\\rc452\\Desktop\\work\\vimeo-download\\ffmpeg\\bin\\ffmpeg.exe'
else:
    try:
        FFMPEG_BIN = distutils.spawn.find_executable("ffmpeg")
    except AttributeError:
        FFMPEG_BIN = 'ffmpeg'


def download_video(base_url, content, title):
    """Downloads the video portion of teht content into the INSTANCE_TEMP folder"""
    heights = [(i, d['height']) for (i, d) in enumerate(content['video'])]
    idx, _ = max(heights, key=lambda (_, h): h)
    video = content['video'][idx]
    video_base_url = base_url + 'video/' + video['base_url']
    print('video base url:', video_base_url)

    # Create INSTANCE_TEMP if it doesn't exist
    INSTANCE_TEMP = INSTANCE_TEMP = os.path.join(TEMP_DIR, title)
    if not os.path.exists(INSTANCE_TEMP):
        print("Creating {}...".format(INSTANCE_TEMP))
        os.makedirs(INSTANCE_TEMP)

    # Download the video portion of the stream
    filename = os.path.join(INSTANCE_TEMP, "v.mp4")
    video_filename = filename
    print('saving to %s' % filename)

    video_file = open(filename, 'wb')

    init_segment = base64.b64decode(video['init_segment'])
    video_file.write(init_segment)

    for segment in tqdm(video['segments']):
        segment_url = video_base_url + segment['url']
        resp = session.get(segment_url, stream=True)
        if resp.status_code != 200:
            print('not 200!')
            print(resp)
            print(segment_url)
            break
        for chunk in resp:
            video_file.write(chunk)

    video_file.flush()
    video_file.close()


def download_audio(base_url, content, title):
    """Downloads the video portion of teht content into the INSTANCE_TEMP folder"""
    audio = content['audio'][0]
    audio_base_url = base_url + audio['base_url'][3:]
    print('audio base url:', audio_base_url)

    # Create INSTANCE_TEMP if it doesn't exist
    INSTANCE_TEMP = INSTANCE_TEMP = os.path.join(TEMP_DIR, title)
    if not os.path.exists(INSTANCE_TEMP):
        print("Creating {}...".format(INSTANCE_TEMP))
        os.makedirs(INSTANCE_TEMP)

    # Download
    filename = os.path.join(INSTANCE_TEMP, "a.mp3")
    audio_filename = filename
    print('saving to %s' % filename)

    audio_file = open(filename, 'wb')

    init_segment = base64.b64decode(audio['init_segment'])
    audio_file.write(init_segment)

    for segment in tqdm(audio['segments']):
        segment_url = audio_base_url + segment['url']
        resp = session.get(segment_url, stream=True)
        if resp.status_code != 200:
            print('not 200!')
            print(resp)
            print(segment_url)
            break
        for chunk in resp:
            audio_file.write(chunk)

    audio_file.flush()
    audio_file.close()


def merge_audio_video(input_timestamp, output_filename, title):
    audio_filename = os.path.join(TEMP_DIR, title, "a.mp3")
    video_filename = os.path.join(TEMP_DIR, title, "v.mp4")
    command = [FFMPEG_BIN,
               '-i', audio_filename,
               '-i', video_filename,
               '-acodec', 'copy',
               '-vcodec', 'h264',
               output_filename]
    print("ffmpeg command is:", command)

    if OS_WIN:
        sp.call(command, shell=True)
    else:
        sp.call(command)


def down_all(url, title):

    # parse the base_url
    master_json_url = url
    base_url = master_json_url[:master_json_url.rfind('/', 0, -26) - 5]

    # get the content
    resp = session.get(master_json_url)
    content = resp.json()

    # Download the components of the stream
    download_video(base_url, content, title)
    download_audio(base_url, content, title)
