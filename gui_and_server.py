# -*- coding: utf-8 -*-
"""GUI_and_server.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zyN2cIyr_gY18qU_VzkeUIygiLvIjMXk
"""

! wget "https://pjreddie.com/media/files/yolov3.weights"

import cv2
import tkinter as tk
from PIL import Image, ImageTk

# Load pre-trained YOLOv3 model
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Setting up GUI
window = tk.Tk()
window.title("Gun and Knife Detection")
canvas = tk.Canvas(window, width=800, height=600)
canvas.pack()

# Open video capture
cap = cv2.VideoCapture(0)

def detect_objects():
    ret, frame = cap.read()
    if ret:
        # Perform object detection
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        outs = net.forward(output_layers)

        # Process detection results
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5 and class_id in [0, 1]:  # Filter for gun and knife classes
                    # Calculate bounding box coordinates
                    center_x = int(detection[0] * frame.shape[1])
                    center_y = int(detection[1] * frame.shape[0])
                    width = int(detection[2] * frame.shape[1])
                    height = int(detection[3] * frame.shape[0])
                    x = int(center_x - width / 2)
                    y = int(center_y - height / 2)
                    
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, width, height])

        # Apply non-maximum suppression to remove overlapping boxes
        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        # Draw bounding boxes and labels on the frame
        for i in indices:
            i = i[0]
            x, y, width, height = boxes[i]
            label = classes[class_ids[i]]
            cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Convert frame to ImageTk format and display in GUI
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img_tk = ImageTk.PhotoImage(image=img)
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        canvas.img_tk = img_tk

    window.after(10, detect_objects)  # Repeat the detection process every 10ms

# Start the object detection process
detect_objects()
window.mainloop()


cap.release()
cv2.destroyAllWindows()