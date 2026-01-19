import json
import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def scrape_entertainment_news(page, max_articles=5):
    #Navigate to entertainment section and extract top 5 news articles
    entertainment_news = []
    
    try:
        print("Navigating to homepage first...")
        page.goto("https://ekantipur.com", wait_until="domcontentloaded", timeout=60000)
        print(" Homepage loaded")
        
        
        time.sleep(2)
        page.evaluate("window.scrollTo(0, 300)")
        time.sleep(1)
        
        # Try to find and click entertainment link
        print("Looking for entertainment section link...")
        entertainment_found = False
        
        link_strategies = [
            ("text=मनोरञ्जन", "Nepali text"),
            ("a[href*='entertainment']", "href contains entertainment"),
            ("text=/.*मनोरञ्जन.*/i", "case insensitive Nepali"),
            (".nav a:has-text('मनोरञ्जन')", "nav menu item"),
        ]

        for selector, desc in link_strategies:
            try:
                element = page.wait_for_selector(selector, timeout=5000)
                if element:
                    print(f" Found link using: {desc}")
                    # Scroll element into view
                    element.scroll_into_view_if_needed()
                    time.sleep(0.5)
                    element.click()
                    entertainment_found = True
                    break
            except:
                continue
       
        if not entertainment_found:
            print("  Trying direct navigation to entertainment page...")
            try:
                page.goto("https://ekantipur.com/entertainment", 
                         wait_until="domcontentloaded", 
                         timeout=60000)
                entertainment_found = True
            except PlaywrightTimeout:
                print("  Timeout on entertainment page")
                page.goto("https://ekantipur.com/entertainment", timeout=90000)
        
        if entertainment_found:
            print("  Entertainment section loaded")
            # Wait for content to load
            page.wait_for_load_state("domcontentloaded")
            time.sleep(3)
            
            # Scroll down to load more content
            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(1)
        
        print("Searching for article elements...")
        
        article_selectors = [
            "article.teaser",
            ".teaser",
            "article",
            ".news-item",
            ".article-card",
            ".post-item",
            "[class*='article']",
            "div[class*='news']",
            ".story-card"
        ]
        
        article_cards = []
        used_selector = None
        
        for selector in article_selectors:
            try:
                cards = page.query_selector_all(selector)
                # Filter out cards that don't have both image and heading
                valid_cards = []
                for card in cards:
                    has_img = card.query_selector("img") is not None
                    has_heading = card.query_selector("h1, h2, h3, h4, h5") is not None
                    if has_img and has_heading:
                        valid_cards.append(card)
                
                if len(valid_cards) >= 3:
                    article_cards = valid_cards[:max_articles]
                    used_selector = selector
                    print(f" Found {len(valid_cards)} articles using selector: {selector}")
                    break
            except Exception as e:
                continue
        
   
        if not article_cards:
            print("  Using fallback method - searching all divs...")
            all_divs = page.query_selector_all("div")
            for div in all_divs:
                try:
                    img = div.query_selector("img")
                    heading = div.query_selector("h2, h3, h4")
                    if img and heading:
                        heading_text = heading.text_content().strip()
                        if len(heading_text) > 15:  # Substantial title
                            article_cards.append(div)
                            if len(article_cards) >= max_articles:
                                break
                except:
                    continue
            print(f"  Found {len(article_cards)} articles with fallback method")
        
        # Extract data from found articles
        print(f"\nExtracting data from {len(article_cards)} articles...")
        
        for idx, card in enumerate(article_cards, 1):
            try:
                # Extract title
                title = None
                for heading_tag in ["h2", "h3", "h1", "h4", "h5"]:
                    title_elem = card.query_selector(heading_tag)
                    if title_elem:
                        title_text = title_elem.text_content().strip()
                        if title_text and len(title_text) > 10:
                            title = title_text
                            break
                
   
                if not title:
                    link_elem = card.query_selector("a")
                    if link_elem:
                        title = link_elem.text_content().strip()
                
                if not title:
                    print(f"  [{idx}]  Skipped - no valid title")
                    continue
                
                # Extract image URL
                image_url = None
                img_elem = card.query_selector("img")
                if img_elem:
                
                    for attr in ["src", "data-src", "data-lazy-src", "data-original", "data-url"]:
                        url = img_elem.get_attribute(attr)
                        if url:
                            image_url = url
                            break
                    
                
                    if image_url:
                        if image_url.startswith("//"):
                            image_url = f"https:{image_url}"
                        elif image_url.startswith("/"):
                            image_url = f"https://ekantipur.com{image_url}"
                        elif not image_url.startswith("http"):
                            image_url = f"https://ekantipur.com/{image_url}"
                
          
                category = "मनोरञ्जन" 
                for cat_selector in [".category", ".tag", ".label", "[class*='category']", "span.badge"]:
                    cat_elem = card.query_selector(cat_selector)
                    if cat_elem:
                        cat_text = cat_elem.text_content().strip()
                        if cat_text and len(cat_text) < 30:
                            category = cat_text
                            break
                
                # Extract author
                author = None
                for auth_selector in [".author", ".by-line", ".writer", "[class*='author']", ".byline"]:
                    auth_elem = card.query_selector(auth_selector)
                    if auth_elem:
                        auth_text = auth_elem.text_content().strip()
                        auth_text = auth_text.replace("By", "").replace("by", "")
                        auth_text = auth_text.replace("द्वारा", "").strip()
                        if auth_text and len(auth_text) < 50 and auth_text != title:
                            author = auth_text
                            break

                if title:
                    article_data = {
                        "title": title,
                        "image_url": image_url,
                        "category": category,
                        "author": author
                    }
                    entertainment_news.append(article_data)
                    print(f"  [{idx}]  {title[:70]}...")
                
            except Exception as e:
                print(f"  [{idx}]  Error: {str(e)}")
                continue
        
        print(f"\n Successfully extracted {len(entertainment_news)} articles")
        
    except Exception as e:
        print(f"\n Error in entertainment news extraction: {str(e)}")
    
    return entertainment_news

