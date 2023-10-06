from urllib.parse import urlparse

from yt_dlp import YoutubeDL

import os

import cv2

import tqdm

import multiprocessing

import json

import shutil

import time

import multiprocessing.pool as mpp


def istarmap(self, func, iterable, chunksize=1):
    """starmap-version of imap

    """

    if self._state != mpp.RUN:

        raise ValueError("Pool not running")

    if chunksize < 1:

        raise ValueError(

            "Chunksize must be 1+, not {0:n}".format(

                chunksize))

    task_batches = mpp.Pool._get_tasks(func, iterable, chunksize)

    result = mpp.IMapIterator(self._cache)

    self._taskqueue.put(

        (

            self._guarded_task_generation(result._job,

                                          mpp.starmapstar,

                                          task_batches),

            result._set_length

        ))

    return (item for chunk in result for item in chunk)


mpp.Pool.istarmap = istarmap


class loggerOutputs:

    def error(msg):

        return

    def warning(msg):

        return

    def debug(msg):

        return


def cut_video(video_path, start_frame, end_frame, output_path):

    if os.path.exists(output_path):
        return

    # remove file name from output path
    download_path = os.path.dirname(output_path)
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Open the input video and get the video properties
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video")
        return

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # Create the output video
    out = cv2.VideoWriter(output_path, fourcc, fps,
                          (frame_width, frame_height))
    # Jump to the starting frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    # Process the frames and write them to the output video asynchronously

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Write the frame to the output video
        out.write(frame)
        if cap.get(cv2.CAP_PROP_POS_FRAMES) >= end_frame+5:
            break

    # Release the input and output video objects
    cap.release()
    out.release()


download_pbar_lock = multiprocessing.Lock()


download_pbar = None


def download_video(url, path):

    global download_pbar

    if os.path.exists(path):

        print("Video already downloaded")

        return True

    # Set the options for the youtube-dl downloader

    options = {
        "format": "bestvideo/best",
        "outtmpl": path,

    }

    # add https:// to url if not present

    if not urlparse(url).scheme:
        url = "https://" + url

    try:
        with YoutubeDL(options) as ydl:
            ydl.download(url)
            print("Downloaded video")
            return True

    except Exception as e:
        print("Error downloading video", url)
        return False


def download_parallel(videos_pool):

    with mpp.Pool() as pool:
        for _ in pool.starmap(download_video, videos_pool):
            pass


def update_pbar_and_cut(video_path, start, end, output_path):

    if not os.path.exists(video_path):

        return

    cut_video(video_path, start, end, output_path)


def download_videos_from_json(json_file, download_path):

    global download_pbar

    if not os.path.exists(download_path):

        os.makedirs(download_path)

    import json

    with open(json_file) as f:

        data = json.load(f)

        url_map = set()

        for video in data:

            url_map.add(video["url"])

        # download the videos

        videos_pool = []

        for url in url_map:

            video_path = os.path.join(
                download_path, url.split("=")[-1] + ".mp4")

            videos_pool.append((url, video_path))

        download_parallel(videos_pool)
        print("Downloaded videos")

        videos_map = {}

        # add progress bar

        for video in data:

            video_id = video["url"].split("&")[0].split("=")[-1]

            if video_id not in videos_map:

                videos_map[video_id] = []

            videos_map[video_id].append(video)

        # add progress bar

        pbar = tqdm.tqdm(total=len(data), desc="Cutting videos")

        # loop through the video_map and cut the videos

        for video_id, videos in videos_map.items():

            # download the video

            video_path = os.path.join(download_path, video_id + ".mp4")

            # cut the video

            for video in videos:

                start = video["start"]

                end = video["end"]

                action = video["clean_text"]

                output_path = os.path.join(
                    download_path+'_CUT', action, video_id + "_" + action + ".mp4")

                update_pbar_and_cut(video_path, start, end, output_path)

                pbar.update(1)


def get_word(word):

    synonym_map = {}

    with open(os.path.join('MS-ASL', "MSASL_synonym.json")) as f:

        data = json.load(f)

        for synonym in data:

            synonym_map[synonym[0]] = synonym

    word = word.lower()

    word = word.split("/")[0]

    word = word.replace("-", " ")

    word = word.replace("#", "")

    for key, value in synonym_map.items():

        if word in value:

            return key

    return word


