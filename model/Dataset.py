from itertools import repeat
import math
import multiprocessing
import os
import shutil
from typing import List
from tqdm import tqdm
import numpy as np
from mediapipeHelper import *
import cv2
import time
import json
import istarmap
import concurrent.futures
from main import main, FRAMES_PER_VIDEO
# import pandas as pd
from helper import split_data, VIDEO_NAME_SEPARATOR


class Dataset:

    # static variables
    resize_values = [0.5, 1.5]
    # features_output_folder_name = 'MP_Data_New'
    num_cpu_for_multiprocessing = multiprocessing.cpu_count()
    rotate_times = 0,
    aspect_ratio_times = 0,
    non_moving_frames_threshold = 0
    accumulative_augmentation = True

    def __init__(
            self,
            dataset_folder_path="DATASETS",
            num_frames_per_video=30,
            resize_values=[0.5, 1.5],
            rotate_times=0,
            aspect_ratio_times=0,
            non_moving_frames_threshold=0,
            save_features_only=True,
            accumulative_augmentation=True
    ):
        if resize_values is not None:
            Dataset.resize_values = resize_values

        Dataset.rotate_times = rotate_times
        Dataset.aspect_ratio_times = aspect_ratio_times
        Dataset.non_moving_frames_threshold = non_moving_frames_threshold
        self.dataset_folder_path = dataset_folder_path
        self.num_frames_per_video = num_frames_per_video
        self.all_videos_folder_name = 'all_vids'
        self.accumulative_augmentation = accumulative_augmentation
        # self.all_vids_augmented_folder_name = 'all_vids_augmented'

        self.save_features_only = save_features_only

    def process(self):
        self._remove_corrupted_videos()
        if self.non_moving_frames_threshold > 0:
            self._remove_none_moving_frames_from_videos()
        self._adjust_videos_total_frames()
        self._rename_videos()
        split_data()
        self._increase_videos_by_data_augmentation()
        # self._save_videos_per_actions_json()
        if not self.save_features_only:
            self._save_videos_features()

    def _rename_videos(self) -> None:
        vids: List[str] = Dataset.get_all_vids_paths(
            self.all_videos_folder_name)
        Dataset.rename_videos(vids)

    @staticmethod
    def rename_videos(vids):
        for vid in vids:
            # rename from all_vids/action/video.mp4 to all_vids/action/video$separator$.mp4
            os.rename(vid, vid.replace('.mp4', VIDEO_NAME_SEPARATOR + '.mp4'))

    def _put_all_videos_in_one_folder(self) -> None:
        if not os.path.exists(self.all_videos_folder_name):
            os.makedirs(self.all_videos_folder_name, exist_ok=True)
        # ['whatever//whatever//action//video.mp4']
        vids: List[str] = self.get_all_vids_paths(self.dataset_folder_path)
        pbar: tqdm = tqdm(
            total=len(vids), desc='Putting all videos in one folder')
        for video in vids:
            action: str = video.split(os.sep)[-2]
            video_name: str = video.split(os.sep)[-1]
            # check if video already exists
            if not os.path.exists(os.path.join(self.all_videos_folder_name, action, video_name)):
                # create the folder for the action if it doesn't exist
                if not os.path.exists(os.path.join(self.all_videos_folder_name, action)):
                    os.makedirs(os.path.join(
                        self.all_videos_folder_name, action), exist_ok=True)
                # copy the video to the folder
                shutil.copy(video, os.path.join(
                    self.all_videos_folder_name, action))
            pbar.update()

    def _remove_corrupted_videos(self) -> None:
        vids: List[str] = Dataset.get_all_vids_paths(
            self.all_videos_folder_name)
        Dataset.remove_corrupted_videos(vids)

    def _remove_none_moving_frames_from_videos(self) -> None:
        vids = Dataset.get_all_vids_paths(self.all_videos_folder_name)
        Dataset.remove_none_moving_frames_from_videos(vids)

    def _adjust_videos_total_frames(self) -> None:
        vids: List[str] = Dataset.get_all_vids_paths(
            self.all_videos_folder_name)
        Dataset.regulate_videos_total_frames(
            vids, self.num_frames_per_video, self.all_videos_folder_name)

    def _increase_videos_by_data_augmentation(self) -> None:
        Dataset.increase_videos_by_data_augmentation(
            'Train_unaugmented', 'Train', self.save_features_only, self.accumulative_augmentation)
        shutil.rmtree('Train_unaugmented')

    # def _save_videos_per_actions_json(self) -> None:
    #     Dataset.save_videos_per_actions_json(
    #         self.all_vids_augmented_folder_name)

    def _save_videos_features(self) -> None:
        vidsTRAIN = Dataset.get_all_vids_paths('Train')
        Dataset.save_videos_features(vidsTRAIN, 'MP_Train')

        vidsTEST = Dataset.get_all_vids_paths('Test')
        Dataset.save_videos_features(vidsTEST, 'MP_Test')

        vidsVAL = Dataset.get_all_vids_paths('Val')
        Dataset.save_videos_features(vidsVAL, 'MP_Val')

        shutil.rmtree('Train')
        shutil.rmtree('Test')
        shutil.rmtree('Val')

    @staticmethod
    def regulate_videos_total_frames(videos_paths, num_frames_per_video, output_folder_name):
        inputs = [(video_path, video_path.replace(
            'all_vids', 'all_vids_regulated'), num_frames_per_video) for video_path in videos_paths]
        # create the folders for the regulated videos

        for input in inputs:
            if not os.path.exists(os.path.dirname(input[1])):
                os.makedirs(os.path.dirname(input[1]))

        with multiprocessing.Pool(processes=Dataset.num_cpu_for_multiprocessing) as p:
            with tqdm(total=len(videos_paths), desc='Adjusting videos total frames') as pbar:
                # call adjust_video_total_frames_using_interpolation for each video with 3 arguments
                # output_path should be the same as the input_path but with parent changed to 'all_vids_regulated'
                for _ in p.istarmap(Dataset.adjust_video_total_frames_using_interpolation, inputs):
                    pbar.update()

        shutil.rmtree('all_vids')
        os.rename('all_vids_regulated', 'all_vids')

    @staticmethod
    def save_video_features(video_path, output):
        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            # get the number of frames in the video
            cap = cv2.VideoCapture(os.path.join(video_path))
            length: int = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # output path will be the same as input but with changing first folder to (MP_Train || MP_Test || MP_Val) and adding .npy
            # split using the os separator
            output_path = video_path.split(os.sep)

            output_path[0] = output
            # print(f'the output folder is {output_path}')
            # remove the file extension
            output_path[-1] = os.path.splitext(output_path[-1])[0]
            # add .npy
            output_path[-1] += '.npy'
            # join the path
            output_path = os.sep.join(output_path)

            # check if the file already exists
            if os.path.exists(output_path):
                return
            if not os.path.exists(os.path.dirname(output_path)):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Loop through frames
            to_save = []
            for frame_num in range(length):
                # Read feed
                success, image = cap.read()
                # Make detections
                if image is None:
                    continue

                image, results = mediapipe_detection(image, holistic)
                # Export keypoints
                keypoints = extract_keypoints(results)
                to_save.append(keypoints)

            np.save(output_path, to_save)
            cap.release()
            cv2.destroyAllWindows()

    @staticmethod
    def save_videos_features(vids: List[str], output):
        inputs = []
        for vid in vids:
            inputs.append((vid, output))

        with multiprocessing.Pool(processes=Dataset.num_cpu_for_multiprocessing) as p:
            with tqdm(total=len(inputs), desc='Saving videos features') as pbar:
                for _ in p.istarmap(Dataset.save_video_features, inputs):
                    pbar.update()

    @staticmethod
    def get_all_vids_paths(folder_path):
        video_extensions = [
            "3g2",
            "3gp",
            "aaf",
            "asf",
            "avchd",
            "avi",
            "drc",
            "flv",
            "m2v",
            "m3u8",
            "m4p",
            "m4v",
            "mkv",
            "mng",
            "mov",
            "mp2",
            "mp4",
            "mpe",
            "mpeg",
            "mpg",
            "mpv",
            "mxf",
            "nsv",
            "ogg",
            "ogv",
            "qt",
            "rm",
            "rmvb",
            "roq",
            "svi",
            "vob",
            "webm",
            "wmv",
            "yuv"
        ]
        # get all the paths of the videos (.mp4) in folder or subfolders
        vids_paths = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.split('.')[-1] in video_extensions:
                    vids_paths.append(os.path.join(root, file))
        return vids_paths

    @staticmethod
    def adjust_video_total_frames_using_interpolation(video_path, output_path, num_frames):

        # read the video
        cap = cv2.VideoCapture(video_path)
        # get the total number of frames
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # get the width and height of the video
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # check if the video in the output path already exists
        if os.path.exists(output_path):
            # check if the video has the same number of frames
            cap2 = cv2.VideoCapture(output_path)
            total_frames2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames2 == num_frames:
                # if the video has the same number of frames, return
                cap.release()
                cap2.release()
                return

        # calculate the ratio
        ratio = total_frames / float(num_frames)
        # create a new video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, num_frames, (width, height))
        # loop through the frames
        for i in range(num_frames):
            # get the frame number
            frame_number = int(i * ratio)
            if frame_number >= total_frames:
                frame_number = total_frames - 1
            if frame_number < 0:
                frame_number = 0
            # set the frame number

            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            # read the frame
            ret, frame = cap.read()
            retry_count = 0
            while not ret:
                cap.release()
                cap = cv2.VideoCapture(video_path)
                ret, frame = cap.read()
                retry_count += 1
                if retry_count > 10:
                    break
            # write the frame
            out.write(frame)
        # release the video
        cap.release()
        # release the video writer
        out.release()
        # close all windows
        cv2.destroyAllWindows()

    @staticmethod
    def random_rotation(frame):
        """
        Applies a random rotation to a video frame with a maximum rotation angle of 20 degrees left or right.
        """
        # Generate a random angle between -7 and 7 degrees
        max_angle = 8
        angle = np.random.randint(-max_angle, max_angle)

        # Get the height and width of the frame
        height, width = frame.shape[:2]

        # Calculate the rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D(
            (width/2, height/2), angle, 1)

        # Apply the rotation to the frame
        rotated_frame = cv2.warpAffine(frame, rotation_matrix, (width, height))

        return rotated_frame

    @staticmethod
    def rotate_video(input_path, vid_num="", output_folder_name=""):
        # output_path save as input_path but adding _rotated to the name and the angle
        output_path = input_path[:-4] + '_rotated_' + str(vid_num) + '.mp4'
        # replace first folder with output folder
        output_path = output_path.replace(
            input_path.split(os.sep)[0], output_folder_name)

        if os.path.exists(output_path) or 'rotated' in input_path:
            return
        # create output folder if it does not exist
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        # Open input video file
        cap = cv2.VideoCapture(input_path)

        # Get the codec information of input video
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))

        # Get the frame rate of input video
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Get the dimensions of input video
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Create VideoWriter object to write the rotated video
        out = cv2.VideoWriter(output_path, fourcc, fps,
                              (frame_width, frame_height))

        while cap.isOpened():
            # Read a frame from input video
            ret, frame = cap.read()

            if ret:
                # Rotate the frame
                rotated_frame = Dataset.random_rotation(frame)

                out.write(rotated_frame)

            else:
                break

        # Release input and output video
        cap.release()
        out.release()

        # Close all windows
        cv2.destroyAllWindows()

    @staticmethod
    def change_video_aspect_ratio(input_path, vid_num=1, output_folder_name=""):
        # Open input video file
        cap = cv2.VideoCapture(input_path)

        # input = all_vids/action/video_name.mp4
        # output = output_folder/action/video_name_aspect_ratio_changed.mp4

        # replace first folder with output folder

        output_folder = os.path.dirname(input_path.replace(
            input_path.split(os.sep)[0], output_folder_name))

       # create output folder if it does not exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Get the codec information of input video
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))

        # Get the frame rate of input video
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Get the dimensions of input video
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        aspect_ratios = [4.0/3.0, 16.0/9.0, 16.0/10.0, 21.0/9.0,
                         1.0, 3.0/4.0, 9.0/16.0, 10.0/16.0, 9.0/21.0]

        # choose a different aspect ratio and make sure it is not the same as the original aspect ratio
        # new_aspect_ratio = aspect_ratios[0] if round(aspect_ratios[0], 2) != round(
        #     frame_width / frame_height, 2) else aspect_ratios[1]

        for index, aspect_ratio in enumerate(aspect_ratios):
            if index < vid_num-1:
                continue

            if round(aspect_ratio, 2) != round(frame_width / frame_height, 2):
                # check if the video has the same aspect ratio saved already in the output_folder
                if os.path.exists(output_folder + os.sep + input_path.split(os.sep)[-1][:-4] + '_aspect_ratio_changed_' + str(round(aspect_ratio, 2)) + '.mp4'):
                    print(
                        f"video {input_path} already has aspect ratio {aspect_ratio} saved")
                    return

                new_aspect_ratio = aspect_ratio
                break

        new_height = 0
        new_width = 0
        # Calculate the new dimensions of the frame
        if frame_width > frame_height:
            new_height = int(frame_width / new_aspect_ratio)
            new_width = frame_width

        else:
            new_height = frame_height
            new_width = int(frame_height * new_aspect_ratio)

        new_aspect_ratio = round(new_width / new_height, 2)
        # Create VideoWriter object to write the resized video
        out = cv2.VideoWriter(output_folder + os.sep + input_path.split(os.sep)[-1][:-4] + '_aspect_ratio_changed_' + str(new_aspect_ratio) + '.mp4', fourcc, fps,
                              (new_width, new_height))

        while cap.isOpened():
            # Read a frame from input video
            ret, frame = cap.read()

            if ret:
                # Resize the frame
                resized_frame = cv2.resize(frame, (new_width, new_height))
                # Write the resized frame to output video
                out.write(resized_frame)

            else:
                break

        # Release input and output video
        cap.release()
        out.release()

    @staticmethod
    def resize_video(input_path,  multiplier=2.0, output_folder_name=""):

        # output_path save as input_path but adding _resized to the name and the multiplier
        output_path = input_path[:-4] + '_resized_' + str(multiplier) + 'x.mp4'

        # replace first folder with output folder
        output_path = output_path.replace(
            input_path.split(os.sep)[0], output_folder_name)

        # create output folder if it does not exist
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        # check if the resized video already exists
        if os.path.exists(output_path) or "resized" in input_path:
            return

        # Open input video file
        cap = cv2.VideoCapture(input_path)

        # Get the codec information of input video
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))

        # Get the frame rate of input video
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Get the dimensions of input video
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = math.ceil(frame_width * multiplier)
        height = math.ceil(frame_height * multiplier)
        # Create VideoWriter object to write the resized video
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        while cap.isOpened():
            # Read a frame from input video
            ret, frame = cap.read()

            if ret:
                # Resize the frame
                resized_frame = cv2.resize(frame, (width, height))
                # Write the resized frame to output video
                out.write(resized_frame)

            else:
                break

        # Release resources
        cap.release()
        out.release()
        cv2.destroyAllWindows()

    @staticmethod
    def increase_videos_by_data_augmentation(folder_path, output_folder, save_features_only=False, accumulative_augmentation=True):
        all_pbar = tqdm(total=len(os.listdir(folder_path)),
                        desc='Increasing videos by data augmentation')

        for action in os.listdir(folder_path):
            vids = Dataset.get_all_vids_paths(folder_path + os.sep + action)

            for vid in vids:
                output_path = vid.replace(folder_path, output_folder)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                shutil.copyfile(vid, output_path)

            inputs = [(vid, i + 1, output_folder)
                      for vid in vids for i in range(Dataset.aspect_ratio_times)]
            with multiprocessing.Pool(processes=Dataset.num_cpu_for_multiprocessing) as p:
                with tqdm(total=len(inputs), desc='Changing videos aspect ratio') as pbar:
                    for _ in p.istarmap(Dataset.change_video_aspect_ratio, inputs):
                        pbar.update()

            if accumulative_augmentation:
                vids = Dataset.get_all_vids_paths(
                    output_folder + os.sep + action)
            inputs = [(vid, resize_value, output_folder)
                      for resize_value in Dataset.resize_values for vid in vids]
            with multiprocessing.Pool(processes=Dataset.num_cpu_for_multiprocessing) as p:
                with tqdm(total=len(inputs), desc='Resizing videos') as pbar:
                    for _ in p.istarmap(Dataset.resize_video, inputs):
                        pbar.update()

            if accumulative_augmentation:
                vids = Dataset.get_all_vids_paths(
                    output_folder + os.sep + action)
            inputs = [(vid, i, output_folder)
                      for vid in vids for i in range(Dataset.rotate_times)]
            with multiprocessing.Pool(processes=Dataset.num_cpu_for_multiprocessing) as p:
                with tqdm(total=len(inputs), desc='Rotating videos') as pbar:
                    for _ in p.istarmap(Dataset.rotate_video, inputs):
                        pbar.update()

            # if save_features_only:
            #     Dataset.save_videos_features(
            #         Dataset.get_all_vids_paths(output_folder))
            #     shutil.rmtree(output_folder)

            all_pbar.update()

    @staticmethod
    def detect_non_moving_frames(video_path,  threshold=0.8):
        moving_video_suffix = '_moving.mp4'
        if video_path.endswith(moving_video_suffix):
            return
        # Initialize the video capture object
        output_path = video_path[:-4] + moving_video_suffix
        cap = cv2.VideoCapture(video_path)

        # Get the video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Initialize the video writer object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        def read_retry(cap, n=10):
            for i in range(n):
                ret, frame = cap.read()
                if ret:
                    return ret, frame
            return False, None

        # Initialize the previous frame
        ret, prev_frame = read_retry(cap)
        if not ret:
            return

        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        # Convert the frame to grayscale
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

        while True:
            # Read the current frame
            ret, frame = read_retry(cap)
            if not ret:
                break

            # Convert the frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # image, results = mediapipe_detection(frame, holistic)

            # if not results.left_hand_landmarks:
            #     continue
            # if not results.right_hand_landmarks:
            #     continue

            # Calculate the difference between the current and previous frames
            diff = cv2.absdiff(gray, prev_gray)

            # Check if the difference falls below the threshold
            if cv2.mean(diff)[0] < threshold:
                continue

            # Write the frame to the output video
            out.write(frame)

            # Update the previous frame
            prev_gray = gray

        # Release the video capture and writer objects
        cap.release()
        out.release()

        # Delete the old video
        os.remove(video_path)
        # Rename the new video and remove the suffix
        os.rename(output_path, video_path)

    @staticmethod
    def remove_none_moving_frames_from_video(video_path, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        moving_video_suffix = '_moving.mp4'
        if video_path.endswith(moving_video_suffix):
            return
        cap = cv2.VideoCapture(video_path)
        # Get the codec information of input video
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))

        # Get the frame rate of input video
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Get the dimensions of input video
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Create VideoWriter object to write the resized video
        output_path = video_path[:-4] + moving_video_suffix
        out = cv2.VideoWriter(output_path, fourcc, fps,
                              (frame_width, frame_height))

        with mp_holistic.Holistic(min_detection_confidence=min_detection_confidence,
                                  min_tracking_confidence=min_tracking_confidence) as holistic:
            while cap.isOpened():
                # Read a frame from input video
                ret, frame = cap.read()

                if ret:
                    image, results = mediapipe_detection(frame, holistic)
                    # Export keypoints
                    keypoints = extract_keypoints(results)
                    # check if the keypoints are moving by checking if all the keypoints are 0
                    is_moving = np.sum(keypoints) != 0
                    if is_moving:
                        out.write(frame)

                else:
                    break

            # Release resources
            cap.release()
            out.release()
            cv2.destroyAllWindows()

            # delete the old video
            # os.remove(video_path)

            return None

    @staticmethod
    def remove_none_moving_frames_from_videos(videos_paths):
        inputs = []
        for video_path in videos_paths:
            inputs.append((video_path, Dataset.non_moving_frames_threshold))

        with multiprocessing.Pool(processes=Dataset.num_cpu_for_multiprocessing) as p:
            with tqdm(total=len(inputs), desc='removing non moving frames') as pbar:
                for _ in p.istarmap(Dataset.detect_non_moving_frames, inputs):
                    pbar.update()

    @staticmethod
    def is_video_corrupted(video_path):
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return True
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
            cap.release()
            return False
        except:
            return True

    @staticmethod
    def remove_corrupted_videos(videos_paths):
        number_of_deleted_videos = 0
        pbar = tqdm(total=len(videos_paths), desc='Removing corrupted videos')
        for video_path in videos_paths:
            if Dataset.is_video_corrupted(video_path):
                number_of_deleted_videos += 1
                os.remove(video_path)
            pbar.update()
        print(f'{number_of_deleted_videos} videos were deleted')

    @staticmethod
    def save_videos_per_actions_json(videos_path='all_vids_regulated', json_path='videos_per_actions.json'):
        videos_per_actions = {}
        for action in os.listdir(videos_path):
            videos_per_actions[action] = len(os.listdir(
                os.path.join(videos_path, action)))
        # sort from largest to smallest
        videos_per_actions = dict(
            sorted(videos_per_actions.items(), key=lambda item: item[1], reverse=True))
        with open(os.path.join(json_path), 'w') as f:
            json.dump(videos_per_actions, f)