def scrape_cartoon_of_the_day(page):
    
    #Locate and extract the cartoon of the day section
    cartoon_data = {}
    
    try:
        print("\nSearching for Cartoon of the Day...")
        
        # Navigate to homepage
        try:
            page.goto("https://ekantipur.com", wait_until="domcontentloaded", timeout=60000)
            print("   Homepage loaded")
        except PlaywrightTimeout:
            print(" Timeout loading homepage, trying anyway...")
        
        time.sleep(2)
        
        page.evaluate("window.scrollTo(0, 800)")
        time.sleep(1)
        
        # Search for cartoon section with multiple strategies
        cartoon_section = None
        
        cartoon_selectors = [
            ".cartoon",
            ".cartoon-section", 
            ".vyangya",
            "[class*='cartoon']",
            "[class*='vyangya']",
        ]
        
        for selector in cartoon_selectors:
            try:
                section = page.query_selector(selector)
                if section and section.query_selector("img"):
                    cartoon_section = section
                    print(f"  Found cartoon with selector: {selector}")
                    break
            except:
                continue
        
        if not cartoon_section:
            print("  Searching by Nepali text content...")
            all_sections = page.query_selector_all("div, section, article, aside")
            
            for section in all_sections:
                try:
                    
                    text = section.text_content() or ""
                    # Check for Nepali keywords
                    if any(word in text for word in ["व्यंग्य", "चित्र", "कार्टुन", "व्यंग्यचित्र"]):
                    
                        if section.query_selector("img"):
                            cartoon_section = section
                            print("   Found section with Nepali cartoon keywords")
                            break
                except:
                    continue
        
      
        if not cartoon_section:
            print("  Searching images for cartoon indicators...")
            all_images = page.query_selector_all("img")
            
            for img in all_images:
                try:
                    src = img.get_attribute("src") or ""
                    alt = img.get_attribute("alt") or ""
                    
                    if "cartoon" in src.lower() or "vyangya" in src.lower() or \
                       "cartoon" in alt.lower() or "व्यंग्य" in alt:
                        # Get parent container
                        cartoon_section = img.evaluate("el => el.closest('div, section, article')")
                        if cartoon_section:
                            print("   Found cartoon via image attributes")
                            break
                except:
                    continue
        
        # Extract data if found
        if cartoon_section:
            # Extract title
            title = "व्यंग्यिचित्र"  # Default
            for heading_tag in ["h2", "h3", "h4", "h5", ".title", ".heading"]:
                title_elem = cartoon_section.query_selector(heading_tag)
                if title_elem:
                    title_text = title_elem.text_content().strip()
                    if title_text and len(title_text) < 100:
                        title = title_text
                        break
            
            # Extract image URL
            image_url = None
            img_elem = cartoon_section.query_selector("img")
            if img_elem:
                for attr in ["src", "data-src", "data-lazy-src", "data-original"]:
                    url = img_elem.get_attribute(attr)
                    if url:
                        image_url = url
                        break
                
                if image_url:
                    if image_url.startswith("//"):
                        image_url = f"https:{image_url}"
                    elif image_url.startswith("/"):
                        image_url = f"https://ekantipur.com{image_url}"
                    elif not image_url.startswith("http"):
                        image_url = f"https://ekantipur.com/{image_url}"
            
            # Extract author
            author = None
            for auth_selector in [".author", ".cartoonist", ".by", "[class*='author']", "span"]:
                auth_elem = cartoon_section.query_selector(auth_selector)
                if auth_elem:
                    auth_text = auth_elem.text_content().strip()
                    if auth_text and auth_text != title and len(auth_text) < 50:
                        if "व्यंग्य" not in auth_text and "चित्र" not in auth_text:
                            author = auth_text
                            break
            
            cartoon_data = {
                "title": title,
                "image_url": image_url,
                "author": author
            }
            
            print(f"   Cartoon title: {title}")
            if image_url:
                print(f"   Image URL: {image_url[:60]}...")
            if author:
                print(f"   Author: {author}")
        else:
            print("   Could not locate cartoon section")
            cartoon_data = {
                "title": None,
                "image_url": None,
                "author": None
            }
            
    except Exception as e:
        print(f" Error in cartoon extraction: {str(e)}")
        cartoon_data = {
            "title": None,
            "image_url": None,
            "author": None
        }
    
    return cartoon_data