def combine_folder_to_one_folder(src_folders, dst_folder):

    import os

    import shutil

    if not os.path.exists(dst_folder):

        os.makedirs(dst_folder)

    for src_folder in os.listdir(src_folders):

        for action in os.listdir(os.path.join(src_folders, src_folder)):

            action_clean = get_word(action)

            if not os.path.exists(os.path.join(dst_folder, action_clean)):

                os.makedirs(os.path.join(dst_folder, action_clean))

            for video in os.listdir(os.path.join(src_folders, src_folder, action)):

                shutil.copy(os.path.join(src_folders, src_folder, action, video), os.path.join(
                    dst_folder, action_clean, video))


def categorize_wlasl():

    gloss_map = {}

    with open('WLASL_v0.3.json') as f:

        data = json.load(f)

        pbar = tqdm.tqdm(total=len(data))

        for video in data:

            gloss = video["gloss"]

            instances = video["instances"]

            for instance in instances:

                video_id = instance["video_id"]

                gloss_map[video_id] = gloss

                video_path = os.path.join('WLASL2000', video_id + ".mp4")

                if not os.path.exists(video_path):

                    continue

                output_path = os.path.join(
                    'WLASL2000_CUT', gloss, video_id + "_" + gloss + ".mp4")

                if not os.path.exists(os.path.join('WLASL2000_CUT', gloss)):

                    os.makedirs(os.path.join('WLASL2000_CUT', gloss))

                shutil.copy(video_path, output_path)

            pbar.update(1)


def fix_folders():

    # loop on folder in a directory

    for folder in os.listdir('ASLLVD_DATASET_CUT'):

        # loop on folder content

        for item in os.listdir(os.path.join('ASLLVD_DATASET_CUT', folder)):

            # check item is a folder

            if os.path.isdir(os.path.join('ASLLVD_DATASET_CUT', folder, item)):

                # loop on folder content

                for video in os.listdir(os.path.join('ASLLVD_DATASET_CUT', folder, item)):

                    # check video is a video

                    if video.endswith('.mp4'):

                        # move video to folder

                        shutil.move(os.path.join('ASLLVD_DATASET_CUT', folder, item, video), os.path.join(
                            'ASLLVD_DATASET_CUT', folder, video))

                # remove folder

                shutil.rmtree(os.path.join('ASLLVD_DATASET_CUT', folder, item))


def calc_avg_video_per_folder():

    import os

    import matplotlib.pyplot as plt

    # ALL_VIDEOS_CUT

    # display a graph of the number of videos that have 1-200 videos

    # loop on folder in a directory

    videos_per_folder = []

    for folder in os.listdir('ALL_VIDEOS_CUT'):

        # loop on folder content

        videos_per_folder.append(
            len(os.listdir(os.path.join('ALL_VIDEOS_CUT', folder))))

    # show actions that have less than more than 15

    cnt = 0

    for folder in os.listdir('ALL_VIDEOS_CUT'):

        if len(os.listdir(os.path.join('ALL_VIDEOS_CUT', folder))) <= 30:

            cnt = cnt + 1

    print(cnt)


