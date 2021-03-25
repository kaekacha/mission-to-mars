# Importing dependencies
import pymongo
from bs4 import BeautifulSoup as bs
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests

def scrape():

    # Scraping for the latest Mars-related headline and associated teaser
    #scrape the website https://mars.nasa.gov/news/ to scrape data on most recent headline and teaser associated with the headline.
    url = 'https://mars.nasa.gov/news/'
    response = requests.get(url)
    bs_news= bs(response.text, 'html.parser')

    #print(bs_news.prettify())
    title_news = bs_news.find(class_='content_title').text.strip()
    teaser_news = bs_news.find(class_='rollover_description').text.strip()

    # Scraping for the for the featured Mars image of the day
    #Next, we will use splinter to scrape the featured image on the website https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html

    #setup splinter
    executable_path={'executable_path': ChromeDriverManager().install()}
    browser=Browser('chrome',**executable_path, headless=False)

    #below, the url is separated into two parts in order to concatonate the "url" with the image path later.
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/'
    index_url='index.html'
    browser.visit(url+index_url)

    #after inspecting the page, we see that the featured image is in the class "headerimage fade-in" as a src link within this img tag.
    #use beautifulSoup to scrape the image link
    html=browser.html
    ftimg_soup = bs(html, 'html.parser')
    ftimg_url = ftimg_soup.find('img',class_="headerimage fade-in")
    ftimg_url=ftimg_url.attrs['src'] #learned about the attrs function here: https://towardsdatascience.com/soup-of-the-day-97d71e6c07ec

    #concatonate the image link with the earlier url link
    featured_image_url=url+ftimg_url
    browser.visit(featured_image_url)

    #quit the browser session for splinter.
    browser.quit()

    # Scraping for the images of Mars' four hemispheres
    #setup splinter again
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    #below, the url is separated into two parts in order to concatonate the "url" with the image path later.
    url='https://astrogeology.usgs.gov/'
    hems_url = 'search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url+hems_url)

    #inspected the website to see that all the info we need for each of the hemsipheres (the link as well as the name) is located within the class "item".
    html = browser.html
    soup = bs(html, 'html.parser')
    sidebar = soup.find_all(class_='item')

    #create a url list to get the urls to the image and name for each of hte four hemispheres (within each of the "item" classes)
    url_list=[]
    for x in sidebar:
        hem_url = x.find('a')['href']
        url_list.append(url+hem_url)

    #we then create a list to visit each of the urls from the list created above, and in this list we are collecting each of the image paths for each of the four hemisphere urls and storing those image paths into a list.
    hemimgs_list=[]
    for x in url_list:
        browser.visit(x)
        html = browser.html
        soup = bs(html, 'html.parser')
        sidebar=soup.find('li')
        categories = sidebar.find('a')['href']
        hemimgs_list.append(categories)

    #we then create a list to visit each of the urls from the url_list created above, and in this list we are collecting each of the hemisphere titles for each of the four hemisphere urls (removing the extra space and word "Enhanced") and storing those titles into a list.
    hemtitles_list=[]
    for x in url_list:
        browser.visit(x)
        html = browser.html
        soup = bs(html, 'html.parser')
        sidebar3=soup.find('h2',class_="title")
        hem_title=sidebar3.text.strip().replace(' Enhanced','') #use this replace code to remove the " Enhanced" part of the hemisphere title.
        hemtitles_list.append(hem_title)

    #finally, create a dictionary with title and img_url keys. Utilized documentation here: https://www.geeksforgeeks.org/python-convert-two-lists-into-a-dictionary/
    hemisphere_image_urls=[]
    for i in range(len(hemimgs_list)):
        hemisphere_image_urls.append({"title":hemtitles_list[i], "img_url":hemimgs_list[i]})

    #quit this instance of the browser
    browser.quit()

    mars_data = {
        'news_title': title_news,
        'news_p': teaser_news,
        'featured_image_url': featured_image_url,
        'html_table': html,
        'hemisphere_image_urls': hemisphere_image_urls
        }

    return mars_data    

# Scraping for Mars facts
def scrape_table():
    #Found documentation to create a separate function to scrape the table of Mars facts
    facts_url="https://space-facts.com/mars/"
    tables=pd.read_html(facts_url)
    #after inspect the tables, we see that the first table (index=0) contains the information we'd like to include in our site
    df=tables[0]
    df.columns=['Variable', 'Mars Data'] #used this code to change the indexed columns: https://note.nkmk.me/en/python-pandas-dataframe-rename/
    df.set_index('Variable', inplace=True)
    
    return df