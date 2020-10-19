#!/usr/bin/env python

import os, sys, shutil
import ffmpeg
import pygame
from numpy import arange

if len(sys.argv) > 1:
    
    # prep input
    input_file   = os.path.abspath(sys.argv[1])
    input_folder = os.path.dirname(input_file)
    tmp_dir      = input_folder + os.sep + '_tmp'
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    info      = ffmpeg.probe(input_file)
    im_w      = 0
    im_h      = 0
    fps       = 0
    frames    = 0
    aud_dur   = 0
    aud_slice = 0.0
    for stream in info['streams']:
        if stream['codec_type'] == 'video':
            im_w = int(stream['coded_width' ])
            im_h = int(stream['coded_height'])
            fps  = int(stream['codec_time_base'].split('/')[1])
            frames = int(stream['nb_frames'])
    for stream in info['streams']:        
        if stream['codec_type'] == 'audio':
            aud_dur = float(stream['duration'])
            aud_slice = aud_dur / float(frames)
    print('STATS = w:{} - h:{} - fps:{} - frames:{} - aud:{} - slice:{}'.format(im_w, im_h, fps, frames, aud_dur, aud_slice))

    print('Exporting image sequence...')
    input_vid = ffmpeg.input(input_file)
    video_stream = input_vid.video
    audio_stream = input_vid.audio
    out = tmp_dir + os.sep + os.path.basename(input_file)[:-4] + '.%04d.jpg'
    out_stream = ffmpeg.output(video_stream, out, **{'qscale:v': 2})
    ffmpeg.run(out_stream, quiet=True, overwrite_output=True)
    print('Done! Exporting audio...')
    
    a = 1
    for i in arange(0.0, aud_dur, aud_slice):
        start = i
        frm = '%04d' % a
        out = tmp_dir + os.sep + os.path.basename(input_file)[:-3] + frm +  '.wav'
        out_stream = ffmpeg.output(audio_stream, out, ss=start, t=aud_slice)
        ffmpeg.run(out_stream, quiet=True, overwrite_output=True)
        a += 1
    print('Done! Starting playback...')

    # display sequence
    pygame.init()

    print('Preloading images...')
    frame_array = []
    for i in range(frames):
        img_path  = tmp_dir + os.sep + os.path.basename(input_file)[:-4]
        img_path += '.%04d.jpg' % (i+1)
        frame_array.append(pygame.image.load(img_path))
    print('Done!')

    print('Preloading audio...')
    aud_array = []
    for i in range(frames):
        aud_path  = tmp_dir + os.sep + os.path.basename(input_file)[:-4]
        aud_path += '.%04d.wav' % (i+1)
        aud_array.append(pygame.mixer.Sound(aud_path))
    print('Done!')

    font = pygame.font.Font('freesansbold.ttf', 14)
    gameDisplay = pygame.display.set_mode((im_w,im_h))
    pygame.display.set_caption('nv_seqview')
    closed = False
    paused = False
    clock = pygame.time.Clock()
    frame = frames

    while not closed:
        if frame >= frames:
            frame = 1
        # input ###########################################
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                closed = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    closed = True
                if event.key == pygame.K_ESCAPE:
                    closed = True
                if event.key == pygame.K_SPACE:
                    pygame.mixer.stop()
                    if paused:
                        paused = False
                    else:
                        paused = True
                if event.key == pygame.K_LEFT:
                    paused = True
                    frame -= 1
                    text_str   = 'frame : %04d' % frame
                    text_frame = font.render(text_str, True, (255, 255, 255))
                    text_str   = 'framerate : %d' % clock.get_fps()
                    text_fps   = font.render(text_str, True, (255, 255, 255))
                    aud_array[frame - 1].play()
                    gameDisplay.blit(frame_array[frame - 1], (0,0))
                    gameDisplay.blit(text_frame, (10,10))
                    gameDisplay.blit(text_fps, (10,30))
                    pygame.display.update()
                    clock.tick(fps)
                if event.key == pygame.K_RIGHT:
                    paused = True
                    frame += 1
                    text_str   = 'frame : %04d' % frame
                    text_frame = font.render(text_str, True, (255, 255, 255))
                    text_str   = 'framerate : %d' % clock.get_fps()
                    text_fps   = font.render(text_str, True, (255, 255, 255))
                    aud_array[frame - 1].play()
                    gameDisplay.blit(frame_array[frame - 1], (0,0))
                    gameDisplay.blit(text_frame, (10,10))
                    gameDisplay.blit(text_fps, (10,30))
                    pygame.display.update()
                    clock.tick(fps)
                    

        # DO THE THING! ###################################
        if not paused:
            text_str   = 'frame : %04d' % frame
            text_frame = font.render(text_str, True, (255, 255, 255))
            text_str   = 'framerate : %d' % clock.get_fps()
            text_fps   = font.render(text_str, True, (255, 255, 255))
            aud_array[frame - 1].play()
            gameDisplay.blit(frame_array[frame - 1], (0,0))
            gameDisplay.blit(text_frame, (10,10))
            gameDisplay.blit(text_fps, (10,30))
            pygame.display.update()
            clock.tick(fps)
            frame += 1
    
    print('Done!')

    # cleanup
    print('Cleaning up...')
    shutil.rmtree(tmp_dir)
    print('Done! Exiting.\n\n')

else:
    print('Add a file, moron...\n\n')
