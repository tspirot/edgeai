import os
import time
import math
import random
from collections import deque
import cv2
import numpy as np

# Postavljanje prikaza na lokalni HDMI ekran (TV) kada se pokrece preko SSH
os.environ["DISPLAY"] = ":0"
os.environ["WAYLAND_DISPLAY"] = "wayland-0"

# Provera MediaPipe biblioteke
try:
    import mediapipe as mp
except ImportError:
    print("\n[GRESKA] 'mediapipe' nije instaliran!")
    print("Pokreni: pip install mediapipe==0.10.14\n")
    exit(1)

# Inicijalizacija MediaPipe Pose (za celo telo)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Inicijalizacija MediaPipe Face Mesh (za detaljne crte lica i emocije)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# Inicijalizacija MediaPipe Hands (za pracenje saka i prstiju)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Inicijalizacija kamere (Picamera2 za RPi 5 sa fallback-om na OpenCV)
use_picam2 = False
picam2 = None
cap = None

try:
    from picamera2 import Picamera2
    print("[INFO] Pokrecem kameru preko nativnog Picamera2 drajvera (IMX708)...")
    picam2 = Picamera2()
    # RGB888 konfiguracija daje tačan BGR raspored u OpenCV memoriji
    config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
    picam2.configure(config)
    picam2.start()
    use_picam2 = True
    print("[INFO] Picamera2 uspešno pokrenuta sa prirodnim bojama!")
except Exception as e:
    print(f"[INFO] Picamera2 nije ucitana ({e}), pokusavam OpenCV VideoCapture...")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not use_picam2 and (cap is None or not cap.isOpened()):
    print("[GRESKA] Kamera nije pronadjena! Pokreni skriptu sa: libcamerify python klon.py")
    exit(1)

# Konekcije za celo telo
FULL_BODY_CONNECTIONS = [
    (11, 12), (11, 23), (12, 24), (23, 24),
    (11, 13), (13, 15), (12, 14), (14, 16),
    (15, 17), (15, 19), (15, 21), (16, 18), (16, 20), (16, 22),
    (23, 25), (25, 27), (27, 29), (27, 31),
    (24, 26), (26, 28), (28, 30), (28, 32),
    (0, 11), (0, 12)
]

# Konekcije za prste na sakama
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20),
    (5, 9), (9, 13), (13, 17)
]

# Kljucne konture lica
FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_EYEBROW = [336, 296, 334, 293, 300, 276, 283, 282, 295, 285]
RIGHT_EYEBROW = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]
# Precizne konture gornje i donje usne
UPPER_LIP_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]
UPPER_LIP_INNER = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]
LOWER_LIP_INNER = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]
LOWER_LIP_OUTER = [291, 375, 321, 405, 314, 17, 84, 181, 91, 146, 61]
MOUTH_OPENING_LOOP = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
FULL_LIPS_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]
NOSE_BRIDGE = [168, 6, 197, 195, 5, 4, 1, 19, 94, 2]

# Bogata, diskretna konstelacija linija preko celog lica (kao na slici)
DISCRETE_FACE_MESH = [
    (10, 67), (10, 297), (67, 109), (297, 338), (109, 10), (338, 10),
    (67, 105), (105, 66), (66, 107), (107, 168), (168, 336), (336, 296), (296, 334), (334, 297),
    (10, 151), (151, 9), (9, 8), (8, 168),
    (168, 6), (6, 197), (197, 195), (195, 5), (5, 4), (4, 1),
    (105, 159), (107, 158), (336, 385), (334, 386),
    (168, 158), (168, 385), (6, 133), (6, 362),
    (133, 116), (116, 123), (123, 147), (147, 213), (213, 192), (192, 214), (214, 210), (210, 211), (211, 32),
    (362, 345), (345, 352), (352, 376), (376, 433), (433, 416), (416, 434), (434, 430), (430, 431), (431, 262),
    (234, 127), (127, 93), (93, 132), (132, 58), (58, 172), (172, 136), (136, 150), (150, 149), (149, 176), (176, 148), (148, 152),
    (454, 356), (356, 323), (323, 361), (361, 288), (288, 397), (397, 365), (365, 379), (379, 378), (378, 400), (400, 377), (377, 152),
    (2, 0), (2, 37), (2, 267), (17, 152), (84, 152), (314, 152),
    (1, 2), (2, 94), (94, 19), (19, 164), (164, 0),
    (234, 105), (454, 334), (234, 1), (454, 1), (234, 152), (454, 152),
    (116, 1), (345, 1), (123, 61), (352, 291), (147, 152), (376, 152)
]

