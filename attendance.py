import cv2
import pickle
import torch
import numpy as np
import faiss
from datetime import datetime
from ultralytics import YOLO
from facenet_pytorch import InceptionResnetV1
from torchvision import transforms

# --- 1. Load Models & FAISS ---
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

yolo_model = YOLO('yolov8x-face.pt') 
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

index = faiss.read_index("faces.index")
with open("labels.pkl", "rb") as f:
    known_labels = pickle.load(f)

preprocess = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((160, 160)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

marked_attendance = set()
track_confirmation = {} 
confirmed_tracks = {} 

# --- 2. Processing Loop ---
cap = cv2.VideoCapture('row.mp4')

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    # Keep tracking persistent
    results = yolo_model.track(frame, persist=True, verbose=False, conf=0.25)

    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        track_ids = results[0].boxes.id.cpu().numpy()

        for box, track_id in zip(boxes, track_ids):
            track_id = int(track_id)
            x1, y1, x2, y2 = map(int, box[:4])
            
            # OPTIMIZATION 2: If this track ID is already confirmed, skip FaceNet!
            if track_id in confirmed_tracks:
                predicted_name = confirmed_tracks[track_id]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"CONFIRMED: {predicted_name}", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                continue # Skip the rest of the loop for this face

            face_crop = frame[max(0,y1):y2, max(0,x1):x2]
            if face_crop.size == 0: continue

            # Generate and Normalize Embedding (Only runs for UNCONFIRMED faces)
            face_tensor = preprocess(face_crop).unsqueeze(0).to(device)
            with torch.no_grad():
                emb = resnet(face_tensor).cpu().numpy().astype('float32')
            
            emb /= np.linalg.norm(emb)

            # FAISS L2 Search
            distances, indices = index.search(emb, k=1)
            dist = distances[0][0]
            predicted_name = known_labels[indices[0][0]]

            # --- 3. THRESHOLD LOGIC ---
            if dist < 0.50: 
                if track_id not in track_confirmation:
                    track_confirmation[track_id] = 0
                track_confirmation[track_id] += 1
                
                if track_confirmation[track_id] >= 10:
                    label_text = f"CONFIRMED: {predicted_name}"
                    color = (0, 255, 0)
                    
                    # Store as confirmed so we never run FaceNet on this ID again
                    confirmed_tracks[track_id] = predicted_name 
                    
                    if predicted_name not in marked_attendance:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] PRESENT: {predicted_name}")
                        marked_attendance.add(predicted_name)
                else:
                    label_text = f"Verifying {predicted_name}..."
                    color = (255, 255, 0) 
            else:
                label_text = f"Unknown (Dist:{dist:.2f})"
                color = (0, 0, 255) 

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.imshow('Better L2 Attendance System', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()