def reset_state():
    folders_to_remove = ['MP_Test', 'MP_Val',
                         'MP_Train', 'all_vids', 'Test', 'Val', 'Train']
    files_to_remove = ['x_train.npy', 'y_train.npy', 'x_test.npy',
                       'y_test.npy', 'x_val.npy', 'y_val.npy']

    for folder in folders_to_remove:
        if os.path.exists(folder):
            shutil.rmtree(folder)

    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)

    # copy the folder name top_10 and rename it to all_vid
    shutil.copytree('original_vids', 'all_vids')


# def append_results_to_excel(results, excel_path='results.xlsx'):
#     if not os.path.exists(excel_path):
#         df = pd.DataFrame(columns=['resize_values', 'rotate_times', 'aspect_ratio_times',
#                                    'accuracy', 'max_accuracy', 'average_accuracy', 'non_moving_frames_threshold', 'num_of_frames', 'accumulative_augmentation'])
#         df.to_excel(excel_path, index=False)

#     df = pd.read_excel(excel_path)
#     df = df.append(results, ignore_index=True)
#     df.to_excel(excel_path, index=False)


if __name__ == '__main__':
    possible_aspect_ratio_times = [1]
    possible_resize_values = [
        # [1.5, 0.5, 1.8, 1.2],
        # [1.5, 0.5, 1.8],
        # [1.5],
        [1.5, 0.5],
        # [],

    ]
    possible_rotate_times = [2]

    possible_non_moving_frames_threshold = [0.08]
    possible_num_of_frames = [30]
    accumulative_augmentations = [False]

    # reset_state()
    # d = Dataset(resize_values=[1.5],
    #             rotate_times=1,
    #             aspect_ratio_times=2,
    #             non_moving_frames_threshold=0.1
    #             )
    # d.process()

    # wait for cpu cores to finish

    # split_data()
    # results = {}
    # accuracy_data, max_accuracy, average_accuracy = main()
    # results['accuracy'] = accuracy_data
    # results['max_accuracy'] = max_accuracy
    # results['average_accuracy'] = average_accuracy
    # results['resize_values'] = [1.5]
    # results['rotate_times'] = 1
    # results['aspect_ratio_times'] = 2
    # results['non_moving_frames_threshold'] = 0.1
    # append_results_to_excel(results)

    for resize_values in possible_resize_values:
        for rotate_times in possible_rotate_times:
            for aspect_ratio_times in possible_aspect_ratio_times:
                for non_moving_frames_threshold in possible_non_moving_frames_threshold:
                    for num_of_frames in possible_num_of_frames:
                        for accumulative_augmentation in accumulative_augmentations:
                            # # read and parse the excel file to skip the already done experiments
                            # if os.path.exists('results.xlsx'):
                            #     # check if all the parameters are the same
                            #     df = pd.read_excel('results.xlsx')
                            #     df = df.loc[(df['resize_values'] == str(resize_values)) &
                            #                 (df['rotate_times'] == rotate_times) &
                            #                 (df['aspect_ratio_times'] == aspect_ratio_times) &
                            #                 (df['non_moving_frames_threshold'] == non_moving_frames_threshold) &
                            #                 (df['num_of_frames'] == num_of_frames) &
                            #                 (df['accumulative_augmentation'] == accumulative_augmentation)]

                            #     if len(df) > 0:
                            #         print(
                            #             f'Skipping {resize_values}, {rotate_times}, {aspect_ratio_times}, {non_moving_frames_threshold}, {num_of_frames}, {accumulative_augmentation}')
                            #         continue

                            reset_state()
                            d = Dataset(resize_values=resize_values,
                                        rotate_times=rotate_times,
                                        aspect_ratio_times=aspect_ratio_times,
                                        non_moving_frames_threshold=non_moving_frames_threshold,
                                        save_features_only=False,
                                        num_frames_per_video=num_of_frames,
                                        accumulative_augmentation=accumulative_augmentation
                                        )
                            d.process()
                            # wait for cpu cores to finish

                            split_data()
                            FRAMES_PER_VIDEO = num_of_frames
                            results = {}
                            accuracy_data, max_accuracy, average_accuracy = main()
                            results['accuracy'] = accuracy_data
                            results['max_accuracy'] = max_accuracy
                            results['average_accuracy'] = average_accuracy
                            results['resize_values'] = resize_values
                            results['rotate_times'] = rotate_times
                            results['aspect_ratio_times'] = aspect_ratio_times
                            results['non_moving_frames_threshold'] = non_moving_frames_threshold
                            results['num_of_frames'] = num_of_frames
                            results['accumulative_augmentation'] = accumulative_augmentation
                            # save to text file
                            with open('results.txt', 'a') as f:
                                f.write(str(results) + '\n')

                            # append_results_to_excel(results)