GLOWING_NODES = [
    10, 151, 9, 168, 6, 197, 4, 1, 2, 0, 152,
    67, 109, 297, 338, 105, 107, 336, 334,
    133, 159, 145, 362, 386, 374,
    234, 127, 93, 58, 172, 454, 356, 323, 288, 397,
    116, 123, 147, 345, 352, 376,
    61, 291, 0, 13, 14, 17, 37, 267, 84, 314
]

# ================= UCITAVANJE SLIKE NIKOLE TESLE =================
script_dir = os.path.dirname(os.path.abspath(__file__))
tesla_file = os.path.join(script_dir, "tesla.jpg")

tesla_loaded = False
tesla_base_img = None
tesla_base_pts = None
tesla_triangles = []
WARP_KEY_INDICES = [
    10, 338, 297, 332, 284, 251, 454, 323, 361, 288, 397, 152, 148, 176, 58, 132, 93, 234, 127, 54, 67, 109,
    33, 160, 159, 158, 133, 153, 145, 144, 362, 385, 386, 387, 263, 373, 374, 380,
    70, 105, 107, 336, 334, 300,
    168, 6, 1, 2,
    61, 81, 13, 311, 291, 402, 14, 178, 0, 17
]
WARP_IDX_MAP = {idx: i for i, idx in enumerate(WARP_KEY_INDICES)}

def offset_tesla_pt(target_arr, landmark_idx, dx=0, dy=0):
    if landmark_idx in WARP_IDX_MAP:
        pos = WARP_IDX_MAP[landmark_idx]
        target_arr[pos][0] += dx
        target_arr[pos][1] += dy

if os.path.exists(tesla_file):
    raw_tesla = cv2.imread(tesla_file)
    if raw_tesla is not None:
        th, tw = raw_tesla.shape[:2]
        ts = min(th, tw)
        crop_t = raw_tesla[:ts, :ts]
        tesla_base_img = cv2.resize(crop_t, (480, 480))

        # Detekcija baznih tacaka Tesle
        fm_static = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1)
        res_t = fm_static.process(cv2.cvtColor(tesla_base_img, cv2.COLOR_BGR2RGB))
        if res_t.multi_face_landmarks:
            tlms = res_t.multi_face_landmarks[0].landmark
            base_pts_list = [(int(tlms[i].x * 480), int(tlms[i].y * 480)) for i in WARP_KEY_INDICES]
            borders = [(0, 0), (240, 0), (479, 0), (0, 240), (479, 240), (0, 479), (240, 479), (479, 479)]
            all_pts_arr = np.array(base_pts_list + borders, dtype=np.int32)
            tesla_base_pts = all_pts_arr

            # Delaunay triangulacija
            subdiv = cv2.Subdiv2D((0, 0, 480, 480))
            for p in all_pts_arr:
                subdiv.insert((float(p[0]), float(p[1])))

            for t in subdiv.getTriangleList():
                pt1 = (int(t[0]), int(t[1]))
                pt2 = (int(t[2]), int(t[3]))
                pt3 = (int(t[4]), int(t[5]))
                if (0 <= pt1[0] < 480 and 0 <= pt1[1] < 480 and
                    0 <= pt2[0] < 480 and 0 <= pt2[1] < 480 and
                    0 <= pt3[0] < 480 and 0 <= pt3[1] < 480):
                    idx1 = np.where((all_pts_arr == pt1).all(axis=1))[0]
                    idx2 = np.where((all_pts_arr == pt2).all(axis=1))[0]
                    idx3 = np.where((all_pts_arr == pt3).all(axis=1))[0]
                    if len(idx1) > 0 and len(idx2) > 0 and len(idx3) > 0:
                        tesla_triangles.append((idx1[0], idx2[0], idx3[0]))

            tesla_loaded = True
            print("[INFO] Slika Nikole Tesle uspesno ucitana i kalibrisana za animaciju!")

