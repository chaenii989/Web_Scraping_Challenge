import pandas as pd
from splinter import Browser
from bs4 import BeautifulSoup as bs
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

def init_browser():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    news_title, news_paragraph = mars_news(browser)

    data = {
        "news_title" : news_title,
        "news_paragraph" : news_paragraph,
        "featured_image" : featured_image(browser),
        "facts" : mars_facts(),
        "hemispheres" : hemisphere(browser),
        "last_modified" : dt.datetime.now()
    }

    browser.quit()
    return data


# NASA Mars News

def mars_news(browser):
    # Visit the NASA Mars News Site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    browser.is_element_present_by_css('div.list_text', wait_time=0.5)
    
    html = browser.html
    soup = bs(html, 'html.parser')

    # Try/except for error handling
    try:
        slide_element = soup.select_one('div.list_text')
        # Scrape the Latest News Title
        news_title = slide_element.find('div', class_='content_title').get_text()

        news_paragraph = slide_element.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None
    return news_title, news_paragraph

# JPL Mars Space Images - Featured Image

def featured_image(browser):
    # Visit the NASA JPL (Jet Propulsion Laboratory) Site
    url = 'https://spaceimages-mars.com/'
    browser.visit(url)

    full_image_button = browser.find_by_tag('button')[1]
    full_image_button.click()

    html = browser.html
    img_soup = bs(html, 'html.parser')

    # Try/except for error handling
    try:
        # Find the image url for the current Featured Mars Image
        img_url = img_soup.find('img', class_ = 'fancybox-image').get('src')
    except AttributeError:
        return None 

   # Use Base URL to Create Absolute URL
    featured_image_url = f"https://spaceimages-mars.com/{img_url}"
    return featured_image_url


# Mars Facts

def mars_facts():
    try:
        table_df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    # Assign columns and set index of table_df
    table_df.columns=['Description','Mars','Earth']
    table_df.set_index('Description', inplace=True)

    return table_df.to_html(classes="table table-striped")


# Mars Hemispheres

def hemisphere(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    
    html = browser.html
    hemi_soup = bs(html, 'html.parser')

    hemisphere_image_urls = []
    # Get a List of All the Hemispheres
    links = browser.find_by_css("a.product-item img")
    for item in range(len(links)):
        
        
        # Find Element on Each Loop to Avoid a Stale Element Exception
        browser.find_by_css("a.product-item img")[item].click()
        hemisphere_data = scrape_hemisphere(browser.html)

        hemisphere_data['img_url'] = url +hemisphere_data['img_url']
        
        # Append Hemisphere Object to List
        hemisphere_image_urls.append(hemisphere_data)
        browser.back()
        
    return hemisphere_image_urls


def scrape_hemisphere(html_text):
    hemisphere_soup = bs(html_text, "html.parser")
    try: 
        title_element = hemisphere_soup.find("h2", class_="title").get_text()
        sample_element = hemisphere_soup.find("a", text="Sample").get("href")
    except AttributeError:
        title_element = None
        sample_element = None 
    hemisphere = {
        "title": title_element,
        "img_url": sample_element
    }
    return hemisphere




if __name__ == "__main__":
    print(init_browser())

