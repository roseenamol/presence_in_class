import pickle
import numpy as np
import faiss
import os

# 1. Load the augmented data
if not os.path.exists('face_data.pkl'):
    print("Error: face_data.pkl not found. Run enrollment.py first.")
    exit()

with open('face_data.pkl', 'rb') as f:
    data = pickle.load(f)

# Convert to float32 (Required by FAISS)
X = np.array(data['embeddings']).astype('float32')
labels = np.array(data['labels'])

# 2. Pre-process: Normalize embeddings
faiss.normalize_L2(X)

# 3. Build the Index
# X.shape[1] is the dimension (512 for FaceNet)
index = faiss.IndexFlatL2(X.shape[1])

# Add the normalized vectors
index.add(X)

# 4. Save the high-quality index
faiss.write_index(index, "faces.index")
with open("labels.pkl", "wb") as f:
    pickle.dump(labels, f)

print(f"Training Complete!")
print(f"Total Embeddings Indexed: {len(labels)}")
print(f"Unique Students: {len(set(labels))}")
print("FAISS Index 'faces.index' is now optimized for L2 distance.")