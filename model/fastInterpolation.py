import cv2
import os


def adjust_video_total_frames_using_interpolation(video_path, output_path, num_frames):
    # read the video
    cap = cv2.VideoCapture(video_path)
    # get the total number of frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # get the width and height of the video
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
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
            print("Can't receive frame. Retrying ...")
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


if __name__ == '__main__':
    mainFolder = os.path.join('all_vids')
    folderPath = mainFolder
    regulatedFolderPath = os.path.join('all_vids_regulated')
    for action in os.listdir(folderPath):

        actionPath = os.path.join(folderPath, action)

        regulatedActionPath = os.path.join(regulatedFolderPath,  action)

        if not os.path.exists(regulatedActionPath):

            os.makedirs(regulatedActionPath)

        # loop through all videos in the action folder

        for video in os.listdir(actionPath):

            videoPath = os.path.join(actionPath, video)

            regulatedVideoPath = os.path.join(regulatedActionPath,  video)

            if not os.path.exists(regulatedVideoPath):

                print('Regulating video: ' + video)

                adjust_video_total_frames_using_interpolation(
                    videoPath, regulatedVideoPath, 15)

    print('Done with all folders')
