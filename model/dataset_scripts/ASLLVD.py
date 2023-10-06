import json

import multiprocessing

import os

import requests

from tqdm import tqdm

import cv2


def download_video(url, path, filename):

    try:
        # Send an HTTP GET request to the URL and save the response to a file

        response = requests.get(url, stream=True)

        file_path = os.path.join(path, filename)

        if not os.path.exists(path):

            os.makedirs(path)

        else:

            if os.path.exists(file_path):

                return

        with open(file_path, 'wb') as file:

            for data in response.iter_content(1024):

                file.write(data)
    except Exception as e:
        print(e)


def download_videos(videos):
    # Download the videos in the list concurrently
    with multiprocessing.Pool(8) as p:
        p.starmap(download_video, videos)


def start_download():
    # Define the videos list
    videos = []
    urls = set()
    # Loop through the JSON file and download the videos
    with open('asllvd.json') as json_file:
        data = json.load(json_file)
        # Get the total number of videos
        for key in data.keys():
            # Loop on the videos of each key
            for video in data[key]:
                url = video[2]
                urls.add(url)
        print(len(urls))
        with tqdm(total=len(urls)) as progress:
            for url in urls:
                video_name = url.split('/')[-2] + "_" + url.split('/')[-1]
                # check if the video is already downloaded
                if os.path.exists(os.path.join("ASLLVD_DATASET", video_name)):
                    progress.update(1)
                    continue

                # check if it exists in a temp folder

                if os.path.exists(os.path.join("/root/Desktop/videos/", video_name)):

                    progress.update(1)

                    continue

                videos.append((url, "ASLLVD_DATASET", video_name))

                if len(videos) == 8:

                    download_videos(videos)

                    videos = []

                    progress.update(8)

            if len(videos) > 0:

                download_videos(videos)

                progress.update(len(videos))


def cut_videos():

    with open('asllvd.json') as json_file:

        data = json.load(json_file)

        # Get the total number of videos

        total_videos = sum(len(videos) for videos in data.values())

        transformed_data = {}

        for tag, tag_data in data.items():

            for entry in tag_data:

                url = entry[2]

                if url in transformed_data:

                    transformed_data[url].append([tag, entry[0], entry[1]])

                else:

                    transformed_data[url] = [[tag, entry[0], entry[1]]]

        # Use tqdm to create a progress bar

        with tqdm(total=total_videos) as progress:

            # Loop on the keys of the JSON file

            for url in transformed_data.keys():

                # Loop on the videos of each key

                videos = transformed_data[url]

                video_name = url.split('/')[-2] + "_" + url.split('/')[-1]

                video_path = os.path.join("ASLLVD_DATASET", video_name)

                download_video(url, "ASLLVD_DATASET", video_name)

                for video in videos:

                    action = video[0]

                    # Get the video name

                    # Get the start and end time of the video

                    start_time = video[1]

                    end_time = video[2]

                    # Open the video

                    cap = cv2.VideoCapture(video_path)

                    # Get the FPS of the video

                    fps = cap.get(cv2.CAP_PROP_FPS)

                    # Calculate the start and end frame

                    start_frame = max(int(start_time)-5, 0)

                    end_frame = min(int(end_time), int(
                        cap.get(cv2.CAP_PROP_FRAME_COUNT)))

                    # Set the current frame to the start frame

                    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

                    # Get the width and height of the video

                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                    # Define the codec and create VideoWriter object

                    # lower case the action name

                    action = action.lower()

                    action = action.split("/")[-1]

                    output_path = os.path.join(
                        "ASLLVD_DATASET_CUT", action, video_name)

                    if not os.path.exists(os.path.join("ASLLVD_DATASET_CUT", action)):

                        os.makedirs(os.path.join("ASLLVD_DATASET_CUT", action))

                    fourcc = cv2.VideoWriter_fourcc(*'XVID')

                    out = cv2.VideoWriter(
                        output_path, fourcc, fps, (width, height))

                    # Loop through the frames

                    while cap.isOpened():

                        # Read the frame

                        ret, frame = cap.read()

                        # Check if the frame is None

                        if frame is None:

                            break

                        # Write the frame to the output video

                        out.write(frame)

                        # Check if the current frame is the end frame

                        if cap.get(cv2.CAP_PROP_POS_FRAMES) == end_frame:

                            break

                    # Release the VideoCapture and VideoWriter objects

                    cap.release()

                    out.release()

                    # Update the progress bar

                    progress.update(1)

                # Delete the original video

                os.remove(video_path)


if __name__ == "__main__":

    # start_download()

    cut_videos()

    # #open a json file and read it

    # with open('MSASL_val.json') as json_file:

    #     data = json.load(json_file)

    #     # Get the total number of videos

    #     url_per_text = {}

    #     for video in data:

    #         text = video["clean_text"]

    #         url = video["url"]

    #         if text in url_per_text:

    #             url_per_text[text].append(url)

    #         else:

    #             url_per_text[text] = [url]

    #     #print the number of videos for each text

    #     for key in url_per_text.keys():

    #         print(key, len(url_per_text[key]))
