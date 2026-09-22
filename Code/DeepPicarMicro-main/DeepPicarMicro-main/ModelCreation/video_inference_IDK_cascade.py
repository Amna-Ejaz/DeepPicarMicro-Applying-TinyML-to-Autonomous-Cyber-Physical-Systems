import tensorflow as tf
import numpy as np
import cv2
import math
import os
from collections import deque

# ============================
# CONFIGURATION
# ============================
script_dir = os.path.dirname(os.path.abspath(__file__))
VIDEO_PATH = os.path.join(script_dir, "../../Dataset/deeppicar/epoch0/out_video.avi")

MODEL_QUANT = os.path.join(script_dir, "../../../../models/quant/pilotnet-200x66x3/quant-model.tflite")
MODEL_FULL = os.path.join(script_dir, "../../../../models/full/pilotnet-200x66x3/full-model.h5")

INPUT_WIDTH = 200
INPUT_HEIGHT = 66
INPUT_CHANNELS = 3

# Thresholds for IDK
ANGLE_THRESHOLD = 15   # deg for left/right decision
IDK_MARGIN = 5         # deg zone where uncertainty is high
SMOOTHING_WINDOW = 5   # for stability checking

# ============================
# Helper functions
# ============================

def rad2deg(rad):
    return 180.0 * rad / math.pi

def classify_direction(angle_deg):
    if abs(angle_deg) < (ANGLE_THRESHOLD - IDK_MARGIN):
        return "CENTER"
    elif angle_deg > (ANGLE_THRESHOLD + IDK_MARGIN):
        return "RIGHT"
    elif angle_deg < -(ANGLE_THRESHOLD + IDK_MARGIN):
        return "LEFT"
    else:
        # In the uncertainty zone
        return "IDK"

# ============================
# Load Models
# ============================

# Quantized tiny model
interpreter = tf.lite.Interpreter(model_path=MODEL_QUANT)
interpreter.allocate_tensors()
input_idx = interpreter.get_input_details()[0]["index"]
output_idx = interpreter.get_output_details()[0]["index"]

# Full model (fallback)
full_model = tf.keras.models.load_model(MODEL_FULL)

# Store last few angle predictions
recent_angles = deque(maxlen=SMOOTHING_WINDOW)

# ============================
# VIDEO SETUP
# ============================
cap = cv2.VideoCapture(VIDEO_PATH)

# Read first frame for video writer
ret, frame = cap.read()
if not ret:
    print("ERROR: Could not read video.")
    exit()

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter("output_prediction_IDK.mp4", fourcc, 30,
                      (frame.shape[1], frame.shape[0]))

cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

# ============================
# MAIN LOOP
# ============================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Preprocess according to DeepPicar pipeline
    img = cv2.resize(frame, (320,240))
    img = cv2.flip(img, 1)
    img = img[0:210,60:190]  
    img = cv2.resize(img, (INPUT_WIDTH, INPUT_HEIGHT))
    img_norm = img.astype("float32") / 255.0
    img_expanded = np.expand_dims(img_norm, axis=0)

    # Stage 1 — Quantized model prediction
    interpreter.set_tensor(input_idx, img_expanded)
    interpreter.invoke()
    angle_rad_q = interpreter.get_tensor(output_idx)[0][0]
    angle_deg_q = rad2deg(angle_rad_q)

    # Check uncertainty
    direction_q = classify_direction(angle_deg_q)

    recent_angles.append(angle_deg_q)
    stability = max(recent_angles) - min(recent_angles)

    # STAGE 2 — Cascade fallback
    if direction_q == "IDK" or stability > 20:
        # Use the full accuracy model
        angle_rad_f = full_model.predict(img_expanded, verbose=0)[0][0]
        angle_deg_f = rad2deg(angle_rad_f)
        direction_f = classify_direction(angle_deg_f)

        final_angle = angle_deg_f
        final_dir = direction_f
        model_used = "FULL"
    else:
        final_angle = angle_deg_q
        final_dir = direction_q
        model_used = "QUANTIZED"

    # Draw overlay
    disp = frame.copy()
    cv2.putText(disp, f"Steering: {final_angle:.2f} deg", (20,40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.putText(disp, f"Direction: {final_dir}", (20,100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

    cv2.putText(disp, f"Model: {model_used}", (20,160),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)

    cv2.imshow("DeepPicar IDK + Cascaded Steering", disp)
    out.write(disp)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
