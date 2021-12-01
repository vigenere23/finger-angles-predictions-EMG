from datetime import datetime
import cv2 as cv
from handDetected import HandDetection
import time 
from datetime import datetime
import pandas as pd
import os

class HandRecorder:

    def __init__(self, hand_side, finger):
        self.capture = None
        self.isRecording = False
        self.hand_side = hand_side
        self.finger = finger
        self.detection = HandDetection()
        self.angles_recorded = {
            'timestamp': [],
            'mcp angle':[],
            'pip angle':[],
            'dip angle':[]
        }

    # end record with p button
    def start_record_hand(self):
        if self.isRecording == False:
            self.capture = cv.VideoCapture(0)
            self.isRecording = True
            while True:
                if self._end_record_after_click():
                    cv.destroyAllWindows()
                    break
                self._detect_hand_while_record()
            cv.waitKey(0)
        else : 
            print('Is recording!!')

    def start_record_hand_during(self, seconde):
        if self.isRecording == False:
            self.capture = cv.VideoCapture(0)
            self.isRecording = True
            timeout = time.time() + seconde
            while True:
                self._detect_hand_while_record()
                if self._end_record_after_click() or self._end_record_after_time(timeout):
                    cv.destroyAllWindows()
                    break
            cv.waitKey(0)
        else : 
            print('Is recording!!')

    
    def end_record(self):
        self.capture.release()

    def _detect_hand_while_record(self):
        if self.isRecording:
            succes, image = self.capture.read()
            image = cv.flip(image, 1)
            self.detection.detect_finger(image, self.hand_side, self.finger)
            mcp_angle, pip_angle, dip_angle = self.detection.get_angles_in_finger(self.finger)
            self._save_hand_angles(mcp_angle, pip_angle, dip_angle)
            cv.putText(image, 'mcp angle: {:.2f}deg'.format(mcp_angle), (10, 70), cv.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)
            cv.putText(image, 'pip angle: {:.2f}deg'.format(pip_angle), (10, 90), cv.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)
            cv.putText(image, 'dip angle: {:.2f}deg'.format(dip_angle), (10, 110), cv.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)
            cv.imshow('Hand', image)

    def _save_hand_angles(self, mcp_angle, pip_angle, dip_angle):
        self.angles_recorded['timestamp'].append(datetime.now().timestamp())
        self.angles_recorded['mcp angle'].append(mcp_angle)
        self.angles_recorded['pip angle'].append(pip_angle)
        self.angles_recorded['dip angle'].append(dip_angle)

    def _end_record_after_click(self):
        return  cv.waitKey(1) & 0xFF==ord('p')
    
    def _end_record_after_time(self, timeout):
        return  time.time() > timeout

    def export_hand_angles_recorded_to_csv(self):
        df = pd.DataFrame(self.angles_recorded)
        if not os.path.exists('export'):
            os.makedirs('export')
        timesptamp = time.time()
        name_file = str(f'export/Hand_angles_record{timesptamp}.csv')
        df.to_csv('export/Hand_angles_record.csv', index=False)
    
    def display_hand_angles_recorded(self):
        df = pd.DataFrame(self.angles_recorded)
        print(df)

    # def _display_hud_info(self, image, ):
    #     cv.putText(image, 'mcp angle: {:.2f}deg'.format(mcp_angle), (10, 70), cv.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)

