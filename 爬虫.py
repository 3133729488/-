import os
import csv
import time
import threading
import requests
from PIL import Image
import io
from selenium import webdriver
from selenium.webdriver.common.by import By

# 全局变量
stop_flag = False

def wait_for_enter():
    global stop_flag
    input("按下回车键停止爬取...")
    stop_flag = True

# 启动浏览器
browser = webdriver.Edge()

data = []

find = input("搜索内容：")
page_num = 1

# 创建一个文件夹
folder_name = "腾讯爬虫"
if not os.path.exists(folder_name):
    os.mkdir(folder_name)

# 创建一个用于保存图片的子文件夹
img_folder = os.path.join(folder_name, "图片")
if not os.path.exists(img_folder):
    os.mkdir(img_folder)

# 启动一个线程等待用户按下回车键停止爬取
thread = threading.Thread(target=wait_for_enter)
thread.start()

while not stop_flag:
    browser.get(f"https://new.qq.com/search?query={find}&page={page_num}")
    browser.implicitly_wait(5)

    # 截取网页元素，标题，简介，链接，图片
    titles = browser.find_elements(By.CLASS_NAME, "title")
    links = browser.find_elements(By.CSS_SELECTOR, "a.hover-link")
    images = browser.find_elements(By.TAG_NAME, "img")
    synopses = browser.find_elements(By.CLASS_NAME, "txt")

    if len(titles) == 0:
        print(f"第 {page_num} 页未找到内容，正在刷新页面...")
        browser.refresh()
        time.sleep(3)
        continue

    for index, title in enumerate(titles):
        title_text = title.text
        link = links[index].get_attribute('href')
        synopsis_text = synopses[index].text  # 获取对应索引的简介文本
        data.append([title_text, synopsis_text, link])  # 将标题、简介、链接添加到数据列表中

    # 遍历所有的图片元素，获取图片的链接，并下载到子文件夹中
    for index, image in enumerate(images):
        img_url = image.get_attribute("src")
        if img_url:
            # 使用requests.get()获取图片的二进制数据
            img_data = requests.get(img_url).content
            # 用PIL打开图片数据
            image = Image.open(io.BytesIO(img_data))
            # 命名图片
            img_name = f"image_{page_num}_{index}.jpg"
            # 生成图片的完整路径
            img_path = os.path.join(img_folder, img_name)
            with open(img_path, "wb") as f:
                f.write(img_data)
    
    page_num += 1

browser.quit()

# 将数据写入csv文件中，注意要加上文件夹的路径
csv_name = "腾讯爬虫.csv"
csv_path = os.path.join(folder_name, csv_name)
with open(csv_path, 'w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    writer.writerow(['标题', '简介', '链接'])
    writer.writerows(data)

print("我导完了")
