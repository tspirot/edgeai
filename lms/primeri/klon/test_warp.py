import cv2
import mediapipe as mp
import numpy as np
import time
import os

img_path = os.path.join(os.path.dirname(__file__), "tesla.jpg")
img = cv2.imread(img_path)
h, w = img.shape[:2]
s = min(h, w)
tesla_base = cv2.resize(img[:s, :s], (480, 480))

KEY_INDICES = [
    10, 338, 297, 332, 284, 251, 454, 323, 361, 288, 397, 152, 148, 176, 58, 132, 93, 234, 127, 54, 67, 109,
    33, 160, 158, 133, 153, 144, 362, 385, 387, 263, 373, 380,
    70, 105, 107, 336, 334, 300,
    168, 6, 1, 2,
    61, 81, 13, 311, 291, 402, 14, 178
]

mp_fm = mp.solutions.face_mesh
fm = mp_fm.FaceMesh(static_image_mode=True, max_num_faces=1)
res = fm.process(cv2.cvtColor(tesla_base, cv2.COLOR_BGR2RGB))
lms = res.multi_face_landmarks[0].landmark

base_pts = [(int(lms[i].x * 480), int(lms[i].y * 480)) for i in KEY_INDICES]
borders = [(0, 0), (240, 0), (479, 0), (0, 240), (479, 240), (0, 479), (240, 479), (479, 479)]
all_base_pts = np.array(base_pts + borders, dtype=np.int32)

rect = (0, 0, 480, 480)
subdiv = cv2.Subdiv2D(rect)
for p in all_base_pts:
    subdiv.insert((float(p[0]), float(p[1])))

triangles = subdiv.getTriangleList()
valid_triangles = []
for t in triangles:
    pt1 = (int(t[0]), int(t[1]))
    pt2 = (int(t[2]), int(t[3]))
    pt3 = (int(t[4]), int(t[5]))
    if (0 <= pt1[0] < 480 and 0 <= pt1[1] < 480 and
        0 <= pt2[0] < 480 and 0 <= pt2[1] < 480 and
        0 <= pt3[0] < 480 and 0 <= pt3[1] < 480):
        idx1 = np.where((all_base_pts == pt1).all(axis=1))[0]
        idx2 = np.where((all_base_pts == pt2).all(axis=1))[0]
        idx3 = np.where((all_base_pts == pt3).all(axis=1))[0]
        if len(idx1) > 0 and len(idx2) > 0 and len(idx3) > 0:
            valid_triangles.append((idx1[0], idx2[0], idx3[0]))

print(f"Total valid triangles: {len(valid_triangles)}")

t0 = time.time()
target_pts = all_base_pts.copy()
target_pts[KEY_INDICES.index(14)][1] += 15

out_img = tesla_base.copy()
for i1, i2, i3 in valid_triangles:
    t_src = np.float32([all_base_pts[i1], all_base_pts[i2], all_base_pts[i3]])
    t_dst = np.float32([target_pts[i1], target_pts[i2], target_pts[i3]])

    r_src = cv2.boundingRect(t_src)
    r_dst = cv2.boundingRect(t_dst)

    if r_src[2] <= 0 or r_src[3] <= 0 or r_dst[2] <= 0 or r_dst[3] <= 0:
        continue

    t_src_off = np.float32(t_src - [r_src[0], r_src[1]])
    t_dst_off = np.float32(t_dst - [r_dst[0], r_dst[1]])

    img_patch = tesla_base[r_src[1]:r_src[1]+r_src[3], r_src[0]:r_src[0]+r_src[2]]
    if img_patch.shape[0] != r_src[3] or img_patch.shape[1] != r_src[2]:
        continue

    M = cv2.getAffineTransform(t_src_off[:3], t_dst_off[:3])
    warp_patch = cv2.warpAffine(img_patch, M, (r_dst[2], r_dst[3]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)

    mask = np.zeros((r_dst[3], r_dst[2]), dtype=np.uint8)
    cv2.fillConvexPoly(mask, np.int32(t_dst_off), 255)

    sub_dst = out_img[r_dst[1]:r_dst[1]+r_dst[3], r_dst[0]:r_dst[0]+r_dst[2]]
    if sub_dst.shape[:2] == warp_patch.shape[:2]:
        sub_dst[mask == 255] = warp_patch[mask == 255]

dt = (time.time() - t0) * 1000
print(f"BENCHMARK: Single warp completed in: {dt:.2f} ms")
