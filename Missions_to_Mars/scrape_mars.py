from splinter import Browser
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import requests
import time
import pandas as pd
from splinter.exceptions import ElementDoesNotExist

def init_browser():
    #Define path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

#Function that will execute all scraping code and return one Python dictionary containing all of the scraped data
def scrape_all():
    mars_data={}
    browser = init_browser()
    
    # Visit NASA Mars News site to retrieve latest news
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    time.sleep(2)
    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")
    #Scrapping the container that has sought info
    result=soup.find_all('li',class_='slide')
    #Latest news is the first item in the list
    latest_news=result[0]
    #Scrapping news title and content
    latest_news_title=latest_news.find('h3').text
    latest_news_content=latest_news.find('div', class_='article_teaser_body').text
    
    
    #Visit JPL Mars Space Images site to find the image url for the current Featured Mars Image
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    time.sleep(2)
    full_image_button = browser.find_by_id("full_image")
    full_image_button.click()
    browser.is_element_present_by_text("more info", wait_time=1)
    more_info_element = browser.find_link_by_partial_text("more info")
    more_info_element.click()
    html = browser.html
    featured_image = bs(html, "html.parser")
    image_url=featured_image.find("img", class_="main_image")["src"]
    img_base_url= "https://www.jpl.nasa.gov" 
    featured_image_url=img_base_url + image_url
    
    #Mars Weather: Scraping latest weather tweet from Mars weather twitter account
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)
    html = browser.html
    weather_report = bs(html, "html.parser")
    #Scrapping the container that has sought info
    tweet=weather_report.find('div', class_='js-tweet-text-container')
    weather=tweet.p.text
    
    #To scrape the table containing facts about the planet from Mars Facts webpage
    url="https://space-facts.com/mars/"
    browser.visit(url)
    facts=pd.read_html(url)
    mars_facts=facts[0]
    # Rename columns
    mars_facts.columns = ['Description','Value']
    # Reset Index to description
    mars_facts = mars_facts.set_index('Description')
    # Use Pandas to convert the data to a HTML table string
    mars_facts = mars_facts.to_html()
  

    #Obtain high resolution images for each of Mar's hemispheres
    url="https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)
    html = browser.html
    soup = bs(html, 'html.parser')
    result=soup.find_all('div', class_='item')
    base_url='https://astrogeology.usgs.gov'
    #Define a list to store results of image titles and urls
    image_urls=[]
    for item in result:
        #get image titles, strip 'enhanced' from the end of each title
        titles=item.find('h3').text
        titles=titles.strip("Enhanced")
        #get relative links of images 
        link=item.find('a', class_="itemLink product-item")['href']
        #get absolute links of images 
        image_link=base_url+link
        #browse to page with link for full image
        browser = init_browser()
        browser.visit(image_link)
        time.sleep(2)
        html = browser.html
        soup = bs(html, "html.parser")
        records = soup.find("div", class_="downloads")
        #get links of full-sized images
        image_url = records.find("a")["href"]
        #append results into a list of dictionaries
        image_urls.append({"titles": titles, "image_url": image_url})

    # Store data in a dictionary
    mars_data = {
        "latest_news": latest_news_title,
        "latest_news_content": latest_news_content,
        "featured_image_url": featured_image_url,
        "weather": weather,
        "facts_html":mars_facts,
        #"facts_html":html_file,
        "image_urls":image_urls
    }

        
    # Close the browser after scraping
    browser.quit()
    # Return results
    return mars_data
if __name__ == "__main__":
        scrape_all()
# print(scrape_all())