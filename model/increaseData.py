import os
import random
import shutil
from natsort import natsorted
from tqdm import tqdm
import numpy as np


def split_val_to_val_and_train():
    # split the validation data into validation and test data
    # the validation data will be used to tra
    # the test data will be used to test the model
    parent_dir = os.path.join('MP_Val')
    try:
        shutil.rmtree('MP_Train')
    except:
        pass

    os.makedirs('MP_Train')
    for word_folder in os.listdir(parent_dir):
        # remove the  _rotated_ and  _resized_x.xx  from the video file names
        # insert the new video file names in a set
        filenames = set()
        for video_folder in os.listdir(os.path.join(parent_dir, word_folder)):
            filename = video_folder.split('_moving')[0]
            filenames.add(filename)

        # split the set into two sets
        train_percent = 0.8
        train_filenames = set(random.sample(filenames, int(
            len(filenames)*train_percent)))

        # create the test folder
        train_folder = os.path.join('MP_Train', word_folder)
        os.makedirs(train_folder, exist_ok=True)

        # move the test videos to the test folder

        for video in os.listdir(os.path.join(parent_dir, word_folder)):
            filename = video.split('_moving')[0]
            if filename in train_filenames:
                shutil.move(os.path.join(parent_dir, word_folder, video),
                            os.path.join(train_folder, video))


if __name__ == '__main__':
    split_val_to_val_and_train()
    # # create an np array that have first 63 values as 1 and last 63 values as -1
    # array = np.ones((63))
    # array = np.concatenate((array, -1*array))

    # os.makedirs('MP_Val/0', exist_ok=True)
    # os.makedirs('MP_Val/1', exist_ok=True)
    # np.save('MP_Val/0/array1.npy', array)
    # np.save('MP_Val/0/array2.npy', array)
    # # create an np array that have first 63 values as 2 and last 63 values as -2
    # array = np.ones((63))
    # array = np.concatenate((array*2, -1*array*2))

    # np.save('MP_Val/1/array1.npy', array)
    # np.save('MP_Val/1/array2.npy', array)
    # make_train_data_concat()
