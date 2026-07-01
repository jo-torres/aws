import cv2

print("Abriendo cámara...")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("❌ No se pudo abrir la cámara")
    exit()

print("✅ Cámara abierta")

while True:
    ret, frame = cap.read()

    if not ret:
        print("No se pudo leer un frame")
        break

    cv2.imshow("Mi Camara", frame)

    tecla = cv2.waitKey(1)

    if tecla == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()