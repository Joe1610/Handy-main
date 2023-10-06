import json
import os
import shutil

# i have a folder called augmented_videos i want to select the top 50 action videos from it and put them in a folder called top_50_videos
# i want to do this by selecting the top 50 videos with the highest number of videos per action


def get_top_50_videos():
    # get all the videos in the augmented_videos folder
    vids_folder = 'all_vids_regulated_20'
    actions = os.listdir(vids_folder)

    # create a dictionary to store the number of videos per action
    actions_dict = {}

    # loop through the actions
    for action in actions:
        # get the number of videos per action
        num_videos = len(os.listdir(os.path.join(vids_folder, action)))
        # store the number of videos per action in the dictionary
        actions_dict[action] = num_videos

    # sort the dictionary by the number of videos per action
    sorted_actions_dict = dict(
        sorted(actions_dict.items(), key=lambda item: item[1], reverse=True))

    # get the top 50 actions
    top_50_actions = list(sorted_actions_dict.keys())[:50]

    # create a folder to store the top 50 videos
    if not os.path.exists('top_50_videos'):
        os.mkdir('top_50_videos')

    # copy them to the top_50_videos folder top_50_videos/action/video.mp4
    for action in top_50_actions:
        # get the videos in the action
        videos = os.listdir(os.path.join(vids_folder, action))
        # create a folder for the action in the top_50_videos folder
        if not os.path.exists(os.path.join('top_50_videos', action)):
            os.mkdir(os.path.join('top_50_videos', action))
        # copy the videos to the top_50_videos folder
        for video in videos:
            shutil.copy(os.path.join(vids_folder, action, video),
                        os.path.join('top_50_videos', action, video))

    print('done')


def delete_videos():
    # get all the videos in the augmented_videos folder
    vids_folder = 'MP_Test'
    actions = os.listdir(vids_folder)

    # create a dictionary to store the number of videos per action
    actions_dict = {}

    # loop through the actions
    for action in actions:
        # delete all files in the folder expect the first and last
        videos = os.listdir(os.path.join(vids_folder, action))
        for video in videos[1:-1]:
            os.remove(os.path.join(vids_folder, action, video))

    print('done')


# Example usage
input_file_path = 'Handy.json'
filter_file_path = 'label_map.json'
output_file_path = 'filtered.json'


def create_filtered_json(input_file_path, filter_file_path, output_file_path):
    with open(input_file_path, 'r') as input_file, open(filter_file_path, 'r') as filter_file:
        input_data = json.load(input_file)
        filter_data = json.load(filter_file)
        print(filter_data.values())
        filtered_data = {}
        for key in input_data:
            filtered_data[key] = [word for word in input_data[key]
                                  if word in filter_data.values()]
        with open(output_file_path, 'w') as output_file:
            json.dump(filtered_data, output_file)


if __name__ == '__main__':
    # delete_videos()
    create_filtered_json(input_file_path, filter_file_path, output_file_path)
