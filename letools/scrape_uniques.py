import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os


def scrape_items_data(url, name_url):
    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # First fetch the name data JSON using Selenium
        print("Fetching name data JSON...")
        driver.get(name_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "pre"))
        )
        # Parse the JSON from the pre element that contains it
        name_data_text = driver.find_element(By.TAG_NAME, "pre").text
        import json

        name_data = json.loads(name_data_text)
        print(f"Retrieved name data with {len(name_data)} entries")

        # Open the webpage
        driver.get(url)

        # Wait for the consent banner and close it
        try:
            print("Waiting for consent banner...")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ncmp__btn"))
            )
            accept_button = driver.find_element(
                By.CSS_SELECTOR, ".ncmp__btn:not(.ncmp__btn-border)"
            )
            accept_button.click()
            print("Closed consent banner")
        except Exception as e:
            print(f"No consent banner found or error closing it: {e}")

        # Wait for the page to fully load and the JavaScript data to be available
        print("Waiting for the page data to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "uniques-table"))
        )

        # Extract the itemDB data directly from JavaScript
        print("Extracting data from JavaScript objects...")

        # Get all unique items by executing JavaScript in the page context
        items_data = driver.execute_script("""
            let items = [];

            // Iterate through all base item types in the database
            Object.entries(window.itemDB.uniqueList.uniques).forEach(([id, data]) => {
                items.push({
                   id: data.uniqueId,
                   displayNameKey: data.displayNameKey,
                   rerollChance: data.rerollChance,
                   rarityTier: data.rarityTier,
                });
            });

            return items;
        """)

        print(f"Found {len(items_data)} unique items")

        for item in items_data:
            # Get the display name from the name_data using the displayNameKey
            display_name_key = item["displayNameKey"]
            item["name"] = name_data.get(display_name_key, "Unknown Item")

        return items_data

    finally:
        # Close the browser
        driver.quit()


def scrape_items_table(url):
    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Open the webpage
        driver.get(url)

        # Wait for the consent banner and close it
        try:
            print("Waiting for consent banner...")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ncmp__btn"))
            )
            accept_button = driver.find_element(
                By.CSS_SELECTOR, ".ncmp__btn:not(.ncmp__btn-border)"
            )
            accept_button.click()
            print("Closed consent banner")
        except Exception as e:
            print(f"No consent banner found or error closing it: {e}")

        # Wait for the table to load
        print("Waiting for the items table to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "uniques-table"))
        )

        all_items = []

        # Get the total number of pages
        pagination = driver.find_element(By.CLASS_NAME, "dataTables_paginate")
        page_links = pagination.find_elements(By.CSS_SELECTOR, "span a.paginate_button")
        last_page = int(page_links[-1].text)

        for page in range(1, last_page + 1):
            print(f"Scraping page {page} of {last_page}")

            # Wait for the table to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "uniques-table"))
            )

            # Extract data from the current page
            rows = driver.find_elements(By.CSS_SELECTOR, "#uniques-table tbody tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                name_element = cells[0].find_element(By.TAG_NAME, "a")

                item = {
                    "name": name_element.text,
                    "item_id": name_element.get_attribute("item-id"),
                    "url": name_element.get_attribute("href"),
                    "type": cells[1].text,
                    "class": cells[2].text if cells[2].text != "–" else None,
                    "level": cells[3].text if cells[3].text != "–" else None,
                    "legendary_potential_level": cells[4].text
                    if cells[4].text != "–"
                    else None,
                    "reroll_chance": cells[5].text if cells[5].text != "–" else None,
                }
                all_items.append(item)

            # Go to the next page if not on the last page
            if page < last_page:
                next_button = driver.find_element(By.ID, "uniques-table_next")
                next_button.click()
                # Wait a bit for the page to load
                time.sleep(1)

        return all_items

    finally:
        # Close the browser
        driver.quit()


def save_to_csv(items, filename):
    df = pd.DataFrame(items)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")


def save_to_json(items, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")


def main():
    # Replace with the actual URL of the website
    url = "https://www.lastepochtools.com/db/items/unique"
    data_url = "https://www.lastepochtools.com/data/version121/i18n/full/en.json"

    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)

    print("Starting scraper...")
    # items = scrape_items_table(url)
    items = scrape_items_data(url, data_url)

    # Save data in different formats
    save_to_csv(items, "output/unique_items.csv")
    save_to_json(items, "output/unique_items.json")

    print(f"Scraping complete. Total items collected: {len(items)}")


if __name__ == "__main__":
    main()
