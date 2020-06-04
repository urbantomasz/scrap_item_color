import requests
import csv
from bs4 import BeautifulSoup
from datetime import date
from urllib.request import urlopen
import cv2
import numpy as np
from matplotlib import pyplot as plt
import re 

"""
def cropp_image_center(image, crop_w, crop_h):
    h = image.shape[0]
    w = image.shape[1]
    cropped_img = img.crop(((w-50)//2, (h-50)//2, (w+50)//2, (h+50)//2))
"""

def url_to_image(url, readFlag=cv2.IMREAD_COLOR):
    resp = urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, readFlag)
    image = image[100:175, 110:200]
    return image

def show_image(image):
    image = image[:,:,::-1]
    plt.imshow(image)
    
    
def get_dominant_color(image):
    
    # usniecie mocno bialych pikseli
    mask = np.logical_and.reduce((image[:,:,0]<240,image[:,:,1]<240,image[:,:,2]<240))
    image = image[mask] 
    array = image.reshape(-1,image.shape[-1])
    colors, count = np.unique(array, axis=0, return_counts=True)
  
    return colors[count.argmax()]

def closest_target_color(rgb_color):
    
    TARGET_COLORS = {"Ciemny":(0, 0, 0), "Jasny":(255, 255, 255)}
    color_difference = lambda color1, color2: sum([abs(component1-component2) for component1, component2 in zip(color1, color2)])
    differences = [[color_difference(rgb_color, target_value), target_name] for target_name, target_value in TARGET_COLORS.items()]
    differences.sort()  # sorted by the first element of inner lists
    color_name = differences[0][1]

    return color_name

def generate_file_name():
    today = date.today()
    today_formated = today.strftime("%d_%m_%Y")
    return "scrap_results_" + today_formated + ".csv"

def scrape_data(url, csv_file_name):
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    result_divs = soup.find_all('article', attrs={"class": "category-products__item"})
  

    with open(csv_file_name, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['href','kod','kolor'])
        
        for result_div in result_divs:
            
            code = re.sub("\D", "", result_div.find('div', {'class':'product__code'}).text.strip()) 
            thumbnail_container = result_div.find('div', {'class':'thumbnail-container'})
            src = thumbnail_container.find('img')['src']
            href = thumbnail_container.find('a')['href']
            image = url_to_image(src)
            dominant_color = get_dominant_color(image)
            dominant_color_text = closest_target_color(dominant_color)

            writer.writerow([href,code,dominant_color_text])

if __name__ == "__main__":
    scrape_data("https://www.montersi.pl/kamery-tubowe-ip?resultsPerPage=150", generate_file_name())
