import numpy as np
import cv2
import pygame

def findWhitePixels(diff, threshold, height, width):
    side1 = 30
    side2 = 40
    a = np.array([])
    for i in range(0, height - side1, side1):
        for j in range(0, width - side2, side2):
            diff_m = (diff[i:(i + side1), j:(j + side2)]) >= 15
            if np.sum(diff_m) > threshold:
                a = np.append(a, [i, j, i + side1, j + side2])
    return a
            

cap = cv2.VideoCapture(0)

pygame.init()
pygame.mixer.music.load("music.wav")

position_of_highest_white_square = 0
frames_since_launch = 0 
font = cv2.FONT_HERSHEY_SIMPLEX
delay_between_subtracted_frames = 5 
samples_number = 15
delay = 30 
samples = np.array([])
calibration = -1
highest = 0
square_positions = [None] * delay
frames = [None] * delay_between_subtracted_frames

alarm_duration = 25
alarm_countdown = [False] * alarm_duration
alarm_countdown = np.array(alarm_countdown)
alarm_counter = 0

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output15.avi', fourcc, 10.0, (640,480), 0)

while True:
    returned_frame, frame = cap.read()
    height, width, t = frame.shape

    if returned_frame==True:

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_np = np.array(frame)
        
        backup = np.zeros(frame.shape)
            
        if frames_since_launch < delay_between_subtracted_frames:
            frames[frames_since_launch] = frame_np
        else:
            backup = frames[frames_since_launch % delay_between_subtracted_frames]
            frames[frames_since_launch % delay_between_subtracted_frames] = frame_np

        frame_np = frame_np.astype('int32')
        backup = backup.astype('int32')
        diff = np.abs(frame_np - backup) 
        diff = diff.astype('uint8')
        frame_np = frame_np.astype('uint8')
        backup = backup.astype('uint8')

        filled_squares = findWhitePixels(diff, 8, 480, 640)
        filled_squares = filled_squares.astype('int32')
        
        
        for i in range(0, filled_squares.shape[0], 4):
            if (filled_squares[i] < filled_squares[highest]) and (filled_squares.shape[0] != 0):
                highest = i
                
        if filled_squares.shape[0] != 0:
            position_of_highest_white_square = filled_squares[highest]
            diff[filled_squares[highest]:filled_squares[highest + 2], filled_squares[highest + 1]:filled_squares[highest + 3]] = 255
        
            if (frames_since_launch >= delay_between_subtracted_frames) and ((frames_since_launch - delay_between_subtracted_frames) < samples_number):
                samples = np.append(samples, position_of_highest_white_square)
                
            if ((frames_since_launch - delay_between_subtracted_frames) == samples_number):
                calibration = np.average(samples)
                
            cv2.putText(diff, str(position_of_highest_white_square - calibration), (10, 100), font, 3, (255, 255, 0), 2, cv2.LINE_AA)
                
        position = position_of_highest_white_square - calibration
        
        if (position > 90) and (alarm_countdown.sum() != alarm_duration):
            alarm_countdown[alarm_counter] = True
            alarm_counter += 1
            
        if position <= 60 and alarm_countdown.sum() > 2:
            alarm_counter -= 1
            alarm_countdown[alarm_counter] = False
            
        temp_sum = alarm_countdown.sum()
        music_playing = pygame.mixer.music.get_busy()
        
        if temp_sum == alarm_duration and (not music_playing):
            pygame.mixer.music.play()
            print ('finished')
        if temp_sum == 0 and music_playing:
            pygame.mixer.music.stop()
        out.write(diff)
        
            
        cv2.imshow('frame',diff)
        frames_since_launch += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
cap.release()

out.release()

cv2.destroyAllWindows()