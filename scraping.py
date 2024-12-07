from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import csv
import re

def clean_train_code(train_code_name):
    """
    Extract clean train code and name
    """
    match = re.search(r'(.*?) (.*)', train_code_name)
    return match.group(0) if match else train_code_name
    # str.replace("Přejít na detail vlaku ", train_code_name)
    # return train_code_name

def clean_price(price_text):
    """
    Extract just the price value
    """
    match = re.search(r'(\d+\s*Kč)', price_text)
    return match.group(1) if match else price_text

def scrape_train_connections(html_content):
    """
    Scrape train connection details from the HTML content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    connection_articles = soup.find_all('article', class_='overview-connection')
    
    connections = []
    
    for article in connection_articles:
        try:
            # Extract train code and name
            train_detail_link = article.find('a', class_='overview-label__link')
            train_code_name = train_detail_link.find('span', class_='vh').text.strip() if train_detail_link else 'N/A'
            cleaned_train_code = clean_train_code(train_code_name)
            
            #edit train code basecally strip firts sentance
            cleaned_train_code = cleaned_train_code.replace("Přejít na detail vlaku ", "")
            
            # Extract departure time
            departure_time_elem = article.find('p', class_='schedule__station schedule__text--time')
            departure_time = departure_time_elem.text.strip() if departure_time_elem else 'N/A'
            
            # Extract departure station
            departure_station_elem = article.find('p', class_='schedule__station schedule__text--primary')
            departure_station = departure_station_elem.find('a').text.strip() if departure_station_elem and departure_station_elem.find('a') else 'N/A'
            
            # Extract price
            price_button = article.find('button', class_='btn btn--green')
            price_text = price_button.find('span').text.strip() if price_button and price_button.find('span') else 'N/A'
            cleaned_price = clean_price(price_text)
            
            # Create connection dictionary
            connection = {
                'Train': cleaned_train_code,
                'Departure Time': departure_time,
                'Departure Station': departure_station,
                'Price': cleaned_price
            }
            
            connections.append(connection)
        
        except Exception as e:
            print(f"Error processing connection: {e}")
    
    return connections

def save_connections_to_csv(connections, filename='train_connections3.csv'):
    """
    Save connection details to a CSV file.
    """
    if not connections:
        print("No connections to save.")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Train', 'Departure Time', 'Departure Station', 'Price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for connection in connections:
            writer.writerow(connection)
    
    print(f"Connections saved to {filename}")

# Rest of the script remains the same as in the previous version





def automate_train_search():
    # Setup Chrome WebDriver
    driver = webdriver.Chrome()
    
    try:
        # Navigate to the website
        driver.get("https://www.cd.cz/spojeni-a-jizdenka/#hledej")
        wait = WebDriverWait(driver, 15)

        # Specific cookie consent button
        try:
            cookies_button = wait.until(EC.element_to_be_clickable((
                By.ID, "consentBtnall"
            )))
            cookies_button.click()
        except Exception as cookie_error:
            print(f"Cookie consent button error: {cookie_error}")

        # Departure Station
        from_station = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, "input[placeholder='Zadejte stanici odkud']"
        )))
        from_station.clear()
        from_station.send_keys("Praha hl.n.")
        time.sleep(1)
        from_station.send_keys(Keys.TAB)

        # Arrival Station
        to_station = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, "input[placeholder='Zadejte stanici kam']"
        )))
        to_station.clear()
        to_station.send_keys("Opava východ")
        time.sleep(1)
        to_station.send_keys(Keys.TAB)

        # Date Input
        date_input = wait.until(EC.presence_of_element_located((By.ID, "depDate")))
        date_input.clear()
        date_input.send_keys("6.12.2024")
        date_input.send_keys(Keys.TAB)

        # Time Input
        time_input = wait.until(EC.presence_of_element_located((By.ID, "timePickerObj")))
        time_input.clear()
        time_input.send_keys("18:20")
        time_input.send_keys(Keys.TAB)

        # Search Button - Multiple Methods
        search_strategies = [
            (By.XPATH, "//button[contains(@class, 'search-btn') and contains(text(), 'Vyhledat')]"),
            (By.CSS_SELECTOR, "button[data-bind='click: search']"),
            (By.XPATH, "//button[@title='Vyhledat']")
        ]

        for strategy in search_strategies:
            try:
                search_button = wait.until(EC.element_to_be_clickable(strategy))
                # Try different clicking methods
                try:
                    search_button.click()
                except:
                    driver.execute_script("arguments[0].click();", search_button)
                break
            except Exception as search_error:
                print(f"Search button strategy failed: {search_error}")

        # Wait for results
        time.sleep(5)

        # Get the page source for scraping
        html_content = driver.page_source

        # Scrape train connections
        connections = scrape_train_connections(html_content)

        # Save connections to CSV
        save_connections_to_csv(connections)

        # Print connections for verification
        for connection in connections:
            print(connection)

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Current URL:", driver.current_url)

    finally:
        input("Press Enter to close the browser...")
        driver.quit()

if __name__ == "__main__":
    automate_train_search()