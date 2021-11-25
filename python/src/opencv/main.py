import numpy as np
import cv2 as cv
from finger import INDEX_FINGER
from record import HandRecorder

handRecorder = HandRecorder('Right', INDEX_FINGER)
# p to stop record
handRecorder.start_record_hand()
# record during (seconde) ans stop
# handRecorder.start_record_hand_during(60)
handRecorder.display_hand_angles_recorded()
handRecorder.export_hand_angles_recorded_to_csv()