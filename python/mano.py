import cv2
import mediapipe as mp

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

mp_draw = mp.solutions.drawing_utils

while True:
    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    resultado = hands.process(rgb)

    if resultado.multi_hand_landmarks:

        for mano in resultado.multi_hand_landmarks:

            mp_draw.draw_landmarks(
                frame,
                mano,
                mp_hands.HAND_CONNECTIONS
            )

    cv2.imshow("Detector de manos", frame)

    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()