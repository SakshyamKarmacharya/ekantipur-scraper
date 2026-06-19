eKantipur News and Media Scraper

This is a Python web scraping application built with Playwright to automatically collect news and media data from the eKantipur news portal. The script targets the latest Entertainment News articles and retrieves the featured Cartoon of the Day.

It uses multi-tiered selectors and customized browser contexts to handle dynamic web elements, lazy-loaded images, and potential network delays.

Features

* Entertainment Content: Collects article titles, image links, categories, and author names up to a specified limit.
* Cartoon Extractor: Identifies editorial cartoons, sanitizes metadata strings, and captures the title and illustrator.
* Browser Emulation: Sets the browser locale to ne-NP, configures the timezone to Asia/Kathmandu, and applies a realistic User-Agent to mirror standard desktop browsing.
* Data Persistence: Saves UTF-8 encoded outputs with low-level disk flushes to ensure data is fully written to the file system.

Tech Stack

* Language: Python 3.8+
* Framework: Playwright for Python (Synchronous API)
* Output Format: JSON

Project Structure

Ensure your project files match this layout:

ekantipur-scraper/
├── scraper.py          # Main script containing scraping pipelines and orchestrator
├── requirements.txt    # Dependencies
└── output.json         # Generated data file

Sample Output Schema

Once the execution completes, the data is saved locally to output.json using the following structure:

{
  "entertainment_news": [
    {
      "title": "मनोरन्जनात्मक समाचार शीर्षक...",
      "image_url": "https://ekantipur.com",
      "category": "मनोरञ्जन",
      "author": "कान्तिपुर संवाददाता"
    }
  ],
  "cartoon_of_the_day": {
    "title": "राजनीतिक व्यंग्यचित्र",
    "image_url": "https://ekantipur.com",
    "author": "रविकाफले"
  }
}

Setup and Execution

Installation

1. Clone the repository:
   git clone https://github.com
   cd ekantipur-scraper

2. Install the required packages:
   pip install playwright

3. Install the Chromium browser binaries:
   playwright install chromium

Execution

Run the scraper script directly from your terminal:

python scraper.py
