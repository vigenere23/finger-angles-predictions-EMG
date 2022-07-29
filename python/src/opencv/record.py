import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import cv2 as cv
import pandas as pd

from src.opencv.handDetected import HandDetection


class HandRecorder:
    def __init__(self, hand_side, finger, camera: int):
        self.capture = None
        self.isRecording = False
        self.hand_side = hand_side
        self.finger = finger
        self.detection = HandDetection()
        self.angles_recorded: Dict[str, List[Any]] = {
            "timestamp": [],
            "mcp angle": [],
            "pip angle": [],
            "dip angle": [],
        }
        self.camera = camera

    def start_record_hand(self):
        if not self.isRecording:
            self.capture = cv.VideoCapture(self.camera)
            self.isRecording = True
            while True:
                if self._end_record_after_click():
                    cv.destroyAllWindows()
                    break
                self._detect_hand_while_record()
            cv.waitKey(0)
        else:
            print("Is recording!!")

    def start_record_hand_during(self, seconds):
        if not self.isRecording:
            self.capture = cv.VideoCapture(self.camera)
            self.isRecording = True
            timeout = datetime.now() + timedelta(seconds=seconds)
            while True:
                self._detect_hand_while_record()
                if self._end_record_after_click() or self._end_record_after_time(
                    timeout
                ):
                    cv.destroyAllWindows()
                    break
            cv.waitKey(0)
        else:
            print("Is recording!!")

    def end_record(self):
        self.capture.release()

    def _detect_hand_while_record(self):
        if self.isRecording:
            succes, image = self.capture.read()
            image = cv.flip(image, 1)
            self.detection.detect_finger(image, self.hand_side, self.finger)
            mcp_angle, pip_angle, dip_angle = self.detection.get_angles_in_finger(
                self.finger
            )
            self._save_hand_angles(mcp_angle, pip_angle, dip_angle)
            cv.putText(
                image,
                "mcp angle: {:.2f}deg".format(mcp_angle),
                (10, 70),
                cv.FONT_HERSHEY_PLAIN,
                1,
                (255, 0, 255),
                1,
            )
            cv.putText(
                image,
                "pip angle: {:.2f}deg".format(pip_angle),
                (10, 90),
                cv.FONT_HERSHEY_PLAIN,
                1,
                (255, 0, 255),
                1,
            )
            cv.putText(
                image,
                "dip angle: {:.2f}deg".format(dip_angle),
                (10, 110),
                cv.FONT_HERSHEY_PLAIN,
                1,
                (255, 0, 255),
                1,
            )
            cv.imshow("Hand", image)

    def _save_hand_angles(self, mcp_angle, pip_angle, dip_angle):
        self.angles_recorded["timestamp"].append(datetime.now().timestamp())
        self.angles_recorded["mcp angle"].append(mcp_angle)
        self.angles_recorded["pip angle"].append(pip_angle)
        self.angles_recorded["dip angle"].append(dip_angle)

    def _end_record_after_click(self):
        return cv.waitKey(1) & 0xFF == ord("p")

    def _end_record_after_time(self, timeout: datetime):
        return datetime.now() >= timeout

    def export_hand_angles_recorded_to_csv(self):
        df = pd.DataFrame(self.angles_recorded)

        root = os.path.join(Path.cwd(), "data")
        os.makedirs(root, exist_ok=True)

        timesptamp = datetime.now().timestamp()
        filename = os.path.join(root, f"angles_{timesptamp}.csv")
        df.to_csv(filename, index=False)

        print(f"Saved angles to {filename}")

    def display_hand_angles_recorded(self):
        df = pd.DataFrame(self.angles_recorded)
        print(df)

    # def _display_hud_info(self, image, ):
    #     cv.putText(image, 'mcp angle: {:.2f}deg'.format(mcp_angle), (10, 70), cv.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)
