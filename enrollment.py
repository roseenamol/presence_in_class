import cv2
import os
import pickle
import torch
import numpy as np
from ultralytics import YOLO
from facenet_pytorch import InceptionResnetV1
from torchvision import transforms
from PIL import Image, ImageEnhance

# --- 1. Setup ---
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
yolo_model = YOLO('yolov8x-face.pt')
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

base_preprocess = transforms.Compose([
    transforms.Resize((160, 160)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

dataset_path = 'student_videos'
embeddings = []
labels = []

def augment_image(pil_img):
    """Generates 4 variations of a single face crop."""
    aug_list = []
    # 1. Original
    aug_list.append(pil_img)
    # 2. Horizontal Flip
    aug_list.append(pil_img.transpose(Image.FLIP_LEFT_RIGHT))
    # 3. Brightness Increase
    aug_list.append(ImageEnhance.Brightness(pil_img).enhance(1.3))
    # 4. Brightness Decrease
    aug_list.append(ImageEnhance.Brightness(pil_img).enhance(0.7))
    return aug_list

# --- 2. Processing with Augmentation ---
for student_name in os.listdir(dataset_path):
    student_dir = os.path.join(dataset_path, student_name)
    if not os.path.isdir(student_dir): continue
    
    print(f"Processing {student_name}...")
    
    for video_name in os.listdir(student_dir):
        cap = cv2.VideoCapture(os.path.join(student_dir, video_name))
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            # Extract face every 5 frames for variety
            if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % 5 == 0:
                results = yolo_model(frame, verbose=False)
                for result in results:
                    for box in result.boxes.xyxy.cpu().numpy():
                        x1, y1, x2, y2 = map(int, box[:4])
                        face_crop = frame[max(0,y1):y2, max(0,x1):x2]
                        if face_crop.size == 0: continue
                        
                        # Convert to PIL for easy augmentation
                        pil_face = Image.fromarray(cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB))
                        
                        # Apply Augmentations
                        for augmented_face in augment_image(pil_face):
                            tensor = base_preprocess(augmented_face).unsqueeze(0).to(device)
                            with torch.no_grad():
                                emb = resnet(tensor).cpu().numpy().flatten()
                            
                            # Normalize for FAISS L2 consistency
                            emb = emb / np.linalg.norm(emb) 
                            embeddings.append(emb)
                            labels.append(student_name)
        cap.release()
    print(f" Successfully Augmented & Enrolled: {student_name}")

# --- 3. Save Data ---
with open('face_data.pkl', 'wb') as f:
    pickle.dump({'embeddings': embeddings, 'labels': labels}, f)