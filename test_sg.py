from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        print("Launching headless=True")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36")
        page = context.new_page()
        
        url = "https://www.sg.gov.cn/sgtjj/gkmlpt/index"
        print(f"Going to {url}")
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        
        print("Page Title:", page.title())
        print("URL:", page.url)
        html = page.content()
        print("HTML length:", len(html))
        print("HTML preview:", html[:200])
        
        print("\nChecking for items...")
        items = page.locator(".table-content tbody tr").count()
        print(f"Found {items} items matching .table-content tbody tr")
        
        browser.close()

if __name__ == "__main__":
    test()
