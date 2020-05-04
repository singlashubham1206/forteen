from django.shortcuts import render
from django.http import HttpResponse

# import required packages
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.support import expected_conditions as EC
from pytube import YouTube
import pandas as pd
import time
import re

# Create your views here.
def greetings(request):
    res = render(request,'yt_scrapper/home.html')
    return res

def search(request):
    if request.method == 'POST':
        # on the basis of search text...search on youtube
        search_text = request.POST['search_text']
        url = "https://www.youtube.com/results?search_query="+search_text.replace(' ','+')
        print(search_text)
        print(url)

        # put that searching url into chrome driver with the help of selenium
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get(url)
        time.sleep(5)

        # get channel details
        channel_section = driver.find_element(By.ID,"content-section")
        channel_details = channel_section.text.split("\n")
        channel_name = channel_details[0]
        channel_subscribers = channel_details[1].split(" ")[0]
        channel_desc = channel_details[2]
        no_of_videos = channel_details[1].split(" ")[1][12:]

        # display channel details
        print("Channel name : ",channel_name)
        print("Channel subscribers : ",channel_subscribers)
        print("Number of videos : ",no_of_videos)
        print("Channel Description : ",channel_desc)

        avtar = channel_section.find_element(By.XPATH,"//*[@id='avatar-section']/a")
        channel_url = avtar.get_attribute("href")
        img_section = channel_section.find_element(By.ID,"img")
        channel_avtar_url = img_section.get_attribute("src")

        print("channal_url : ",channel_url)
        print("channel_avtar_url :",channel_avtar_url)

        driver.quit()

        res = render(request,'yt_scrapper/home.html',{"channel_name":channel_name,"channel_subscribers":channel_subscribers,"no_of_videos":no_of_videos,"channel_desc":channel_desc,"channel_avtar_url":channel_avtar_url,"channel_url":channel_url})
        return res

def top_videos(request):
    if request.method == 'POST':
        channel_avtar_url = request.POST['channel_avtar_url']
        channel_name = request.POST['channel_name']
        channel_subscribers = request.POST['channel_subscribers']
        no_of_videos = request.POST['no_of_videos']
        channel_desc = request.POST['channel_desc']
        channel_url = request.POST['channel_url']

        print("channel_avtar_url_inside_top_videos : ",channel_avtar_url)
        print("channel_name_inside_top_videos : ",channel_name)
        print("channel_subscribers_inside_top_videos : ",channel_subscribers)
        print("no_of_videos_inside_top_videos : ",no_of_videos)
        print("channel_desc_inside_top_videos : ",channel_desc)
        print("channel_url_inside_top_videos : ",channel_url)

        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get(channel_url)
        time.sleep(5)
        driver.find_element(By.XPATH,"//*[@id='tabsContent']/paper-tab[2]/div").click()
        time.sleep(5)

        if ',' not in no_of_videos:
            no_of_videos = int(no_of_videos)
        else:
            no_of_videos = int(no_of_videos[:no_of_videos.index(',')])*1000 + int(no_of_videos[no_of_videos.index(',')+1:])

        count = 1
        while True:
            driver.execute_script("window.scrollBy(0,1000)","")
            time.sleep(3)
            video_sections = driver.find_elements(By.ID,"video-title")
            print(len(video_sections))
            print(count)
            count = count+1
            if len(video_sections) >= no_of_videos-4:
                break

        video_links = []

        for i in video_sections:
            video_links.append(i.get_attribute("href"))

        print(len(video_links))

        video_titles = []
        video_lengths = []
        video_descs = []
        video_views = []
        video_ratings = []
        video_age_restricted = []
        video_thumbnail_urls = []

        flag = 1
        for i in video_links:
            yt = YouTube(i)
            video_titles.append(yt.title)
            video_lengths.append(yt.length)
            video_descs.append(yt.description)
            video_views.append(yt.views)
            video_ratings.append(yt.rating)
            video_age_restricted.append(yt.age_restricted)
            video_thumbnail_urls.append(yt.thumbnail_url)
            print(flag)
            flag = flag + 1

        df = pd.DataFrame(list(zip(video_titles, video_lengths,video_descs,video_views,video_ratings,video_age_restricted,video_links,video_thumbnail_urls)),
               columns =['video_title', 'video_length','video_desc','video_views','video_ratings','video_age_restricted','video_link','video_thumbnail_urls'])

        final = df.sort_values(by=['video_views','video_ratings'],ascending=False).head(10)
        print(final)

    res = render(request,'yt_scrapper/home.html',{"data":final,"flag":flag,"channel_name":channel_name,"channel_subscribers":channel_subscribers,"no_of_videos":no_of_videos,"channel_desc":channel_desc,"channel_avtar_url":channel_avtar_url})
    return res
