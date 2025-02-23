import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import webbrowser

# Flag to stop the crawler
download_active = False


def make_request(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.RequestException as e:
        result_text.insert(tk.END, f"Error: {e}\n")
        return None


def find_elements(soup, url, element_type):
    found_items = set()

    if element_type == "Images":
        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                found_items.add(urljoin(url, src))

    elif element_type == "Links":
        for link in soup.find_all("a"):
            href = link.get("href")
            if href:
                found_items.add(urljoin(url, href))

    return found_items


def crawler(url, element_type, visited=None):
    global download_active
    if visited is None:
        visited = set()

    if url in visited or not download_active:
        return

    visited.add(url)
    soup = make_request(url)
    if soup is None:
        return

    results = find_elements(soup, url, element_type)

    for index, item in enumerate(results, start=1):
        result_text.insert(tk.END, f"{index}. ", "bold")
        result_text.insert(tk.END, item + "\n", "link")

    result_text.yview(tk.END)

    for link in soup.find_all("a"):
        found_link = link.get("href")
        if found_link:
            found_link = urljoin(url, found_link)
            if found_link.startswith("http") and found_link not in visited and download_active:
                crawler(found_link, element_type, visited)


def start_crawler():
    global download_active
    download_active = True
    url = url_entry.get()
    element_type = selection.get()
    result_text.delete(1.0, tk.END)

    if url and url != placeholder_text and element_type:
        thread = threading.Thread(target=crawler, args=(url, element_type))
        thread.start()


def stop_crawler():
    global download_active
    download_active = False


def open_link(event):
    index = result_text.index(tk.CURRENT)
    link = result_text.get(index + " linestart", index + " lineend").strip()
    if link.startswith("http"):
        webbrowser.open(link)


# **Tkinter GUI**
root = tk.Tk()
root.title("Web Crawler")
root.geometry("600x500")

# **Placeholder İşlevleri**
placeholder_text = "https://example.com"

def set_placeholder(event):
    if url_entry.get() == placeholder_text:
        url_entry.delete(0, tk.END)
        url_entry.config(fg="black")


def restore_placeholder(event):
    if not url_entry.get():
        url_entry.insert(0, placeholder_text)
        url_entry.config(fg="grey")


# **Input Field**
tk.Label(root, text="Enter Website Link:", font=("Arial", 12)).pack(pady=5)
url_entry = tk.Entry(root, width=50, fg="grey")
url_entry.insert(0, placeholder_text)  # Placeholder metni ekle
url_entry.bind("<FocusIn>", set_placeholder)
url_entry.bind("<FocusOut>", restore_placeholder)
url_entry.pack(pady=5)

# **Selection Field**
tk.Label(root, text="What do you want to search for?", font=("Arial", 12)).pack(pady=5)
selection = tk.StringVar(value="Links")
options = ["Links", "Images"]
dropdown = ttk.Combobox(root, textvariable=selection, values=options, state="readonly")
dropdown.pack(pady=5)

# **Start and Stop Buttons**
button_frame = tk.Frame(root)
button_frame.pack(pady=5)

start_button = tk.Button(button_frame, text="Start Crawl", command=start_crawler, font=("Arial", 10))
start_button.pack(side=tk.LEFT, padx=5)

stop_button = tk.Button(button_frame, text="Stop", command=stop_crawler, font=("Arial", 10), fg="red")
stop_button.pack(side=tk.LEFT, padx=5)

# **Result Display**
result_text = scrolledtext.ScrolledText(root, width=70, height=15, wrap=tk.WORD)
result_text.pack(pady=5)
result_text.tag_config("link", foreground="blue", underline=True)
result_text.tag_config("bold", font=("Arial", 10, "bold"))
result_text.bind("<Button-1>", open_link)

root.mainloop()
