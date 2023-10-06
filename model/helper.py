import os
import shutil
import random
from tqdm import tqdm
from mediapipeHelper import *

VIDEO_NAME_SEPARATOR = '$separator$'


def split_arr(dataset: set,
              train_ratio: float,
              val_ratio: float) -> tuple:
    """
    Split a given dataset into three subsets: train, validation, and test.

    Args:
    dataset (set): The dataset to be split.
    train_ratio (float): The ratio of data to use for the training set.
    val_ratio (float): The ratio of data to use for the validation set.

    Returns:
    A tuple containing three sets: train set, validation set, and test set.
    """
    if len(dataset) < 3:
        raise ValueError('The dataset must have at least 3 elements.')

    # Calculate the size of each subset based on the given ratios
    data_size = len(dataset)
    train_size = int(train_ratio * data_size)
    val_size = int(val_ratio * data_size)
    test_size = data_size - train_size - val_size

    # Randomly shuffle the dataset
    random.seed(42)
    # random sample with seed 42
    sorted_data = sorted(dataset)
    shuffled_data = random.sample(sorted_data, len(sorted_data))

    # check if the val and test sets are empty
    if val_size == 0:
        val_size = 1
    if test_size == 0:
        test_size = 1

    train_size = data_size - val_size - test_size

    # Split the shuffled dataset into train, validation, and test sets
    train_set = set(shuffled_data[:train_size])
    val_set = set(shuffled_data[train_size: train_size + val_size])
    test_set = set(shuffled_data[train_size + val_size:])

    return train_set, val_set, test_set


def split_data(limit=500,
               min_videos_per_action=5):
    MAIN_DATA_FOLDER = 'all_vids'
    # count the number of videos that are greater than min_videos_per_action
    number_of_videos = [f for f in os.listdir(
        MAIN_DATA_FOLDER) if len(os.listdir(os.path.join(MAIN_DATA_FOLDER, f))) >= min_videos_per_action]
    pbar = tqdm(total=min(len(number_of_videos), limit),
                desc='Generating test and val data')
    words_folder = os.listdir(MAIN_DATA_FOLDER)
    # sort the words folder by the folder that has the most videos
    words_folder.sort(key=lambda x: len(os.listdir(
        os.path.join(MAIN_DATA_FOLDER, x))), reverse=True)
    for word_folder in words_folder:
        if limit == 0:
            break
        action_path = os.path.join(MAIN_DATA_FOLDER, word_folder)
        number_of_videos = len(os.listdir(action_path))
        if number_of_videos < min_videos_per_action:
            continue
        limit -= 1

        val_percent = 0.10
        train_percent = 0.65

        # remove the  _rotated_ and  _resized_x.xx  from the video file names
        # insert the new video file names in a set
        filenames = set()
        for video_folder in os.listdir(action_path):
            # filename = video_folder.split(VIDEO_NAME_SEPARATOR)[0] # no need since splitting is done before augmentation
            filenames.add(video_folder)

        # sort
        filenames = set(sorted(filenames))
        # split the set into two sets
        train_filenames, val_filenames, test_filenames = split_arr(
            filenames, train_percent, val_percent)

        # create the test folder
        test_folder = os.path.join('Test', word_folder)
        if not os.path.exists(test_folder):
            os.makedirs(test_folder)
        # create the val folder
        val_folder = os.path.join('Val', word_folder)
        if not os.path.exists(val_folder):
            os.makedirs(val_folder)
        # create the train folder
        train_folder = os.path.join('Train_unaugmented', word_folder)
        if not os.path.exists(train_folder):
            os.makedirs(train_folder)

        for video_folder in os.listdir(action_path):
            # filename = video_folder.split(VIDEO_NAME_SEPARATOR)[0]
            filename = video_folder
            if filename in test_filenames:
                shutil.copy(os.path.join(action_path, video_folder),
                            os.path.join(test_folder, video_folder))
            elif filename in val_filenames:
                shutil.copy(os.path.join(action_path, video_folder),
                            os.path.join(val_folder, video_folder))
            elif filename in train_filenames:
                shutil.copy(os.path.join(action_path, video_folder),
                            os.path.join(train_folder, video_folder))
        pbar.update(1)


def get_all_vids_paths(folder_name):
    # get all the paths of the videos (.mp4) in folder or subfolders
    vids_paths = []
    for root, dirs, files in os.walk(folder_name):
        for file in files:
            if file.endswith('.mp4'):
                vids_paths.append(os.path.join(root, file))
    return vids_paths


if __name__ == '__main__':
    split_data()
    # videos = get_all_vids_paths('MSASL')
    # # calculate time taken to process all the videos
    # start = time.time()

    # remove_not_moving_frames(videos)
    # end = time.time()
    # print("Time taken to process all the videos: ", end - start)
