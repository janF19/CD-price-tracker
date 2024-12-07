import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re



def clean_train_code(train_code_name):
    """
    Extract clean train code and name from a given string.
    """
    # Match the train number and name pattern after "vlaku"
    match = re.search(r'vlaku\s+[A-Z]+\s+(\d+\s+.+)', train_code_name)
    return match.group(1) if match else train_code_name
    # str.replace("Přejít na detail vlaku ", train_code_name)
    # return train_code_name
    
def clean_price(price_text):
    """
    Extract just the price value
    """
    match = re.search(r'(\d+)\s*Kč', price_text)
    return match.group(1) if match else price_text

def scrape_train_connections(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    connection_articles = soup.find_all('article', class_='overview-connection')
    connections = []
    
    for article in connection_articles:
        try:
            # Clean train code and name
            train_detail_link = article.find('a', class_='overview-label__link')
            train_code_name = train_detail_link.find('span', class_='vh').text.strip() if train_detail_link else 'N/A'
            
            # Extract departure time
            departure_time_elem = article.find('p', class_='schedule__station schedule__text--time')
            departure_time = departure_time_elem.text.strip() if departure_time_elem else 'N/A'
            
            # Extract departure station
            departure_station_elem = article.find('p', class_='schedule__station schedule__text--primary')
            departure_station = departure_station_elem.find('a').text.strip() if departure_station_elem and departure_station_elem.find('a') else 'N/A'
            
            # Clean price
            price_button = article.find('button', class_='btn btn--green')
            if price_button and price_button.find('span'):
                # Remove non-numeric characters and additional text
                price_text = price_button.find('span').text.strip()
                price = ''.join(char for char in price_text if char.isdigit() or char == ' ')
                price = price.split()[0] if price.split() else 'N/A'
            else:
                price = 'N/A'
                
            price = clean_price(price)
                
            #clean train code name
            train_code_name = clean_train_code(train_code_name)
            
            
            connection = {
                'Train Code': train_code_name,
                'Departure Time': departure_time,
                'Departure Station': departure_station,
                'Price': price
            }
            
            connections.append(connection)
        
        except Exception as e:
            print(f"Error processing connection: {e}")
    
    return connections

def save_connections_to_csv(connections, filename='train_connections2.csv'):
    """
    Save connection details to a CSV file.
    
    Args:
        connections (list): List of connection dictionaries
        filename (str): Name of the output CSV file
    """
    if not connections:
        print("No connections to save.")
        return
    
    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        # Use the keys of the first connection as fieldnames
        fieldnames = connections[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for connection in connections:
            writer.writerow(connection)
    
    print(f"Connections saved to {filename}")

def process_train_connections(html_content):
    """
    Main function to scrape and save train connection details.
    
    Args:
        html_content (str): The HTML content of the page to scrape
    """
    # Scrape connections
    connections = scrape_train_connections(html_content)
    
    # Save to CSV
    save_connections_to_csv(connections)
    
    return connections



# Example usage in your main script
# Assuming you have the HTML content from the redirected page
# html_content = driver.page_source
# process_train_connections(html_content)