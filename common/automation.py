from playwright.sync_api import sync_playwright




def start_aetna_automation(extracted_data):
    print("Automation started...")
    
    with sync_playwright() as p:
        # ✅ NORMAL BROWSER - No persistent context, no profile issues!
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox", 
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-web-security",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        # ✅ Fresh context har baar
        context = browser.new_context(
            viewport={'width': 1366, 'height': 768}
        )
        page = context.new_page()
        
        page.goto("https://extaz-oci.aetna.com/pocui/join-the-aetna-network")
        print("✅ Aetna site opened successfully!")
        
        # Data fill karo
        print(f"Provider: {extracted_data.get('provider_name', 'N/A')}")
        print(f"NPI: {extracted_data.get('npi', 'N/A')}")
        
        page.wait_for_timeout(10000)
        
        browser.close()
        print("✅ Automation finished!")
    return True

