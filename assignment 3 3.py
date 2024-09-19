#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Function to fetch the HTML content of a page
def fetch_html(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None

# Function to extract product details from the HTML content
def extract_product_details(soup):
    product_data = []
    for product in soup.find_all('div', {'data-component-type': 's-search-result'}):
        try:
            brand_name = product.find('span', {'class': 'a-size-base-plus'}).text.strip()
        except AttributeError:
            brand_name = "-"
        
        try:
            product_name = product.find('span', {'class': 'a-size-medium'}).text.strip()
        except AttributeError:
            product_name = "-"
        
        try:
            price = product.find('span', {'class': 'a-price-whole'}).text.strip()
        except AttributeError:
            price = "-"
        
        try:
            product_url = "https://www.amazon.in" + product.find('a', {'class': 'a-link-normal'})['href']
        except AttributeError:
            product_url = "-"

        # Since availability, return/exchange, and delivery info are not always on the product list page,
        # setting them as "-" for now.
        availability = "-"
        return_exchange = "-"
        delivery = "-"

        product_data.append([brand_name, product_name, price, return_exchange, delivery, availability, product_url])
    
    return product_data

# Function to scrape product information from Amazon search results
def scrape_amazon_products(query, pages=3):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    base_url = "https://www.amazon.in/s?k={}&page={}"
    all_products = []

    for page in range(1, pages+1):
        url = base_url.format(query, page)
        html = fetch_html(url, headers)
        
        if html is None:
            print(f"Failed to fetch page {page}. Skipping...")
            continue
        
        soup = BeautifulSoup(html, 'html.parser')
        products = extract_product_details(soup)
        if products:
            all_products.extend(products)
        else:
            print(f"No products found on page {page}. Ending scraping...")
            break

        time.sleep(1)  # Adding a delay between requests to avoid being blocked
    
    # Creating a DataFrame and saving to CSV
    df = pd.DataFrame(all_products, columns=["Brand Name", "Name of the Product", "Price", "Return/Exchange", "Expected Delivery", "Availability", "Product URL"])
    df.to_csv(f"{query}_products.csv", index=False)
    print(f"Scraped {len(all_products)} products. Data saved to {query}_products.csv")

# Input from user
search_query = input("Enter the product to search: ")
scrape_amazon_products(search_query)


# In[ ]:


pip install selenium pillow


# In[ ]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import requests
from PIL import Image
from io import BytesIO
import os

# Function to search and scrape images
def scrape_google_images(search_query, num_images=10):
    # Set up Selenium WebDriver (you can replace 'chrome' with the path to your WebDriver if needed)
    driver = webdriver.Chrome()  # Make sure you have the correct WebDriver in your PATH
    driver.get('https://images.google.com')
    
    # Find the search bar and enter the search query
    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)

    time.sleep(2)  # Wait for search results to load

    # Scroll to load more images
    images_scraped = 0
    images = []
    
    while images_scraped < num_images:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Give the page time to load
        
        image_elements = driver.find_elements(By.CSS_SELECTOR, 'img.Q4LuWd')
        for img_element in image_elements:
            img_url = img_element.get_attribute('src')
            if img_url and img_url.startswith('http') and images_scraped < num_images:
                images.append(img_url)
                images_scraped += 1
            if images_scraped >= num_images:
                break

    # Close the browser
    driver.quit()
    
    # Save images to disk
    save_images(search_query, images)

# Function to download and save images
def save_images(search_query, img_urls):
    search_query = search_query.replace(' ', '_')  # For naming folder
    if not os.path.exists(search_query):
        os.makedirs(search_query)
    
    for i, img_url in enumerate(img_urls):
        try:
            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content))
            img_path = os.path.join(search_query, f"{search_query}_{i+1}.jpg")
            img.save(img_path)
            print(f"Saved {img_path}")
        except Exception as e:
            print(f"Failed to save image {i+1} for {search_query}: {e}")

