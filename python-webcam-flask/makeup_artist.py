from PIL import Image
import numpy as np
import cv2



class Makeup_artist(object):
    def __init__(self):
        self.counter = 0

        self.position_of_highest_white_square = 0
        self.frames_since_launch = 0 
        delay = 30 
        self.samples = np.array([])
        self.calibration = -1
        self.highest = 0
        self.square_positions = [None] * 30
        self.frames = [None] * 5

        self.alarm_countdown = np.array([False] * 25)
        self.alarm_counter = 0

        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        pass



    def apply_makeup(self, img):
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_np = np.array(frame)
        
        backup = np.zeros(frame.shape)
            
        if self.frames_since_launch < 5:
            self.frames[self.frames_since_launch] = frame_np
        else:
            backup = self.frames[self.frames_since_launch % 5]
            self.frames[self.frames_since_launch % 5] = frame_np

        frame_np = frame_np.astype('int32')
        backup = backup.astype('int32')
        diff = np.abs(frame_np - backup) 
        diff = diff.astype('uint8')
        frame_np = frame_np.astype('uint8')
        backup = backup.astype('uint8')

        PIL_image = Image.fromarray(np.uint8(diff)).convert('RGB')

        side1 = 30
        side2 = 40
        a = np.array([])
        for i in range(0, 480 - side1, side1):
            for j in range(0, 640 - side2, side2):
                diff_m = (diff[i:(i + side1), j:(j + side2)]) >= 15
                if np.sum(diff_m) > 8:
                    a = np.append(a, [i, j, i + side1, j + side2])
                    
        filled_squares = a


        filled_squares = filled_squares.astype('int32')
        
        
        for i in range(0, filled_squares.shape[0], 4):
            if (filled_squares[i] < filled_squares[self.highest]) and (filled_squares.shape[0] != 0):
                self.highest = i
                
        if filled_squares.shape[0] != 0:
            self.position_of_highest_white_square = filled_squares[self.highest]
            diff[filled_squares[self.highest]:filled_squares[self.highest + 2], filled_squares[self.highest + 1]:filled_squares[self.highest + 3]] = 255
        
            if (self.frames_since_launch >= 5) and ((self.frames_since_launch - 5) < 15):
                samples = np.append(self.samples, self.position_of_highest_white_square)
                
            if ((self.frames_since_launch - 5) == 15):
                self.calibration = np.average(self.samples)
                
            cv2.putText(diff, str(self.position_of_highest_white_square - self.calibration), (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 0), 2, cv2.LINE_AA)
                
        position = self.position_of_highest_white_square - self.calibration
        
        if (position > 90) and (self.alarm_countdown.sum() != 25):
            self.alarm_countdown[self.alarm_counter] = True
            self.alarm_counter += 1
            
        if position <= 60 and self.alarm_countdown.sum() > 2:
            self.alarm_counter -= 1
            self.alarm_countdown[self.alarm_counter] = False
            
        temp_sum = self.alarm_countdown.sum()
        
        if temp_sum == 25:
            print ('Stop slouching!/')
        #if temp_sum == 0:

        return(PIL_image)
        #return img.transpose(Image.FLIP_LEFT_RIGHT)
