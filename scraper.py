import os
import requests
from bs4 import BeautifulSoup

# Base URL and output directory
base_url = "http://learnyouahaskell.com/"
output_dir = "learnyouahaskell"
os.makedirs(output_dir, exist_ok=True)

# Localhost root for serving files
localhost_root = "http://localhost:8000/"

# Download the chapters page
chapters_url = base_url + "chapters"
response = requests.get(chapters_url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract chapter links (ignoring section links with '#')
    unwanted_chapters = soup.select('ul a[href]')
    for unwanted_link in unwanted_chapters:
        unwanted_link.decompose()
    chapters = soup.select("ol.chapters a[href]")
    chapter_links = [link['href'] for link in chapters if '#' not in link['href']]

    # Create a mapping of chapter URLs to local filenames
    local_links = {link: f"{link.split('/')[-1]}.html" for link in chapter_links}

    print(local_links)

    # Update links on the chapters page to point to local files on localhost
    for link in chapters:
        if link['href'] in local_links:
            link['href'] = localhost_root + local_links[link['href']]

    # Save the updated chapters page locally
    chapters_path = os.path.join(output_dir, "chapters.html")
    with open(chapters_path, "w", encoding="utf-8") as file:
        file.write(str(soup))
    print(f"Saved chapters page: {chapters_path}")

    # Download each chapter and update internal links
    for link, local_file in local_links.items():
        chapter_url = base_url + link
        response = requests.get(chapter_url)

        if response.status_code == 200:
            chapter_soup = BeautifulSoup(response.text, "html.parser")

            # Clean existing styles
            for style in chapter_soup.find_all('style'):
                style.decompose()

            for img in chapter_soup.find_all('img'):
                img.decompose()

            # Add custom styles
            custom_style = """
            <style>
                body { font-family: Arial, sans-serif; font-size: 18px; background: powderblue; color: #333; line-height: 1.6; padding: 40px }
                a { color: black; text-decoration: none; }
                a:hover { text-decoration: underline; }
                pre, code { background: #f4f4f4; padding: 10px; border-radius: 25px; }
                h1, h2, h3 { color: #007BFF; }
                .dp-highlighter{
                border-radius: 15px;
                padding-left: 10px;
                }
                .footdiv{
                display: flex;
                
                }
            </style>
            """
            chapter_soup.head.append(BeautifulSoup(custom_style, "html.parser"))

            # Update internal links to point to local files on localhost
            for a_tag in chapter_soup.find_all("a", href=True):
                href = a_tag['href']
                if href in local_links:
                    a_tag['href'] = localhost_root + local_links[href]

            # Save the chapter locally
            output_path = os.path.join(output_dir, local_file)
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(str(chapter_soup))
            print(f"Saved: {output_path}")
        else:
            print(f"Failed to fetch {chapter_url}")
else:
    print(f"Failed to fetch the chapters page: {chapters_url}")

# Rename chapters.html to index.html for localhost serving
os.rename(os.path.join(output_dir, "chapters.html"), os.path.join(output_dir, "index.html"))
print("All chapters processed and saved. Ready for localhost serving.")