# List of search queries
search_queries = ['fruits', 'cars', 'Machine Learning', 'Guitar', 'Cakes']

# Scrape 10 images for each query
for query in search_queries:
    scrape_google_images(query, num_images=10)


# In[ ]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Function to fetch HTML content
def fetch_html(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None

# Function to extract smartphone details from the HTML content
def extract_smartphone_details(soup):
    smartphones = []
    
    # Loop through each smartphone in search results
    for product in soup.find_all('div', {'class': '_1AtVbE'}):
        try:
            name_section = product.find('a', {'class': '_1fQZEK'})
            product_url = "https://www.flipkart.com" + name_section['href']
            
            full_name = name_section.find('div', {'class': '_4rR01T'}).text.strip()
            brand_name = full_name.split()[0]  # Usually, brand name is the first word in the product name
            smartphone_name = ' '.join(full_name.split()[1:])  # Rest is the smartphone name
        except AttributeError:
            continue  # Skip if name or URL is missing

        # Extracting features and specifications
        try:
            specs = product.find('ul', {'class': '_1xgFaf'}).find_all('li')
            
            colour = "-"
            ram = "-"
            storage = "-"
            primary_camera = "-"
            secondary_camera = "-"
            display_size = "-"
            battery_capacity = "-"
            
            for spec in specs:
                text = spec.text
                if "GB RAM" in text:
                    ram = text.split()[0] + " GB"
                if "ROM" in text:
                    storage = text.split('|')[0].strip()
                    colour = text.split('|')[1].strip() if '|' in text else "-"
                if "Primary Camera" in text:
                    primary_camera = text
                if "Secondary Camera" in text:
                    secondary_camera = text
                if "Display" in text:
                    display_size = text
                if "Battery" in text:
                    battery_capacity = text
        except Exception as e:
            pass
        
        try:
            price = product.find('div', {'class': '_30jeq3 _1_WHN1'}).text.strip()
        except AttributeError:
            price = "-"
        
        smartphones.append([brand_name, smartphone_name, colour, ram, storage, primary_camera, secondary_camera, display_size, battery_capacity, price, product_url])
    
    return smartphones

# Function to scrape smartphones from Flipkart search results
def scrape_flipkart_smartphones(search_query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # URL for search query on Flipkart
    base_url = f"https://www.flipkart.com/search?q={search_query}"
    
    html = fetch_html(base_url, headers)
    if html is None:
        print("Failed to fetch the webpage.")
        return
    
    soup = BeautifulSoup(html, 'html.parser')
    smartphones = extract_smartphone_details(soup)
    
    if not smartphones:
        print("No smartphones found on the page.")
        return
    
    # Create a DataFrame and save to CSV
    df = pd.DataFrame(smartphones, columns=["Brand Name", "Smartphone Name", "Colour", "RAM", "Storage(ROM)", "Primary Camera", "Secondary Camera", "Display Size", "Battery Capacity", "Price", "Product URL"])
    df.to_csv(f"{search_query}_flipkart_smartphones.csv", index=False)
    print(f"Scraped {len(smartphones)} smartphones. Data saved to {search_query}_flipkart_smartphones.csv")

# Input from user
search_query = input("Enter the smartphone to search: ").replace(' ', '+')  # Replace spaces with '+' for the search URL
scrape_flipkart_smartphones(search_query)


# In[ ]:


from geopy.geocoders import Nominatim

# Function to get latitude and longitude of a city
def get_coordinates(city_name):
    geolocator = Nominatim(user_agent="geoapiExercises")
    
    # Geocoding to get location
    location = geolocator.geocode(city_name)
    
    if location:
        return location.latitude, location.longitude
    else:
        return None

# Input city from the user
city = input("Enter the name of the city: ")

# Get the coordinates
coordinates = get_coordinates(city)

if coordinates:
    print(f"Coordinates of {city} are: Latitude = {coordinates[0]}, Longitude = {coordinates[1]}")
else:
    print(f"Could not find coordinates for {city}")


# In[ ]:


import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to fetch HTML content from a URL
def fetch_html(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch {url}")
        return None

# Function to scrape gaming laptop details from Digit.in
def scrape_best_gaming_laptops():
    url = "https://www.digit.in/top-products/best-gaming-laptops-3534.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    html = fetch_html(url, headers)
    if not html:
        return

    soup = BeautifulSoup(html, 'html.parser')

    # List to store all laptop details
    laptops = []

    # Locate the sections that contain laptop details
    products = soup.find_all('div', class_='TopNumbeHeading')

    # Loop through each product and extract details
    for product in products:
        try:
            # Extract laptop name
            laptop_name = product.find('h3').text.strip()

            # Extract features
            features = product.find_next_sibling('div', class_='SpcsDetails').find_all('li')
            feature_dict = {feature.find('span').text.strip(): feature.find('strong').text.strip() for feature in features}

            # Extract price
            try:
                price = product.find_next_sibling('div', class_='Price').text.strip()
            except AttributeError:
                price = "-"

            # Collect all the details into a dictionary
            laptop_details = {
                'Laptop Name': laptop_name,
                'Price': price,
            }

            # Append feature details
            laptop_details.update(feature_dict)

            laptops.append(laptop_details)
        except AttributeError:
            continue

    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(laptops)

    # Save the results in a CSV file
    df.to_csv("best_gaming_laptops_digit.csv", index=False)
    print(f"Scraped {len(laptops)} gaming laptops. Data saved to best_gaming_laptops_digit.csv")

# Run the scraping function
scrape_best_gaming_laptops()


# In[ ]:


from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
from bs4 import BeautifulSoup

# Function to initialize Selenium WebDriver
def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode
    driver = webdriver.Chrome(options=options)
    return driver

# Function to scrape billionaires data
def scrape_forbes_billionaires():
    url = 'https://www.forbes.com/billionaires/'
    
    # Initialize WebDriver
    driver = initialize_driver()
    driver.get(url)
    time.sleep(5)  # Allow time for the page to load

    # Scroll down to load more content (optional, depending on content length)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)

    # Get the page source and parse it with BeautifulSoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find the container with the billionaire data
    table = soup.find('div', {'class': 'table-container'})

    # List to store the data
    billionaires = []

    if table:
        # Loop through each billionaire entry
        rows = table.find_all('div', {'class': 'tr'})
        for row in rows[1:]:  # Skipping the header row
            try:
                rank = row.find('div', {'class': 'rank'}).text.strip()
                name = row.find('div', {'class': 'personName'}).text.strip()
                net_worth = row.find('div', {'class': 'netWorth'}).text.strip()
                age = row.find('div', {'class': 'age'}).text.strip() if row.find('div', {'class': 'age'}) else '-'
                citizenship = row.find('div', {'class': 'countryOfCitizenship'}).text.strip()
                source = row.find('div', {'class': 'source'}).text.strip()
                industry = row.find('div', {'class': 'category'}).text.strip()

                # Append the data to the list
                billionaires.append([rank, name, net_worth, age, citizenship, source, industry])
            except AttributeError:
               


# In[ ]:


import os
import pandas as pd
from googleapiclient.discovery import build

# Function to initialize YouTube API client
def initialize_youtube(api_key):
    return build('youtube', 'v3', developerKey=api_key)

# Function to extract comments from a YouTube video
def get_youtube_comments(video_id, youtube, max_results=100):
    comments = []
    next_page_token = None

    while len(comments) < max_results:
        # Request to get comment threads
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            pageToken=next_page_token,
            maxResults=100,  # Fetch 100 comments per request
            textFormat="plainText"
        )
        response = request.execute()

        # Loop through each comment in the response
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comment_text = comment['textDisplay']
            upvote_count = comment['likeCount']
            published_at = comment['publishedAt']

            # Append comment details to the list
            comments.append({
                'Comment': comment_text,
                'Upvotes': upvote_count,
                'Posted At': published_at
            })

        # Check if there are more comments to fetch
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return comments

# Function to save comments to CSV
def save_comments_to_csv(comments, file_name='youtube_comments.csv'):
    df = pd.DataFrame(comments)
    df.to_csv(file_name, index=False)
    print(f"Saved {len(comments)} comments to {file_name}")

# Main function to extract comments from a YouTube video
def main():
    api_key = 'YOUR_YOUTUBE_API_KEY'  # Replace with your API Key
    video_id = input("Enter the YouTube video ID: ")  # e.g., 'dQw4w9WgXcQ'
    
    youtube = initialize_youtube(api_key)

    # Get comments (fetch at least 500 comments)
    comments = get_youtube_comments(video_id, youtube, max_results=500)

    # Save the comments to a CSV file
    save_comments_to_csv(comments)

# Run the program
if __name__ == "__main__":
    main()


# In[ ]:


from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

# Function to initialize Selenium WebDriver
def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode
    driver = webdriver.Chrome(options=options)
    return driver

# Function to extract hostel data from Hostelworld for a specific location
def scrape_hostels_in_london():
    url = "https://www.hostelworld.com/hostels/London"
    
    # Initialize the WebDriver
    driver = initialize_driver()
    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    # Get the page source and parse it using BeautifulSoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # List to store hostel data
    hostels = []

    # Loop through all hostels on the page
    hostel_cards = soup.find_all('div', class_='property-card')

    for hostel in hostel_cards:
        try:
            # Hostel Name
            hostel_name = hostel.find('h2', class_='title').text.strip()

            # Distance from city centre
            distance = hostel.find('span', class_='distance-description').text.strip()

            # Rating and Total Reviews
            rating_tag = hostel.find('div', class_='score')
            if rating_tag:
                ratings = rating_tag.text.strip()
            else:
                ratings = "-"
            
            total_reviews_tag = hostel.find('div', class_='reviews')
            if total_reviews_tag:
                total_reviews = total_reviews_tag.text.strip().replace('Total Reviews', '').strip()
            else:
                total_reviews = "-"
            
            # Price for privates
            privates_price_tag = hostel.find('div', class_='price price-privates')
            if privates_price_tag:
                privates_price = privates_price_tag.text.strip().replace('Privates From', '').strip()
            else:
                privates_price = "-"

            # Price for dorms
            dorms_price_tag = hostel.find('div', class_='price price-dorms')
            if dorms_price_tag:
                dorms_price = dorms_price_tag.text.strip().replace('Dorms From', '').strip()
            else:
                dorms_price = "-"

            # Facilities (using placeholder as Hostelworld loads them dynamically)
            facilities = ', '.join([fac.text for fac in hostel.find_all('li', class_='facilities-list-item')]) if hostel.find('li', class_='facilities-list-item') else "-"

            # Property description
            property_description = hostel.find('div', class_='rating-facilities').text.strip() if hostel.find('div', class_='rating-facilities') else "-"

            # Append hostel data to the list
            hostels.append({
                'Hostel Name': hostel_name,
                'Distance from City Centre': distance,
                'Ratings': ratings,
                'Total Reviews': total_reviews,
                'Privates From Price': privates_price,
                'Dorms From Price': dorms_price,
                'Facilities': facilities,
                'Property Description': property_description
            })

        except AttributeError:
            continue

    # Quit the Selenium driver
    driver.quit()

    # Save the data to a Pandas DataFrame
    df = pd.DataFrame(hostels)

    # Save the data to CSV
    df.to_csv('hostels_in_london.csv', index=False)
    print(f"Scraped data for {len(hostels)} hostels in London. Data saved to hostels_in_london.csv")

# Run the scraping function
scrape_hostels_in_london()


# In[ ]:




