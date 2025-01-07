from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from train_connection_scraper import scrape_train_connections
import time
import random
from datetime import datetime, timedelta
import os

def get_target_date():
    # Read the date from file or create initial date if file doesn't exist
    date_file = 'target_date.txt'
    
    if not os.path.exists(date_file):
        # Initialize with 20.12.2024 as the starting date
        initial_date = datetime.strptime('10.1.2025', '%d.%m.%Y')
        with open(date_file, 'w') as f:
            f.write(initial_date.strftime('%d.%m.%Y'))
        return initial_date
    
    with open(date_file, 'r') as f:
        current_date = datetime.strptime(f.read().strip(), '%d.%m.%Y')
    
    # Check if it's Friday and we need to update the date
    if datetime.now().weekday() == 4:  # Friday is 4
        new_date = current_date + timedelta(days=7)
        with open(date_file, 'w') as f:
            f.write(new_date.strftime('%d.%m.%Y'))
        return new_date
    
    return current_date

def automate_train_search():
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    
    # Add headless mode to run without opening browser window
    options.add_argument('--headless')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://www.cd.cz/spojeni-a-jizdenka/#hledej")
        wait = WebDriverWait(driver, 20)  # Increased timeout
        
        # Handle cookie consent with multiple fallback strategies
        cookie_strategies = [
            (By.ID, "consentBtnall"),
            (By.XPATH, "//button[contains(text(), 'Přijmout')]"),
            (By.CLASS_NAME, "consent-button")
        ]
        
        for strategy in cookie_strategies:
            try:
                cookies_button = wait.until(EC.element_to_be_clickable(strategy))
                cookies_button.click()
                break
            except TimeoutException:
                continue
        
        # Input fields with more robust handling
        input_strategies = [
            (By.CSS_SELECTOR, "input[placeholder='Zadejte stanici odkud']"),
            (By.XPATH, "//input[@data-testid='search-from-input']")
        ]
        
        from_station = None
        for strategy in input_strategies:
            try:
                from_station = wait.until(EC.presence_of_element_located(strategy))
                from_station.clear()
                from_station.send_keys("Praha hl.n.")
                time.sleep(random.uniform(0.5, 1.5))
                from_station.send_keys(Keys.TAB)
                break
            except TimeoutException:
                continue
        
        if not from_station:
            raise Exception("Could not locate departure station input")
        
        # Similar robust approach for arrival station
        to_station_strategies = [
            (By.CSS_SELECTOR, "input[placeholder='Zadejte stanici kam']"),
            (By.XPATH, "//input[@data-testid='search-to-input']")
        ]
        
        to_station = None
        for strategy in to_station_strategies:
            try:
                to_station = wait.until(EC.presence_of_element_located(strategy))
                to_station.clear()
                to_station.send_keys("Opava východ")
                time.sleep(random.uniform(0.5, 1.5))
                to_station.send_keys(Keys.TAB)
                break
            except TimeoutException:
                continue
        
        if not to_station:
            raise Exception("Could not locate arrival station input")
        
        # Replace hardcoded date with dynamic date
        target_date = get_target_date()
        date_input = wait.until(EC.presence_of_element_located((By.ID, "depDate")))
        date_input.clear()
        date_input.send_keys(target_date.strftime('%d.%m.%Y'))
        
        time_input = wait.until(EC.presence_of_element_located((By.ID, "timePickerObj")))
        time_input.clear()
        time_input.send_keys("13:20")
        
        # Enhanced search button handling
        search_strategies = [
            (By.XPATH, "//button[contains(@class, 'search-btn') and contains(text(), 'Vyhledat')]"),
            (By.CSS_SELECTOR, "button[data-bind='click: search']"),
            (By.XPATH, "//button[@title='Vyhledat']"),
            (By.CLASS_NAME, "search-btn")
        ]
        
        search_button = None
        for strategy in search_strategies:
            try:
                search_button = wait.until(EC.element_to_be_clickable(strategy))
                try:
                    search_button.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", search_button)
                break
            except TimeoutException:
                continue
        
        if not search_button:
            raise Exception("Could not locate search button")
        
        # Wait for results with progressive timeout
        time.sleep(5)
        
        html_content = driver.page_source
        connections = scrape_train_connections(html_content)
        return connections
        
    except Exception as e:
        print(f"Detailed error: {e}")
        print("Current URL:", driver.current_url)
        return []
    
    finally:
        # Always close the browser, regardless of success or failure
        driver.quit()
        


if __name__ == "__main__":
    connections = automate_train_search()
    print(connections)  
