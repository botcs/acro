#!/usr/bin/env python3
import cv2
import time
import datetime
import numpy as np
import sys
import os

camid = int(sys.argv[1])

# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(camid)
codec = cv2.VideoWriter_fourcc( 'M', 'J', 'P', 'G'  )
cap.set(6, codec)
cap.set(5, 60)
# cap.set(3, 1920)
# cap.set(4, 1080)
cap.set(3, 1280)
cap.set(4, 720)

FRAME_DELAY = 1

cv2.namedWindow('frame', cv2.WINDOW_KEEPRATIO)

print("FPS", cap.get(5))
print("Size", (int(cap.get(3)), int(cap.get(4))))

timestr = time.strftime("%Y%m%d-%H%M%S")
avi_file_name = f"REC/{timestr}.avi"
out = cv2.VideoWriter(
    avi_file_name,
    codec,
    cap.get(5),
    (int(cap.get(3)), int(cap.get(4)))
)

# cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


FPS_COUNT = 0
def readCam(flip=False, timestamp=True):
    global FPS_COUNT

    ret, frame = cap.read()
    assert frame is not None

    FPS_COUNT += 1

    if flip:
       frame = cv2.flip(frame, 0)

    if timestamp:
        frame = cv2.putText(
            frame,
            str(datetime.datetime.now()),
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            .9, (0, 255, 0), 1, cv2.LINE_AA)

    return np.array(frame)


unseen_buffer = []
history_buffer = []

for i in range(FRAME_DELAY):
    frame = readCam()
    pressed_key = cv2.waitKey(30) & 0xFF

    unseen_buffer.append(frame)

    frame = cv2.putText(
        np.array(frame),
        f"Buffering DELAY: {FPS_COUNT} / {FRAME_DELAY}",
        (10, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        .9, (0, 255, 0), 1, cv2.LINE_AA)

    cv2.imshow('frame',frame)



def mirror(pressed_key):
    # Capture frame-by-frame
    t = time.time()

    frame = readCam()

    out.write(frame)
    unseen_buffer.append(frame)
    frame = unseen_buffer.pop(0)
    history_buffer.append(frame)

    if len(history_buffer) > 30 * 600: # translates to 10 min @ 30 FPS
        history_buffer.pop(0)


    frame = cv2.putText(
        np.array(frame),
        f"REC: {len(history_buffer)}",
        (10, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        .9, (0, 0, 255), 1, cv2.LINE_AA)

    cv2.imshow('frame',frame)


def replay(pressed_key):
    global frame_idx
    if pressed_key == ord('j'):
        frame_idx = frame_idx-1
        if frame_idx < 0:
            frame_idx = 0
            print("Oldest frame")

    if pressed_key == ord('k'):
        frame_idx = frame_idx+1
        if frame_idx > len(history_buffer)-1:
            frame_idx = len(history_buffer)-1
            print("Newest frame... Resume mirroring")
            return True

    frame = history_buffer[frame_idx]


    frame = cv2.putText(
        np.array(frame),
        f"REP: {frame_idx+1} / {len(history_buffer)}",
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        .9, (0, 255, 0), 1, cv2.LINE_AA)

    cv2.imshow('frame',frame)
    return False

PAUSE = False
while(True):
    pressed_key = cv2.waitKey(30) & 0xFF
    if pressed_key == ord('q'):
        print("\nQ pressed, quitting app...\n")
        break
    elif pressed_key == ord(' '):
        if not PAUSE:
            PAUSE = True
            frame_idx = len(history_buffer) - 1
            print("\nRewind time!")
        else:
            PAUSE = False
            print("\nResume mirroring")
    elif pressed_key == ord('j'):
        if not PAUSE:
            PAUSE = True
            frame_idx = len(history_buffer) - 1
            print("\nRewind time!")


    if PAUSE:
        hit_newest_frame = replay(pressed_key)
        if hit_newest_frame:
            PAUSE = False
    else:
        mirror(pressed_key)


# When everything done, release the capture
cap.release()
out.release()
cv2.destroyAllWindows()

print("Saved recordings to:", avi_file_name)

# def convert_avi_to_mp4(avi_file_name, _name):
#     # os.popen(
#     #     f"ffmpeg -i '{avi_file_name}' -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 '{output}.mp4'"
#     # )

print(f"converting to {avi_file_name[:-4]+'.mp4'}")
os.popen(
    f"ffmpeg -hide_banner -loglevel warning -i {avi_file_name} {avi_file_name[:-4]+'.mp4'}"
)
print("Done!")


