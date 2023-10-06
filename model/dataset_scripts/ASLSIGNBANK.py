import requests
from bs4 import BeautifulSoup
import os
import urllib.request
import tqdm

max_video = 3083
BASE_URL = "https://aslsignbank.haskins.yale.edu"

URL = BASE_URL+"/dictionary/gloss/3083.html"

def download_video(video_id,output_folder):
    URL = "https://aslsignbank.haskins.yale.edu/dictionary/gloss/" + str(video_id) + ".html"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    video_container_id ="videoplayer"
    video_container = soup.find(id=video_container_id)
    #get video url from video container 
    video_url = BASE_URL + video_container.attrs['src']
    
    #get video name from video container
    video_name = video_container.attrs['src'].split('/')[-1]
    gloss = soup.find(id="annotation_idgloss_en_US").get_text().lower()
    output_folder = os.path.join(output_folder,gloss)
    #download video
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    urllib.request.urlretrieve(video_url, os.path.join(output_folder,video_name))

    


if __name__ == "__main__":
    with tqdm.tqdm(total=max_video) as pbar:
        for i in range(0,max_video):
            try:
                download_video(i,'ASL_Videos')
            except:
                pbar.update(1)
                pass
                
            pbar.update(1)

    