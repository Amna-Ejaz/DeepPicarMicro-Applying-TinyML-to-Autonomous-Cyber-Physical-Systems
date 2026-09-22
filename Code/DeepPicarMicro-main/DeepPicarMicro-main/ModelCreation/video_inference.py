import tensorflow as tf
import numpy as np
import cv2
import math
import os

# ------------------------------
# CONFIGURATIONS
# ------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
VIDEO_PATH = os.path.join(script_dir, "../../Dataset/deeppicar/epoch0/out_video.avi")  # <-- change if needed
MODEL_PATH = os.path.join(script_dir, "../../../../models/quant/pilotnet-200x66x3/quant-model.tflite")

INPUT_WIDTH = 200
INPUT_HEIGHT = 66
INPUT_CHANNELS = 3

# ------------------------------
# Load TFLite Quantized Model
# ------------------------------
interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_index = interpreter.get_input_details()[0]["index"]
output_index = interpreter.get_output_details()[0]["index"]

# Helper to convert angle → left/center/right
def rad2deg(rad):
    return 180.0 * rad / math.pi

def get_action(angle_rad):
    degree = rad2deg(angle_rad)
    if -15 < degree < 15:
        return "CENTER"
    elif degree >= 15:
        return "RIGHT"
    else:
        return "LEFT"

# ------------------------------
# Process Video
# ------------------------------
cap = cv2.VideoCapture(VIDEO_PATH)

# Read first frame to get size
ret, frame = cap.read()
if not ret:
    print("Could not read video.")
    exit()

# Create video writer
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter("output_prediction.mp4", fourcc, 30, (frame.shape[1], frame.shape[0]))

cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # restart video from beginning

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # your resize/crop/preprocess steps here…
    img = cv2.resize(frame, (320,240))
    img = cv2.flip(img, 1)
    img = img[0:210,60:190]
    img = cv2.resize(img, (INPUT_WIDTH, INPUT_HEIGHT))
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)

    interpreter.set_tensor(input_index, img)
    interpreter.invoke()

    angle = interpreter.get_tensor(output_index)[0][0]
    action = get_action(angle)

    # Draw text on original frame
    disp = frame.copy()
    cv2.putText(disp, f"Angle: {rad2deg(angle):.2f} deg", (20,40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv2.putText(disp, f"Direction: {action}", (20,100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

    # Show on screen
    cv2.imshow("DeepPicar Steering Prediction", disp)

    # Save frame to output video
    out.write(disp)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