def main():
    #Main function to orchestrate the scraping process
    print("EKANTIPUR NEWS SCRAPER")
     
    with sync_playwright() as p:
        print("\n Launching browser...")
        
        browser = p.chromium.launch(
            headless=False, 
            slow_mo=50  
        )
        
        # Create context with realistic settings
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ne-NP",  
            timezone_id="Asia/Kathmandu"
        )
        
        page = context.new_page()
        page.set_default_timeout(90000)  
        
        try:
            # Scrape entertainment news
            entertainment_news = scrape_entertainment_news(page, max_articles=5)
            # Scrape cartoon of the day  
            cartoon_of_the_day = scrape_cartoon_of_the_day(page)
            
        finally:
    
            print("\n Closing browser...")
            browser.close()
        
        # Prepare output
        output_data = {
            "entertainment_news": entertainment_news,
            "cartoon_of_the_day": cartoon_of_the_day
        }

        # Save to JSON with proper encoding
        print("\n Saving to output.json...")
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            f.flush()  # Ensure data is written to buffer
            os.fsync(f.fileno())  # Force write to disk
        print("   File saved successfully")
        
        # Print summary
        print(" SCRAPING COMPLETED!")
        print(f" Entertainment articles: {len(entertainment_news)}")
        print(f"Cartoon of the day: {' Found' if cartoon_of_the_day.get('image_url') else 'Not found'}")
        print(f" Output: output.json") 
        
        # Show extracted articles
        if entertainment_news:
            print("\n Extracted Articles:")
            for i, article in enumerate(entertainment_news, 1):
                print(f"  {i}. {article['title'][:75]}...")
                if article.get('author'):
                    print(f" Author: {article['author']}")
        else:
            print("No articles extracted!")
        
        # Display the actual JSON output
        print(" OUTPUT.JSON CONTENT:")
        print(json.dumps(output_data, ensure_ascii=False, indent=2))
        
if __name__ == "__main__":
    main()