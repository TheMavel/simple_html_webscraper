import tkinter as tk
from tkinter import simpledialog, messagebox, Button, Entry, Checkbutton, BooleanVar
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
from urllib.parse import urlparse

def get_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we capture HTTP errors
        print(f"Static HTML content fetched successfully from {url}")
        return response.text
    except requests.RequestException as e:
        print(f"An error occurred while fetching static HTML: {e}")
        return None

def clean_text(text):
    """Cleans up text by removing excessive whitespace and line breaks."""
    return ' '.join(text.split())

def scrape_static_content(html):
    """Extracts and cleans text content from static HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    content_blocks = soup.find_all(['p', 'h1', 'h2', 'h3'])  # Adjust tags as needed
    cleaned_content = [clean_text(block.get_text()) for block in content_blocks if block.get_text().strip() != '']
    print(f"Extracted static content: {cleaned_content[:5]}")  # Print first 5 blocks for debugging
    return '\n\n'.join(cleaned_content)

def scrape_dynamic_content(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    driver.implicitly_wait(5) 
    content = driver.page_source 
    soup = BeautifulSoup(content, 'html.parser')
    cleaned_content = [clean_text(block.get_text()) for block in soup.find_all(['p', 'h1', 'h2', 'h3']) if block.get_text().strip() != '']
    driver.quit()
    print(f"Extracted dynamic content: {cleaned_content[:5]}")  # Print first 5 blocks for debugging
    return '\n\n'.join(cleaned_content)

def save_content(content, filename):
    """Saves the extracted content to a text file."""
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Content saved to {filename}")

def sanitize_filename(filename):
    """Sanitizes the filename by removing invalid characters."""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', filename)

def generate_filename_from_url(url):
    """Generates a filename based on the provided URL."""
    parsed_url = urlparse(url)
    filename = parsed_url.netloc + parsed_url.path
    filename = sanitize_filename(filename)
    return filename or 'output'  # Default to 'output' if filename is empty

def start_scraping():
    """Initiates the scraping process based on user input."""
    url = url_entry.get()
    if not url.strip():
        messagebox.showerror("Error", "Please enter a URL")
        return

    if dynamic_var.get():
        html = scrape_dynamic_content(url)
    else:
        html = get_html(url)

    if html:
        content = scrape_static_content(html)
        if content.strip():  # Ensure content is not empty
            filename = generate_filename_from_url(url) + '.txt'
            save_content(content, filename)
            messagebox.showinfo("Success", f"Content scraped and saved successfully as {filename}.")
        else:
            messagebox.showerror("Error", "Scraped content is empty")
    else:
        messagebox.showerror("Error", "Failed to retrieve the website")

# --- GUI Setup ---
root = tk.Tk()
root.title("Web Scraper Tool")

# URL Input
tk.Label(root, text="Enter URL:").pack()
url_entry = Entry(root, width=50)
url_entry.pack()

# Dynamic Content Checkbox
dynamic_var = BooleanVar()
dynamic_check = Checkbutton(root, text="Dynamic Content (JavaScript)", variable=dynamic_var)
dynamic_check.pack()

# Scrape button
scrape_button = Button(root, text="Scrape", command=start_scraping)
scrape_button.pack()

root.mainloop()