def calc_videos():

    # open json file

    gloss_map = {}

    with open('MS-ASL\\MSASL_test.json') as f:

        data = json.load(f)

        for gloss in data:

            gloss = gloss["clean_text"]

            lower_gloss = gloss.lower()

            lower_gloss = get_word(lower_gloss)

            if lower_gloss not in gloss_map:

                gloss_map[lower_gloss] = 0

            gloss_map[lower_gloss] = gloss_map[lower_gloss] + 1

    with open('MS-ASL\\MSASL_train.json') as f:

        data = json.load(f)

        for gloss in data:

            gloss = gloss["clean_text"]

            lower_gloss = gloss.lower()

            lower_gloss = get_word(lower_gloss)

            if lower_gloss not in gloss_map:

                gloss_map[lower_gloss] = 0

            gloss_map[lower_gloss] = gloss_map[lower_gloss] + 1

    with open('MS-ASL\\MSASL_val.json') as f:

        data = json.load(f)

        for gloss in data:

            gloss = gloss["clean_text"]

            lower_gloss = gloss.lower()

            lower_gloss = get_word(lower_gloss)

            if lower_gloss not in gloss_map:

                gloss_map[lower_gloss] = 0

            gloss_map[lower_gloss] = gloss_map[lower_gloss] + 1

    # with open('WLASL_v0.3.json') as f:

    #     data = json.load(f)

    #     for gloss in data:

    #         lower_gloss = gloss["gloss"]

    #         lower_gloss = lower_gloss.lower()

    #         lower_gloss = get_word(lower_gloss)

    #         if lower_gloss not in gloss_map:

    #             gloss_map[lower_gloss] = 0

    #         gloss_map[lower_gloss] = gloss_map[lower_gloss]+len(gloss["instances"])

    # with open('asllvd.json') as f:

    #     data = json.load(f)

    #     for gloss in data:

    #         length = len(data[gloss])

    #         lower_gloss = gloss.lower().split("/")[0]

    #         lower_gloss = get_word(lower_gloss)

    #         if lower_gloss not in gloss_map:

    #             gloss_map[lower_gloss] = 0

    #         gloss_map[lower_gloss] = gloss_map[lower_gloss] + length

    #         lower_gloss2 = gloss.lower().split("/")[-1]

    #         if lower_gloss2 == lower_gloss:

    #             continue

    #         lower_gloss2 = get_word(lower_gloss2)

    #         if lower_gloss2 not in gloss_map:

    #             gloss_map[lower_gloss2] = 0

    #         gloss_map[lower_gloss2] = gloss_map[lower_gloss2] + length

    # with open("ASL_Videos.json") as f:

    #     data = json.load(f)

    #     for gloss in data:

    #         gloss = gloss["gloss"]

    #         lower_gloss = gloss.lower()

    #         lower_gloss = get_word(lower_gloss)

    #         if lower_gloss not in gloss_map:

    #             gloss_map[lower_gloss] = 0

    #         gloss_map[lower_gloss] = gloss_map[lower_gloss] + 1

    # remove actions that have less than 15 videos

    for key in list(gloss_map.keys()):

        if gloss_map[key] < 30:

            del gloss_map[key]

    # print top 30 action with most videos

    print(sorted(gloss_map.items(), key=lambda x: x[1], reverse=True)[:30])

    # print top 30 action with least videos

    print(sorted(gloss_map.items(), key=lambda x: x[1], reverse=False)[:30])

    # print number of actions

    print('number of actions: ' + str(len(gloss_map)))

    # print average number of videos per action

    print('average number of videos per action: ' +
          str(sum(gloss_map.values()) / len(gloss_map)))

    # print max number of videos per action

    print('max number of videos per action: ' + str(max(gloss_map.values())))

    # print min number of videos per action

    print('min number of videos per action: ' + str(min(gloss_map.values())))

    import matplotlib.pyplot as plt

    # show a graph showing the number of actions that have x videos

    plt.hist(gloss_map.values(), bins=100)

    plt.show()


if __name__ == "__main__":

    download_videos_from_json("MS-ASL/test.json",
                              os.path.join("MSASL", "MSASL_val"))

    print("done val")

    download_videos_from_json(
        "MS-ASL/MSASL_train.json", os.path.join("MSASL", "MSASL_train"))

    print("done train")

    download_videos_from_json("MS-ASL/MSASL_test.json",
                              os.path.join("MSASL", "MSASL_test"))

    print("done test")

    # calc_videos()

    # combine_folder_to_one_folder("DATASETS" , "all_vids")

    # actions = os.listdir(os.path.join("actions"))

    # DATASETS_PATH = os.path.join("DATASETS")

    # # the datasets path has folders for each dataset and each dataset has folders for each action

    # # copy the videos from the actions folder to the dataset folder if the action is in the dataset

    # for dataset in os.listdir(DATASETS_PATH):

    #     dataset_path = os.path.join(DATASETS_PATH, dataset)

    #     for action in os.listdir(dataset_path):

    #         clean_action = get_word(action)

    #         if clean_action in actions:

    #             action_path = os.path.join(dataset_path, action)

    #             videos = os.listdir(action_path)

    #             for video in videos:

    #                 video_path = os.path.join(action_path, video)

    #                 #check if the viode is already in the actions folder

    #                 if video in os.listdir(os.path.join("actions", clean_action)):

    #                     continue

    #                 shutil.copy(video_path, os.path.join("actions", clean_action))

    #                 print("copied " + video_path + " to " + os.path.join("actions", clean_action))
