import cv2
import numpy as np
import os
from vidaug import augmentors as va
from PIL import Image
import random
import uuid
import istarmap
import multiprocessing
from tqdm import tqdm
import gc


class DataAugmentation:

    ''' This class is used to augment the data by applying random translations, center cropping, and random resizing to the videos '''

    def __init__(self, videos_path, output_path):
        self.videos_paths = videos_path
        self.output_folder_name = output_path

    def convert_to_list(self, video):
        frames = []
        while True:
            ret, frame = video.read()
            if not ret:
                break
            frames.append(frame)
        return frames

    def convert_to_pil(self, video_frames):
        # video is a cv2 video
        # Read video frames using OpenCV and convert to PIL images
        frames = [Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                  for frame in video_frames]
        return frames

    def convert_to_cv2(self, pil_frames):
        # Convert PIL images to OpenCV images
        cv2_frames = [cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
                      for frame in pil_frames]
        return cv2_frames

    def random_translation(self, video):
        aug = va.RandomTranslate(100, 100)
        pil_frames = self.convert_to_pil(video)
        translated_frames = aug(pil_frames)
        translated_video = self.convert_to_cv2(translated_frames)
        return translated_video

    def center_crop(self, video, crop_percentage=0.75):
        # Calculate crop dimensions
        height, width, layers = video[0].shape
        crop_width = int(width * crop_percentage)
        crop_height = int(height * crop_percentage)

        aug = va.CenterCrop((crop_height, crop_width))
        pil_frames = self.convert_to_pil(video)
        cropped_frames = aug(pil_frames)
        cropped_video = self.convert_to_cv2(cropped_frames)
        return cropped_video

    def random_resize(self, video, scale_range=(0.2, 1.2), aspect_ratio_range=(0.1, 0.9)):
        # Get video properties
        height, width, layers = video[0].shape
        num_frames = len(video)

        # Randomly choose scale and aspect ratio
        scale = random.uniform(scale_range[0], scale_range[1])
        aspect_ratio = random.uniform(
            aspect_ratio_range[0], aspect_ratio_range[1])

        # Calculate new dimensions
        new_width = int(width * scale * aspect_ratio)
        new_height = int(height * scale / aspect_ratio)

        # Resize video
        resized_video = []
        for i in range(num_frames):
            frame = video[i]

            resized_frame = cv2.resize(frame, (new_width, new_height))
            resized_video.append(resized_frame)

        return resized_video

    def random_sheer(self, video, intensity=0.15):
        height, width, layers = video[0].shape
        num_frames = len(video)

        # Randomly choose scale and aspect ratio
        shear_x = random.uniform(0.1, intensity)
        shear_y = random.uniform(0.1, intensity)

        # Calculate new dimensions
        new_width = int(width * (1 + shear_x))
        new_height = int(height * (1 + shear_y))

        # Resize video
        sheared_video = []
        for i in range(num_frames):
            frame = video[i]
            sheared_frame = cv2.warpAffine(frame, np.float32(
                [[1, shear_x, 0], [shear_y, 1, 0]]), (new_width, new_height))
            sheared_video.append(sheared_frame)

        return sheared_video

    def piecewise_affine(self, video):
        aug = va.PiecewiseAffineTransform(
            displacement=16, displacement_kernel=24,
            displacement_magnification=1)
        pil_frames = self.convert_to_pil(video)
        transformed_frames = aug(pil_frames)
        return self.convert_to_cv2(transformed_frames)

    def rotate_image(self, image, angle):
        # Rotate an image by a given angle.
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
        result = cv2.warpAffine(
            image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
        return result

    def rotate_video_frames(self, video, angle=8):
        # rotate each frame of the video by a random angle
        rotated_video = []
        num_frames = len(video)
        for i in range(num_frames):
            frame = video[i]
            rotated_frame = self.rotate_image(frame, angle)
            rotated_video.append(rotated_frame)

        return rotated_video

    def get_augmented_videos(self, video):
        # Apply a random combination of data augmentation techniques to the video.
        onetime_augmentation_techniques = [
            self.random_translation,
            self.piecewise_affine,
            self.random_resize,
            self.random_sheer,
            self.center_crop,
            self.rotate_video_frames,
        ]
        augmented_videos = [video]
        for augmentation_technique in onetime_augmentation_techniques:
            augmented_videos.append(augmentation_technique(video))

        second_time_augmentation_techniques = [

        ]
        all_augmented_videos = []

        # for each augmented video, we apply the second time augmentation techniques
        for augmented_video in augmented_videos:
            all_augmented_videos.append(augmented_video)
            for augmentation_technique in second_time_augmentation_techniques:
                # show type of augmented_video
                new_augmented_video = augmentation_technique(augmented_video)
                all_augmented_videos.append(new_augmented_video)

        return all_augmented_videos

    def save_video(self, video, out_path):
        # Save the video to the specified path.
        # Get video properties
        height, width, layers = video[0].shape
        num_frames = len(video)
        # check if the output folder exists
        output_folder = os.path.dirname(out_path)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)
        # Create a VideoWriter object
        out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(
            *'mp4v'), 30, (width, height))
        # Write each frame to the output video
        for i in range(num_frames):
            out.write(video[i])
        # Release the VideoWriter object
        out.release()

    def augment_video(self, video_file, output_folder_name, get_augmented_videos, save_video, convert_to_list):
        # out_path will be same as video_file but with changing the first folder name
        out_path = video_file.split(os.sep)
        out_path[0] = output_folder_name
        # remove the file name
        out_path = out_path[:-1]
        out_path = '/'.join(out_path)

        # if os.path.exists(out_path):
        #     # check if the folder has less than 10 videos
        #     if len(os.listdir(out_path)) < 10:
        #         return

        # Augment a single video.
        video = cv2.VideoCapture(video_file)
        # convert it to a list of frames
        video = convert_to_list(video)
        augmented_videos = get_augmented_videos(video)
        print(output_folder_name, len(augmented_videos))

        for i in range(len(augmented_videos)):
            video_name = video_file.split(os.sep)[-1]
            # add uuid to the end of the video name before the .mp4
            video_name = video_name.split(
                '.')[0] + '#' + str(uuid.uuid4()) + '.mp4'

            save_video(augmented_videos[i], out_path + os.sep + video_name)

        del augmented_videos

    def augment_videos(self):
        # Augment all of the videos in the specified path.
        inputs = [(video_file, self.output_folder_name, self.get_augmented_videos,
                   self.save_video, self.convert_to_list) for video_file in self.videos_paths]
        with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
            with tqdm(total=len(self.videos_paths), desc='Increasing dataset size') as pbar:
                for _ in p.istarmap(self.augment_video, inputs):
                    pbar.update()
