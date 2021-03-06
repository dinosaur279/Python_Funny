# -*- coding: utf-8 -*-
from threading import Thread
from TikiTarget import TikiTarget
from TikiItem import TikiItem
from TikiHelper import *
from bs4 import BeautifulSoup
import requests
import time


class TikiHunterThread(Thread):
    MAX_PAGE = 1

    def __init__(self, target):
        Thread.__init__(self)
        self.target = target
        self.bestItem = None
        self.name = target.getKeyword()
    
    def __findBestItem(self):
        # for to MAX_PAGE
        headers = {
            'User-Agent': 'Go to | https://www.whatismybrowser.com/detect/what-is-my-user-agent |, Get your User-Agent and paste here'}
        searchLink = self.target.getSearchLink(1)
        response = requests.get(searchLink, headers=headers)
        # response = requests.get(searchLink)

        if response.status_code != 200:
            return


        bsoup = BeautifulSoup(response.text, "lxml")
        # <a> class = search-a-product-item
        listElement = bsoup.findAll("a", {"class": "product-item"})

        i = 0
        for e in listElement:
            # print(str(i) + " : ")

            if(e.get_text().find("Đã hết hàng") >= 0 or e.get_text().find("Ngừng kinh doanh") >= 0):
                # print("=========== Đã hết hàng ======")
                continue

            newItem = TikiItem()

            newItem.title = (e.find("div", {"class": "name"}).text)
            newItem.url = "https://tiki.vn" + e.get("href")
            span = e.find("div", {"class": "price-discount__price"})
            newItem.price = convertToPrice(span.text)


            span = e.find("div", {"class":"price-discount__discount"})
            if(span != None):
                newItem.discount = convertToDiscount(span.text)

            if(newItem.isValidItem(self.target.patterns)):
                # print(newItem.info())
                if(self.bestItem == None):
                    self.bestItem = newItem
                else:
                    if(newItem.price < self.bestItem.price):
                        self.bestItem = newItem
            i = i + 1

        # print("Best Item: " + self.name)
        # if(self.bestItem != None):
        #     print(self.bestItem.info())
        # print("--------------")
        

    def run(self):
        print("Start Thread: " + self.name)
        while True:
            try:
                self.__findBestItem()
            except:
                print("Something Wrong!!!!")
            time.sleep(2)
        print("End Thread: " + self.name)
