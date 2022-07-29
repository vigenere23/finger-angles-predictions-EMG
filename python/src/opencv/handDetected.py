import cv2 as cv
import mediapipe as mp
import numpy as np


class HandDetection:
    def __init__(self) -> None:
        mpHands = mp.solutions.hands
        self.model_hands = mpHands.Hands()
        self.landmark_hand_detected = []

    def detect_finger(self, image, hand_side, finger):
        imgRGB = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        hand_get = self.model_hands.process(imgRGB)
        if hand_get.multi_handedness != None:
            hand_label = hand_get.multi_handedness[0].classification[0].label
            if hand_label == hand_side:
                self.landmark_hand_detected = hand_get.multi_hand_landmarks[0].landmark
                if self.landmark_hand_detected:
                    h, w, c = image.shape
                    finger_points_scaled = self.get_finger_points_img(finger, w, h)
                    self.__mark_finger(image, finger_points_scaled, finger["color"])

    """ def detect_multi_finger(self, image, hand_side, fingers):
        imgRGB = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        hand_get = self.model_hands.process(imgRGB)
        if hand_get.multi_handedness != None:
            hand_label = hand_get.multi_handedness[0].classification[0].label
            if  hand_label == hand_side:
                self.landmark_hand_detected = hand_get.multi_hand_landmarks[0].landmark
                if (self.landmark_hand_detected):
                    h, w, c = image.shape
                    for finger in fingers:
                        finger_points_scaled = self.get_finger_points(finger, w, h)
                        self.__mark_finger(image, finger_points_scaled, finger['color']) """

    def get_finger_points_img(self, finger, width, height):
        finger_points = []
        for id, landmark in enumerate(self.landmark_hand_detected):
            if id in finger["points"]:
                finger_points.append((landmark.x * width, landmark.y * height))
        return finger_points

    def __mark_finger(self, image, points, color):
        for x, y in points:
            cv.circle(image, (int(x), int(y)), 5, color, cv.FILLED)

    def __calcul_angle(self, u_vector, v_vector):
        rad_angle = 0
        if len(u_vector) > 0 and len(v_vector):
            v1 = u_vector / np.linalg.norm(u_vector)
            v2 = v_vector / np.linalg.norm(v_vector)
            cos_alpha = v1.dot(v2)
            rad_angle = np.arccos(cos_alpha)
        return np.rad2deg(rad_angle)

    def __define_vector(self, finger_point_A, finger_point_B):
        point_A, point_B, vector = [], [], []
        if len(self.landmark_hand_detected) > 0:
            point_A = np.array(
                [
                    self.landmark_hand_detected[finger_point_A].x,
                    self.landmark_hand_detected[finger_point_A].y,
                ]
            )
            point_B = np.array(
                [
                    self.landmark_hand_detected[finger_point_B].x,
                    self.landmark_hand_detected[finger_point_B].y,
                ]
            )
            vector = point_B - point_A
        return vector

    def get_angles_in_finger(self, finger):
        mcp_angle, pip_angle, dip_angle = 0, 0, 0
        points = finger["points"]
        if len(finger["points"]) == 5:
            # change the points to vector e.g.: AB <=> <B, A>
            u_vector = self.__define_vector(points[0], points[1])
            v_vector = self.__define_vector(points[1], points[2])
            e_vector = self.__define_vector(points[2], points[3])
            h_vector = self.__define_vector(points[3], points[4])
            mcp_angle = self.__calcul_angle(u_vector, v_vector)
            pip_angle = self.__calcul_angle(v_vector, e_vector)
            dip_angle = self.__calcul_angle(e_vector, h_vector)

        return (mcp_angle, pip_angle, dip_angle)

    # def get_angles_finger(self, finger):
    #     pipj_angle, dipj_angle = 0, 0
    #     points = finger.points
    #     if len(finger) == 5:
    #         # change the points to vector e.g.: AB <=> <B, A>
    #         u_vector = self.__define_vector(points[2], points[1])
    #         v_vector = self.__define_vector(points[2], points[3])
    #         e_vector = self.__define_vector(points[3], points[2])
    #         h_vector = self.__define_vector(points[3], points[4])
    #         pipj_angle = self.__calcul_angle(u_vector, v_vector)
    #         dipj_angle = self.__calcul_angle(e_vector, h_vector)

    #     return (pipj_angle, dipj_angle)