def warp_tesla_face(target_pts):
    """Real-time deformacija i animacija fotografije Nikole Tesle"""
    if not tesla_loaded or tesla_base_img is None:
        return np.zeros((480, 480, 3), dtype=np.uint8)

    out = tesla_base_img.copy()
    for i1, i2, i3 in tesla_triangles:
        t_src = np.float32([tesla_base_pts[i1], tesla_base_pts[i2], tesla_base_pts[i3]])
        t_dst = np.float32([target_pts[i1], target_pts[i2], target_pts[i3]])

        r_src = cv2.boundingRect(t_src)
        r_dst = cv2.boundingRect(t_dst)
        if r_src[2] <= 0 or r_src[3] <= 0 or r_dst[2] <= 0 or r_dst[3] <= 0:
            continue

        t_src_off = np.float32(t_src - [r_src[0], r_src[1]])
        t_dst_off = np.float32(t_dst - [r_dst[0], r_dst[1]])

        img_patch = tesla_base_img[r_src[1]:r_src[1]+r_src[3], r_src[0]:r_src[0]+r_src[2]]
        if img_patch.shape[0] != r_src[3] or img_patch.shape[1] != r_src[2]:
            continue

        M = cv2.getAffineTransform(t_src_off[:3], t_dst_off[:3])
        warp_patch = cv2.warpAffine(img_patch, M, (r_dst[2], r_dst[3]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)

        mask = np.zeros((r_dst[3], r_dst[2]), dtype=np.uint8)
        cv2.fillConvexPoly(mask, np.int32(t_dst_off), 255)

        sub_dst = out[r_dst[1]:r_dst[1]+r_dst[3], r_dst[0]:r_dst[0]+r_dst[2]]
        if sub_dst.shape[:2] == warp_patch.shape[:2]:
            sub_dst[mask == 255] = warp_patch[mask == 255]
    return out

def analyze_emotions(pts):
    """Prepoznaje emocije i promene na licu na osnovu precizne geometrije"""
    lip_left = pts[61]
    lip_right = pts[291]
    lip_top_inner = pts[13]
    lip_bot_inner = pts[14]
    lip_top_outer = pts[0]
    lip_bot_outer = pts[17]

    eye_dist = max(20.0, math.hypot(pts[263][0] - pts[33][0], pts[263][1] - pts[33][1]))
    mouth_width = math.hypot(lip_left[0] - lip_right[0], lip_left[1] - lip_right[1])
    
    # Vertikalni otvor izmedju gornje i donje usne
    mouth_height = math.hypot(lip_top_inner[0] - lip_bot_inner[0], lip_top_inner[1] - lip_bot_inner[1])
    mar = mouth_height / max(1.0, mouth_width)
    mouth_open_pct = int(np.clip((mar - 0.07) / 0.32 * 100, 0, 100))

    # Proracun pravog osmeha:
    # 1. Uglovi usana (61, 291) se dizu prema nosu i gornjoj usni
    corners_y = (lip_left[1] + lip_right[1]) / 2.0
    corner_elevation = (lip_top_outer[1] - corners_y) / max(1.0, eye_dist)
    
    # 2. Usta se sire u odnosu na razmak ociju
    width_ratio = mouth_width / max(1.0, eye_dist)

    # Pravi osmeh podize uglove i siri usta
    smile_score = (width_ratio - 0.49) * 2.0 + (corner_elevation + 0.04) * 2.2
    
    # KLJUCNO: Ako su usta samo otvorena naniže (pad vilice / govor / iznenadjenje),
    # a nisu razvucena u sirinu, to NIJE osmeh vec govor ili zevanje!
    if mar > 0.15 and width_ratio < 0.57:
        smile_score -= (mar - 0.15) * 2.6

    smile_pct = int(np.clip(smile_score * 100, 0, 100))

    # Obrve
    brow_dist_l = pts[159][1] - pts[105][1]
    brow_dist_r = pts[386][1] - pts[334][1]
    brow_norm = ((brow_dist_l + brow_dist_r) / 2.0) / max(1.0, mouth_width)
    brow_pct = int(np.clip((brow_norm - 0.28) / 0.16 * 100, 0, 100))

    inner_brow_dist = math.hypot(pts[55][0] - pts[285][0], pts[55][1] - pts[285][1])
    furrow_norm = inner_brow_dist / max(1.0, mouth_width)

    # Oci
    ear_l = math.hypot(pts[386][0] - pts[374][0], pts[386][1] - pts[374][1]) / max(1.0, math.hypot(pts[362][0] - pts[263][0], pts[362][1] - pts[263][1]))
    ear_r = math.hypot(pts[159][0] - pts[145][0], pts[159][1] - pts[145][1]) / max(1.0, math.hypot(pts[33][0] - pts[133][0], pts[33][1] - pts[133][1]))
    eye_pct = int(np.clip(((ear_l + ear_r)/2.0 - 0.15) / 0.17 * 100, 0, 100))

    # Odredjivanje emocije po prioritetu
    if mouth_open_pct > 25 and brow_pct > 55 and eye_pct > 40:
        emotion = "IZNENADJEN / ODUSEVLJEN"
        conf = min(99, 60 + mouth_open_pct // 2)
        color = (0, 220, 255)
    elif smile_pct > 35:
        emotion = "SRECAN / OSMEH"
        conf = min(99, 55 + smile_pct // 2)
        color = (0, 255, 180)
    elif mouth_open_pct > 20:
        emotion = "GOVOR / OTVORENA USTA"
        conf = min(99, 50 + mouth_open_pct // 2)
        color = (0, 240, 255)
    elif furrow_norm < 0.29 and eye_pct < 65:
        emotion = "LJUT / ZAMISLJEN"
        conf = 82
        color = (0, 70, 255)
    elif corner_elevation < -0.09:
        emotion = "TUZAN / ZABRINUT"
        conf = 78
        color = (255, 120, 120)
    elif eye_pct < 15:
        emotion = "ZAZMUREN / SPAVA"
        conf = 95
        color = (180, 180, 180)
    else:
        emotion = "SMIREN / NEUTRALAN"
        conf = 88
        color = (255, 255, 255)

    return emotion, conf, color, smile_pct, mouth_open_pct, brow_pct, eye_pct

# ------------------------------------------------------------------------------
# DIGITALNA MATRIX KISA (MATRIX DIGITAL RAIN)
# ------------------------------------------------------------------------------
class MatrixRain:
    def __init__(self, width=480, height=480, col_width=16):
        self.w = width
        self.h = height
        self.col_w = col_width
        self.num_cols = width // col_width
        self.chars = "0123456789ABCDEFｦｱｳｴｵｶｷｹｺｻｼｽｾｿﾀﾂﾃﾅﾆﾇﾈﾊﾋﾎﾏﾐﾑﾒﾓﾔﾕﾗﾘﾜ"
        self.drops = [random.randint(-50, 0) for _ in range(self.num_cols)]
        self.speeds = [random.randint(2, 4) for _ in range(self.num_cols)]
        self.lens = [random.randint(8, 20) for _ in range(self.num_cols)]

    def update_and_draw(self, canvas):
        overlay = np.zeros_like(canvas)
        for i in range(self.num_cols):
            x = i * self.col_w + 3
            head_y = self.drops[i]
            length = self.lens[i]

            for j in range(length):
                char_y = head_y - j * 15
                if 0 <= char_y < self.h - 10:
                    char = random.choice(self.chars)
                    if j == 0:
                        col = (200, 255, 220)  # Svetlozelena/bela glava
                    elif j < 3:
                        col = (0, 255, 100)    # Jarka Matrix neon zelena
                    else:
                        col = (0, 75, 30)      # Tamniji zeleni rep

                    cv2.putText(overlay, char, (x, char_y),
                                cv2.FONT_HERSHEY_PLAIN, 0.85, col, 1, cv2.LINE_AA)

            self.drops[i] += self.speeds[i]
            if self.drops[i] - length * 15 > self.h:
                self.drops[i] = random.randint(-40, 0)
                self.speeds[i] = random.randint(2, 4)
                self.lens[i] = random.randint(8, 20)

        cv2.add(canvas, overlay, canvas)

matrix_rain = MatrixRain(width=480, height=480, col_width=16)
scanline_y = 0

# Mod modela na desnoj strani: MATRIX_KLON (podrazumevano) vs CYBER_AVATAR vs FOTO_TESLA
MODEL_MODES = ["MATRIX_KLON", "CYBER_AVATAR", "FOTO_TESLA"]
current_model_idx = 0

print("=" * 65)
print("PROJEKAT KLON (MATRIX KLON, CYBER AVATAR & NIKOLA TESLA)")
print("1. CELO TELO (daleko): Prikazuje kompletnog 3D avatara sa telom")
print("2. LICE I RUKE (blizu): Prati lice, prste i prepoznaje osecanja")
print("Kontrole:")
print("  [s] - Prebaci model: Matrix Klon <-> Cyber Avatar <-> Nikola Tesla")
print("  [q] - Izlaz")
print("=" * 65)

prev_time = 0
mode_history = deque(["LICE_I_RUKE"] * 5, maxlen=5)
current_mode = "LICE_I_RUKE"

while True:
    if use_picam2:
        raw_frame = picam2.capture_array()
        raw_frame = cv2.flip(raw_frame, 1)
        frame = raw_frame
    else:
        success, raw_frame = cap.read()
        if not success:
            break
        frame = cv2.flip(raw_frame, 1)

    h_cam, w_cam, _ = frame.shape
    crop_x = (w_cam - 480) // 2
    left_img = frame[:, crop_x:crop_x + 480].copy()

    active_model_mode = MODEL_MODES[current_model_idx]

    if active_model_mode == "MATRIX_KLON":
        accent_col = (0, 255, 100)      # Neon Matrix zelena
        glow_col = (0, 180, 70)         # Srednje zelena
        white_col = (220, 255, 230)     # Beličasto zelena
        joint_col = (50, 255, 150)      # Svetlo zelena
    else:
        accent_col = (255, 215, 0)      # Zlatno-zuta za Cyber Avatar
        glow_col = (255, 190, 50)
        white_col = (255, 255, 255)
        joint_col = (0, 255, 255)

    right_img = np.zeros((480, 480, 3), dtype=np.uint8)
    if active_model_mode == "MATRIX_KLON":
        right_img[:, :] = (8, 14, 10)
        matrix_rain.update_and_draw(right_img)
    else:
        right_img[:, :] = (16, 14, 12)
        cv2.circle(right_img, (240, 240), 210, (26, 22, 18), 1)
        cv2.circle(right_img, (240, 240), 140, (30, 26, 20), 1)

    rgb_frame = cv2.cvtColor(left_img, cv2.COLOR_BGR2RGB)
    pose_results = pose.process(rgb_frame)

    person_detected = False
    target_mode = "LICE_I_RUKE"

    if pose_results.pose_landmarks:
        person_detected = True
        p_lms = pose_results.pose_landmarks.landmark

        ankles_visible = (p_lms[27].visibility > 0.4 and p_lms[28].visibility > 0.4 and p_lms[27].y < 0.97 and p_lms[28].y < 0.97)
        knees_visible = (p_lms[25].visibility > 0.5 and p_lms[26].visibility > 0.5 and p_lms[25].y < 0.95)
        sh_mid_y = (p_lms[11].y + p_lms[12].y) / 2.0
        head_h = abs(sh_mid_y - p_lms[0].y)

        if ankles_visible and knees_visible and head_h < 0.17:
            target_mode = "CELO_TELO"
        else:
            target_mode = "LICE_I_RUKE"

        mode_history.append(target_mode)
        if mode_history.count(target_mode) >= 3:
            current_mode = target_mode

    # ================= REZIM 1: CELO TELO (DALEKO) =================
    if current_mode == "CELO_TELO" and person_detected:
        p_lms = pose_results.pose_landmarks.landmark
        pts_left_pose = [(int(lm.x * 480), int(lm.y * 480)) for lm in p_lms]

        for i1, i2 in FULL_BODY_CONNECTIONS:
            if p_lms[i1].visibility > 0.35 and p_lms[i2].visibility > 0.35:
                cv2.line(left_img, pts_left_pose[i1], pts_left_pose[i2], glow_col, 2)

        for j_idx in range(11, 33):
            if p_lms[j_idx].visibility > 0.35:
                cv2.circle(left_img, pts_left_pose[j_idx], 4, joint_col, -1)
                cv2.circle(left_img, pts_left_pose[j_idx], 6, accent_col, 1)

        center_x = (pts_left_pose[23][0] + pts_left_pose[24][0]) // 2
        center_y = (pts_left_pose[11][1] + pts_left_pose[27][1]) // 2 if p_lms[27].visibility > 0.3 else 240
        body_h = max(60, abs(pts_left_pose[27][1] - pts_left_pose[0][1])) if p_lms[27].visibility > 0.3 else 320
        scale = 370.0 / float(body_h)

        pts_right_pose = []
        for p in pts_left_pose:
            rx = 240 + int((p[0] - center_x) * scale)
            ry = 240 + int((p[1] - center_y) * scale)
            pts_right_pose.append((rx, ry))

        # Strukturisana cyber kaciga i glava
        head_cx, head_cy = pts_right_pose[0]
        helmet_w, helmet_h = int(22 * scale), int(28 * scale)
        helmet_pts = np.array([
            (head_cx, head_cy - helmet_h),
            (head_cx + helmet_w, head_cy - int(helmet_h * 0.6)),
            (head_cx + int(helmet_w * 0.85), head_cy + int(helmet_h * 0.4)),
            (head_cx + int(helmet_w * 0.5), head_cy + helmet_h),
            (head_cx - int(helmet_w * 0.5), head_cy + helmet_h),
            (head_cx - int(helmet_w * 0.85), head_cy + int(helmet_h * 0.4)),
            (head_cx - helmet_w, head_cy - int(helmet_h * 0.6))
        ], dtype=np.int32)
        cv2.polylines(right_img, [helmet_pts], True, accent_col, 2)

        visor_y = head_cy - int(helmet_h * 0.15)
        cv2.line(right_img, (head_cx - int(helmet_w * 0.65), visor_y), (head_cx + int(helmet_w * 0.65), visor_y), white_col, 2)
        cv2.circle(right_img, (head_cx - int(helmet_w * 0.3), visor_y), 3, (0, 255, 255), -1)
        cv2.circle(right_img, (head_cx + int(helmet_w * 0.3), visor_y), 3, (0, 255, 255), -1)

        cv2.line(right_img, (head_cx - 6, head_cy + helmet_h), pts_right_pose[11], glow_col, 1)
        cv2.line(right_img, (head_cx + 6, head_cy + helmet_h), pts_right_pose[12], glow_col, 1)

        for i1, i2 in FULL_BODY_CONNECTIONS:
            if p_lms[i1].visibility > 0.35 and p_lms[i2].visibility > 0.35:
                cv2.line(right_img, pts_right_pose[i1], pts_right_pose[i2], accent_col, 3)
                cv2.line(right_img, pts_right_pose[i1], pts_right_pose[i2], white_col, 1)

        for j_idx in range(11, 33):
            if p_lms[j_idx].visibility > 0.35:
                pt = pts_right_pose[j_idx]
                cv2.circle(right_img, pt, 5, joint_col, -1)
                cv2.circle(right_img, pt, 8, accent_col, 1)

        cv2.ellipse(right_img, (240, 445), (130, 18), 0, 0, 360, (40, 35, 25), 1)
        cv2.ellipse(right_img, (240, 445), (80, 10), 0, 0, 360, accent_col, 1)

        mode_title = "REZIM: 1. CELO TELO"
        status_sub = "[MATRIX] MOCAP TELA: AKTIVAN" if active_model_mode == "MATRIX_KLON" else "MOCAP POKRETI TELA: AKTIVNI"

    # ================= REZIM 2: LICE, RUKE I PRSTI (BLIZU) =================
    else:
        mode_title = "REZIM: 2. LICE I RUKE"
        face_results = face_mesh.process(rgb_frame)
        hands_results = hands.process(rgb_frame)

        emotion_txt = "SKENIRANJE..."
        emotion_col = white_col
        emotion_conf = 0

        if face_results.multi_face_landmarks:
            lms = face_results.multi_face_landmarks[0].landmark
            pts_left = [(int(lm.x * 480), int(lm.y * 480)) for lm in lms]

            # 1. Diskretne konstelacijske linije (1px)
            overlay_mesh = left_img.copy()
            for p1_idx, p2_idx in DISCRETE_FACE_MESH:
                cv2.line(overlay_mesh, pts_left[p1_idx], pts_left[p2_idx], (255, 220, 140), 1, cv2.LINE_AA)

            # Precizne linije gornje i donje usne (spoljasnje i unutrasnje ivice sa otvaranjem)
            for lip_c in [UPPER_LIP_OUTER, UPPER_LIP_INNER, LOWER_LIP_INNER, LOWER_LIP_OUTER]:
                for k in range(len(lip_c) - 1):
                    cv2.line(overlay_mesh, pts_left[lip_c[k]], pts_left[lip_c[k+1]], (255, 215, 130), 1, cv2.LINE_AA)

            # Diskretne tackice (radijus 2px)
            for idx in GLOWING_NODES:
                cv2.circle(overlay_mesh, pts_left[idx], 2, (0, 230, 255), -1, cv2.LINE_AA)
                cv2.circle(overlay_mesh, pts_left[idx], 1, (255, 255, 255), -1, cv2.LINE_AA)

            # Polutransparentni blend za suptilan i diskretan izgled preko kamere
            cv2.addWeighted(overlay_mesh, 0.55, left_img, 0.45, 0, left_img)

            # 3. Analiza osecanja
            emotion_txt, emotion_conf, emotion_col, smile_p, mouth_p, brow_p, eye_p = analyze_emotions(pts_left)

            # ================= OPCIJA A: REALISTICAN FOTO-KLON NIKOLE TESLE =================
            if active_model_mode == "FOTO_TESLA" and tesla_loaded:
                # Izracunavamo deformaciju Teslinih tacaka na osnovu korisnika
                target_tesla_pts = tesla_base_pts.copy()

                # Deformacija usta (otvaranje i govor)
                mouth_open_dy = int(mouth_p * 0.32)
                offset_tesla_pt(target_tesla_pts, 14, dy=mouth_open_dy)
                offset_tesla_pt(target_tesla_pts, 17, dy=int(mouth_open_dy * 0.85))
                offset_tesla_pt(target_tesla_pts, 178, dy=int(mouth_open_dy * 0.80))
                offset_tesla_pt(target_tesla_pts, 402, dy=int(mouth_open_dy * 0.80))
                offset_tesla_pt(target_tesla_pts, 152, dy=int(mouth_open_dy * 0.40))
                offset_tesla_pt(target_tesla_pts, 13, dy=-int(mouth_open_dy * 0.15))
                offset_tesla_pt(target_tesla_pts, 0, dy=-int(mouth_open_dy * 0.15))

                # Osmeh (uglovi usana na gore i u sirinu - SAMO kad je osmeh stvaran!)
                if smile_p > 25:
                    smile_dy = int((smile_p - 25) * 0.18)
                    offset_tesla_pt(target_tesla_pts, 61, dx=-int(smile_dy * 0.6), dy=-smile_dy)
                    offset_tesla_pt(target_tesla_pts, 291, dx=int(smile_dy * 0.6), dy=-smile_dy)

                # Treptanje ociju (spustanje gornjih kapaka)
                if eye_p < 25:
                    blink_dy = int((25 - eye_p) * 0.30)
                    offset_tesla_pt(target_tesla_pts, 159, dy=blink_dy)
                    offset_tesla_pt(target_tesla_pts, 160, dy=blink_dy)
                    offset_tesla_pt(target_tesla_pts, 158, dy=blink_dy)
                    offset_tesla_pt(target_tesla_pts, 386, dy=blink_dy)
                    offset_tesla_pt(target_tesla_pts, 385, dy=blink_dy)
                    offset_tesla_pt(target_tesla_pts, 387, dy=blink_dy)

                # Obrve (podizanje)
                brow_dy = int((brow_p - 50) * 0.12)
                offset_tesla_pt(target_tesla_pts, 105, dy=-brow_dy)
                offset_tesla_pt(target_tesla_pts, 334, dy=-brow_dy)

                # Warping fotografije Tesle u realnom vremenu
                right_img = warp_tesla_face(target_tesla_pts)

            # ================= OPCIJA B: CYBER AVATAR KLON =================
            else:
                user_cx = (pts_left[234][0] + pts_left[454][0]) // 2
                user_cy = (pts_left[10][1] + pts_left[152][1]) // 2
                user_face_h = max(1, pts_left[152][1] - pts_left[10][1])
                scale_face = 250.0 / float(user_face_h)

                pts_right_face = []
                for p in pts_left:
                    rx = 240 + int((p[0] - user_cx) * scale_face)
                    ry = 210 + int((p[1] - user_cy) * scale_face)
                    pts_right_face.append((rx, ry))

                oval_poly = np.array([pts_right_face[i] for i in FACE_OVAL], dtype=np.int32)
                cv2.polylines(right_img, [oval_poly], True, accent_col, 2)

                for p1_idx, p2_idx in DISCRETE_FACE_MESH:
                    cv2.line(right_img, pts_right_face[p1_idx], pts_right_face[p2_idx], glow_col, 1)

                for idx in GLOWING_NODES:
                    cv2.circle(right_img, pts_right_face[idx], 2, white_col, -1)
                    cv2.circle(right_img, pts_right_face[idx], 4, accent_col, 1)

                cv2.polylines(right_img, [np.array([pts_right_face[i] for i in LEFT_EYEBROW], dtype=np.int32)], False, white_col, 2)
                cv2.polylines(right_img, [np.array([pts_right_face[i] for i in RIGHT_EYEBROW], dtype=np.int32)], False, white_col, 2)
                cv2.polylines(right_img, [np.array([pts_right_face[i] for i in LEFT_EYE], dtype=np.int32)], True, accent_col, 2)
                cv2.polylines(right_img, [np.array([pts_right_face[i] for i in RIGHT_EYE], dtype=np.int32)], True, accent_col, 2)

                left_iris = pts_right_face[468] if len(pts_right_face) > 468 else pts_right_face[373]
                right_iris = pts_right_face[473] if len(pts_right_face) > 473 else pts_right_face[153]
                cv2.circle(right_img, left_iris, 5, white_col, -1)
                cv2.circle(right_img, right_iris, 5, white_col, -1)

                cv2.fillPoly(right_img, [np.array([pts_right_face[i] for i in MOUTH_OPENING_LOOP], dtype=np.int32)], (5, 5, 10))
                cv2.polylines(right_img, [np.array([pts_right_face[i] for i in FULL_LIPS_OUTER], dtype=np.int32)], True, accent_col, 2)
                cv2.polylines(right_img, [np.array([pts_right_face[i] for i in MOUTH_OPENING_LOOP], dtype=np.int32)], True, white_col, 1)

        # Crtanje saka i prstiju (Hands)
        if hands_results.multi_hand_landmarks:
            for hand_idx, hand_lms in enumerate(hands_results.multi_hand_landmarks):
                h_pts_left = [(int(lm.x * 480), int(lm.y * 480)) for lm in hand_lms.landmark]

                for p1, p2 in HAND_CONNECTIONS:
                    cv2.line(left_img, h_pts_left[p1], h_pts_left[p2], (0, 255, 255), 2)

                for tip_idx in [4, 8, 12, 16, 20]:
                    cv2.circle(left_img, h_pts_left[tip_idx], 5, (0, 165, 255), -1)
                    cv2.circle(left_img, h_pts_left[tip_idx], 7, white_col, 1)

                # Prikaz ruku na desnoj strani pored modela
                h_pts_right = [(int(p[0] * 0.90 + 24), int(p[1] * 0.90 + 35)) for p in h_pts_left]

                for p1, p2 in HAND_CONNECTIONS:
                    cv2.line(right_img, h_pts_right[p1], h_pts_right[p2], accent_col, 2)
                    cv2.line(right_img, h_pts_right[p1], h_pts_right[p2], white_col, 1)

                for tip_idx in [4, 8, 12, 16, 20]:
                    cv2.circle(right_img, h_pts_right[tip_idx], 5, joint_col, -1)
                    cv2.circle(right_img, h_pts_right[tip_idx], 8, accent_col, 1)

        # Status osecanja
        if face_results.multi_face_landmarks:
            if active_model_mode == "FOTO_TESLA":
                model_tag = "TESLA"
            elif active_model_mode == "MATRIX_KLON":
                model_tag = "MATRIX"
            else:
                model_tag = "AVATAR"
            status_sub = f"[{model_tag}] OSECANJE: {emotion_txt} [{emotion_conf}%]"
        else:
            status_sub = "CEKAM LICE I RUKE U KADRU..."

    # Laser sken linija za Matrix mod (preko desnog ekrana)
    if active_model_mode == "MATRIX_KLON":
        scanline_y = (scanline_y + 4) % 480
        cv2.line(right_img, (0, scanline_y), (480, scanline_y), (0, 255, 120), 1)
        if 0 < scanline_y < 479:
            cv2.line(right_img, (0, scanline_y - 1), (480, scanline_y - 1), (0, 100, 40), 1)
            cv2.line(right_img, (0, scanline_y + 1), (480, scanline_y + 1), (0, 100, 40), 1)

    # ================= HUD I TEKSTOVI =================

    cv2.rectangle(left_img, (0, 0), (480, 42), (15, 15, 15), -1)
    cv2.putText(left_img, "1. ORIGINAL (SKENIRANJE)", (15, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.55, white_col, 2)

    header_col = (10, 24, 14) if active_model_mode == "MATRIX_KLON" else (20, 16, 12)
    cv2.rectangle(right_img, (0, 0), (480, 42), header_col, -1)
    if active_model_mode == "FOTO_TESLA":
        right_title = "2. FOTO-KLON: NIKOLA TESLA [s]"
    elif active_model_mode == "MATRIX_KLON":
        right_title = "2. MATRIX DVOJNIK: DIGITAL CLONE [s]"
    else:
        right_title = "2. DIGITALNI DVOJNIK: AVATAR [s]"
    cv2.putText(right_img, right_title, (15, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.50, accent_col, 2)

    cv2.putText(left_img, mode_title, (15, 465), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 255, 255), 2)

    if current_mode == "LICE_I_RUKE" and 'emotion_col' in locals():
        cv2.putText(right_img, status_sub, (15, 465), cv2.FONT_HERSHEY_SIMPLEX, 0.46, emotion_col, 2)
    else:
        cv2.putText(right_img, status_sub, (15, 465), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (0, 255, 0), 2)

    split_screen = np.hstack((left_img, right_img))

    cv2.line(split_screen, (479, 0), (479, 480), (35, 35, 35), 3)
    cv2.line(split_screen, (480, 0), (480, 480), accent_col, 2)

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
    prev_time = curr_time
    cv2.putText(split_screen, f"FPS: {int(fps)}", (960 - 85, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 255, 0), 2)

    cv2.imshow("AI Klon - Celo Telo vs Foto Klon vs Matrix (RPi 5)", split_screen)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break
    elif key == ord('s'):
        current_model_idx = (current_model_idx + 1) % len(MODEL_MODES)
        print(f"[INFO] Prebacen model na taster 's': {MODEL_MODES[current_model_idx]}")

if use_picam2:
    picam2.stop()
else:
    cap.release()

cv2.destroyAllWindows()
