#!/usr/bin/env python

import os
import sys
import shutil
import time
import tempfile
import ffmpeg
import pygame
from numpy import arange

###############################################################################
def draw(frame_list, audio_list, fps):
    global FRAMES
    global FRAME
    global input_file

    if FRAME > FRAMES:
        FRAME = 1
    if FRAME == 0:
        FRAME = FRAMES

    text_str   = 'file name : %s' % input_file
    text_file  = font.render(text_str, True, (255, 255, 255), (0, 0, 0))
    text_str   = 'frame     : %04d' % FRAME
    text_frame = font.render(text_str, True, (255, 255, 255), (0, 0, 0))
    text_str   = 'framerate : %d' % clock.get_fps()
    text_fps   = font.render(text_str, True, (255, 255, 255), (0, 0, 0))
    audio_list[FRAME - 1].play()
    gameDisplay.blit(frame_list[FRAME - 1], (0,0))
    gameDisplay.blit(text_file, (10,10))
    gameDisplay.blit(text_frame, (10,25))
    gameDisplay.blit(text_fps, (10,40))
    pygame.display.update()
    clock.tick(fps)

###############################################################################
if len(sys.argv) > 1:
    # prep input ffmpeg ###################################
    input_file   = os.path.abspath(sys.argv[1])
    input_folder = os.path.dirname(input_file)
    # tmp_dir      = input_folder + os.sep + '_tmp'
    tmp_dir      = tempfile.gettempdir() + os.sep + 'nv_seqview_' + str(time.time())
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    info      = ffmpeg.probe(input_file)
    IM_W      = 0
    IM_H      = 0
    FPS       = 0
    FRAMES    = 0
    AUD_DUR   = 0
    AUD_SLICE = 0.0
    for stream in info['streams']:
        if stream['codec_type'] == 'video':
            IM_W = int(stream['coded_width' ])
            IM_H = int(stream['coded_height'])
            FPS  = int(stream['codec_time_base'].split('/')[1])
            FRAMES = int(stream['nb_frames'])
    for stream in info['streams']:        
        if stream['codec_type'] == 'audio':
            AUD_DUR = float(stream['duration'])
            AUD_SLICE = AUD_DUR / float(FRAMES)
    # print('STATS = w:{} - h:{} - fps:{} - frames:{} - aud:{} - slice:{}'.format(IM_W, IM_H, FPS, FRAMES, AUD_DUR, AUD_SLICE))

    print('Exporting image sequence...')
    input_vid = ffmpeg.input(input_file)
    video_stream = input_vid.video
    audio_stream = input_vid.audio
    out = tmp_dir + os.sep + os.path.basename(input_file)[:-4] + '.%04d.jpg'
    out_stream = ffmpeg.output(video_stream, out, **{'qscale:v': 2})
    ffmpeg.run(out_stream, quiet=True, overwrite_output=True)
    print('Done! Exporting audio...')

    a = 1
    for i in arange(0.0, AUD_DUR, AUD_SLICE):
        start = i
        frm = '%04d' % a
        out = tmp_dir + os.sep + os.path.basename(input_file)[:-3] + frm +  '.wav'
        out_stream = ffmpeg.output(audio_stream, out, ss=start, t=AUD_SLICE)
        ffmpeg.run(out_stream, quiet=True, overwrite_output=True)
        a += 1
    print('Done! Starting playback...')

    # preload #############################################
    pygame.init()
    print('Preloading images...')
    frame_array = []
    for i in range(FRAMES):
        img_path  = tmp_dir + os.sep + os.path.basename(input_file)[:-4]
        img_path += '.%04d.jpg' % (i+1)
        frame_array.append(pygame.image.load(img_path))
    print('Done!')

    print('Preloading audio...')
    aud_array = []
    for i in range(FRAMES):
        aud_path  = tmp_dir + os.sep + os.path.basename(input_file)[:-4]
        aud_path += '.%04d.wav' % (i+1)
        aud_array.append(pygame.mixer.Sound(aud_path))
    print('Done!')

    # display sequence ####################################
    # font = pygame.font.Font('freesansbold.ttf', 10)
    font = pygame.font.Font('fonts/SpaceMono-Regular.ttf', 10)
    gameDisplay = pygame.display.set_mode((IM_W,IM_H))
    pygame.display.set_caption('nv_seqview')
    CLOSED = False
    PAUSED = False
    BACKWD = False
    clock = pygame.time.Clock()
    FRAME = FRAMES

    while not CLOSED:
        # input ###########################################
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                CLOSED = True
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_q) or (event.key == pygame.K_ESCAPE):
                    CLOSED = True
                if event.key == pygame.K_SPACE:
                    pygame.mixer.stop()
                    if PAUSED:
                        PAUSED = False
                    else:
                        PAUSED = True
                if event.key == pygame.K_r:
                    if BACKWD:
                        BACKWD = False
                    else:
                        BACKWD = True
                if event.key == pygame.K_LEFT:
                    PAUSED = True
                    FRAME -= 1
                    draw(frame_array, aud_array, FPS)
                if event.key == pygame.K_RIGHT:
                    PAUSED = True
                    FRAME += 1
                    draw(frame_array, aud_array, FPS)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_COMMA]:
            PAUSED = True
            FRAME -= 1
            draw(frame_array, aud_array, FPS * 0.5)
        if keys[pygame.K_PERIOD]:
            PAUSED = True
            FRAME += 1
            draw(frame_array, aud_array, FPS * 0.5)
        if keys[pygame.K_LEFTBRACKET]:
            PAUSED = True
            FRAME -= 1
            draw(frame_array, aud_array, FPS * 3)
        if keys[pygame.K_RIGHTBRACKET]:
            PAUSED = True
            FRAME += 1
            draw(frame_array, aud_array, FPS * 3)
        # DO THE THING! ###################################
        if not PAUSED:
            if not BACKWD:
                FRAME += 1
            else:
                FRAME -= 1
            draw(frame_array, aud_array, FPS)
    print('Done!')
    # cleanup
    # print('Cleaning up...')
    # time.sleep(5)
    # shutil.rmtree(tmp_dir)
    print('Done! Exiting.\n\n')
else:
    print('Add a file, moron...\n\n')
