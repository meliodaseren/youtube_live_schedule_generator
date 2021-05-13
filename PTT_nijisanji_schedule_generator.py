#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from selenium import webdriver

driver = webdriver.Chrome()

if __name__ == '__main__':

    url = 'https://nijisanji.vtubervideo.net/lives'
    # url = 'https://nijisanji.vtubervideo.net/lives/schedules'
    # url = 'https://nijisanji-live.com/'

    driver.get(url)

    content = driver.find_elements_by_xpath('//*[@id="movie_player"]/div[3]/div[2]/div/a')
    for i in content:
        print(f'content: {i.text}')

    driver.close()

    # r = requests.get(url)
    # print(f'Status code: {r.status_code}')
    # if r.status_code == requests.codes.ok:
    #    html_doc = r.textz
    #     soup = BeautifulSoup(html_doc, 'html.parser')
    #     items = soup.find_all('a', class_='ytp-title-link yt-uix-sessionlink')
    #     for i in items:
    #         print(i.text)

