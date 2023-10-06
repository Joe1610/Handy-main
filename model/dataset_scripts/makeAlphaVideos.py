import os
import cv2

path = "path/to/asl_alphabet_train/"
letters = os.listdir(path)
cv2_fourcc = cv2.VideoWriter_fourcc(*'mp4v')

for letter in letters:
    out_path = os.path.join(path[:-1] + "_videos", letter)
    os.makedirs(out_path, exist_ok=True)
    count = 0

    for i in range(1, 3000, 30):
        count += 1
        out_video_full_path = os.path.join(out_path, f"video{count}.mp4")
        seq = [os.path.join(path, f"{letter}/{letter}{i}.jpg")
               for i in range(i, i+30)]

        frame = cv2.imread(seq[0])
        size = list(frame.shape)
        del size[2]
        size.reverse()

        # output video name, fourcc, fps, size
        video = cv2.VideoWriter(out_video_full_path,
                                cv2_fourcc, 30, tuple(size))

        for j in range(len(seq)):
            video.write(cv2.imread(seq[j]))
            print('frame', j+1, 'of', len(seq))

        video.release()
        print('outputted video to', out_path)
