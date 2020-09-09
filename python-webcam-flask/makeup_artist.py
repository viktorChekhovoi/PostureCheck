from PIL import Image
import numpy as np
import cv2



class Makeup_artist(object):
    def __init__(self):
        self.highest_white_square = 0
        self.frames_counter = 0
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.interval = 5 
        self.samples_number = 15
        self.samples = np.array([])
        self.calibration = -1
        self.highest_current_white_square = 0
        self.frames = [None] * self.interval
        self.side1 = 6
        self.side2 = 8
        self.threshold = 3

        self.alarm_duration = 25
        self.alarm_countdown = [False] * self.alarm_duration
        self.alarm_countdown = np.array(self.alarm_countdown)
        self.alarm_counter = 0

        pass



    def apply_makeup(self, img):
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_np = np.array(frame)
        backup = np.zeros(frame.shape)
            
        if self.frames_counter < self.interval:
            self.frames[self.frames_counter] = frame_np
        else:
            backup = self.frames[self.frames_counter % self.interval]
            self.frames[self.frames_counter % self.interval] = frame_np

        frame_np = frame_np.astype('int32')
        backup = backup.astype('int32')
        diff = np.abs(frame_np - backup) 
        diff = diff.astype('uint8')
        frame_np = frame_np.astype('uint8')
        backup = backup.astype('uint8')
        filled_squares = np.array([])

        filled_squares = np.array([])
        for i in range(0, 480 - self.side1, self.side1):
            for j in range(0, 640 - self.side2, self.side2):
                diff_m = (diff[i:(i + self.side1), j:(j + self.side2)]) >= 15
                if np.sum(diff_m) > self.threshold:
                    filled_squares = np.append(filled_squares, [i, j, i + self.side1, j + self.side2])

                
                
        filled_squares = filled_squares.astype('int32')
        
        
        for i in range(0, filled_squares.shape[0], 4):
            if (filled_squares[i] < filled_squares[self.highest_current_white_square]) and (filled_squares.shape[0] != 0):
                self.highest_current_white_square = i
                
        if filled_squares.shape[0] != 0:
            self.highest_white_square = filled_squares[self.highest_current_white_square]
            diff[filled_squares[self.highest_current_white_square]:filled_squares[self.highest_current_white_square + 2], filled_squares[self.highest_current_white_square + 1]:filled_squares[self.highest_current_white_square + 3]] = 255
        
            if (self.frames_counter >= self.interval) and ((self.frames_counter - self.interval) < self.samples_number):
                self.samples = np.append(self.samples, self.highest_white_square)
                
            if ((self.frames_counter - self.interval) == self.samples_number):
                self.calibration = np.average(self.samples)
                
            cv2.putText(diff, str(self.highest_white_square - self.calibration), (10, 100), self.font, 3, (255, 255, 0), 2, cv2.LINE_AA)
                
        position = self.highest_white_square - self.calibration
        
        if (position > 90) and (self.alarm_countdown.sum() != self.alarm_duration):
            self.alarm_countdown[self.alarm_counter] = True
            self.alarm_counter += 1
            
        if position <= 60 and self.alarm_countdown.sum() > 2:
            self.alarm_counter -= 1
            self.alarm_countdown[self.alarm_counter] = False
            
        temp_sum = self.alarm_countdown.sum()
        #print(temp_sum)
        if temp_sum == self.alarm_duration:
            print ('stop slouching')
        if temp_sum == 0 or temp_sum == 2:
            print("good job!")
        PIL_image = Image.fromarray(np.uint8(diff)).convert('RGB')
        self.frames_counter += 1
        return(PIL_image)
