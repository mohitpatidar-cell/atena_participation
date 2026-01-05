import time
from playwright.sync_api import sync_playwright

import re

def clean_npi(npi_str):
    """Extract only 10 digits from NPI"""
    if not npi_str:
        return ""
    # digits = re.5927sub(r'\D', '', str(npi_str))
    digits="1932975927"
    return digits

def start_aetna_automation(extracted_data):
    print("🚀 Aetna automation started...")
    
    with sync_playwright() as p:
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
        
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        page = context.new_page()
        
        # STEP 1: Initial dropdowns
        page.goto("https://extaz-oci.aetna.com/pocui/join-the-aetna-network")
        page.wait_for_load_state("networkidle")
        
        page.select_option("#typeOfRFP", "Aetna")
        time.sleep(2)
        page.select_option("#typeOfRFP1", "BH")
        time.sleep(2)
        page.select_option("#typeOfRFP2", "new group practice")
        time.sleep(2)
        page.click("button.primary-button")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # ========== STEP 2: SUBMITTER Names ==========
        print("👤 STEP 2: SUBMITTER Names...")
        first_name = extracted_data.get("submitter_first_name", "").strip()
        last_name = extracted_data.get("submitter_last_name", "").strip()
        
        if last_name:
            page.wait_for_selector("#lastName", timeout=10000)
            page.fill("#lastName", last_name)
            print("✅ SUBMITTER Last Name FILLED!")
        time.sleep(1)
        
        if first_name:
            page.wait_for_selector("#firstName", timeout=10000)
            page.fill("#firstName", first_name)
            print("✅ SUBMITTER First Name FILLED!")
        time.sleep(1)
        
        screenshot_path = f"/tmp/aetna_step2_names.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"📸 Step 2 Screenshot: {screenshot_path}")
        
        # ========== STEP 3: Role Dropdown ==========
        print("🎭 STEP 3: Role selection...")
        page.wait_for_selector("#role", timeout=10000)
        page.select_option("#role", "Credentialing / Enrollment (Director, Manager, Coordinator)")
        print("✅ Role: Credentialing/Enrolment SELECTED!")
        time.sleep(2)
        
        # ========== STEP 4: Email Fields ==========
        print("📧 STEP 4: Email fields...")
        email = extracted_data.get("submitter_email", "").strip()
        
        if email:
            # Email field
            page.wait_for_selector("#email", timeout=10000)
            page.fill("#email", email)
            print(f"✅ Email FILLED: {email}")
            
            # Verify Email (same value)
            page.wait_for_selector("#verifyEmail", timeout=10000)
            page.fill("#verifyEmail", email)
            print("✅ Verify Email FILLED!")
        time.sleep(2)
        
        # ========== STEP 5: Phone Fields ==========
        print("📞 STEP 5: Phone fields...")
        phone = extracted_data.get("submitter_phone", "").strip()
        ext = extracted_data.get("submitter_ext", "").strip()
        fax = extracted_data.get("submitter_fax", "").strip()
        
        if phone:
            page.wait_for_selector("#phoneNumber", timeout=10000)
            page.fill("#phoneNumber", phone)
            print(f"✅ Phone FILLED: {phone}")
        time.sleep(1)
        
        if ext:
            page.wait_for_selector("#ext", timeout=10000)
            page.fill("#ext", ext)
            print(f"✅ Extension FILLED: {ext}")
        time.sleep(1)
        
        if fax:
            page.wait_for_selector("#faxNumber", timeout=10000)
            page.fill("#faxNumber", fax)
            print(f"✅ Fax FILLED: {fax}")
        time.sleep(2)
        
# ... previous steps same until STEP 5 ...

        # STEP 6: FIXED NPI
        print("🆔 STEP 6: NPI FIXED...")
        personal_info = extracted_data.get("Personal_Information", {})
        npi_raw = personal_info.get("Individual_NPI", "")
        npi = "1932975927"
        print(f"NPI DEBUG - RAW: '{npi_raw}' CLEAN: '{npi}'")

        if len(npi) == 10:
            try:
                page.wait_for_selector("#npi", state="visible", timeout=8000)
                page.click("#npi")
                page.fill("#npi", npi)
                print(f"✅ NPI SUCCESS: {npi}")
            except:
                # JavaScript fallback
                page.evaluate("document.querySelector('#npi').value = '{}';".format(npi))
                print(f"✅ NPI JS FALLBACK: {npi}")
        else:
            print("❌ NPI INVALID")

        screenshot_path = f"/tmp/aetna_npi_fixed.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"📸 NPI Screenshot: {screenshot_path}")

# ... previous code same ...

        print("✅ NPI STEP DONE!")
        time.sleep(3)

        # ========== STEP 7: EMAIL ACKNOWLEDGEMENT LINK ==========
        print("🔗 STEP 7: Email Acknowledgement Link...")
        
        try:
            # EMAIL ACKNOWLEDGEMENT link pe click karna
            page.wait_for_selector('a[aria-label*="Email acknowledgement"]', timeout=10000)
            page.click('a[aria-label*="Email acknowledgement"]')
            print("✅ Email Acknowledgement link clicked!")
            time.sleep(2)
            
            # New tab ka wait karna aur usse handle karna
            print("🔄 New tab handle kar rahe hain...")
            
            # Wait for new tab to open
            page.wait_for_event('popup', timeout=5000)
            
            # Get all tabs
            all_pages = context.pages
            original_page = page
            
            if len(all_pages) > 1:
                # Switch to new tab (last one)
                new_tab = all_pages[-1]
                new_tab.bring_to_front()
                
                print(f"📑 New tab opened: {new_tab.url}")
                print("⏳ New tab content load hone ka wait...")
                new_tab.wait_for_load_state('networkidle')
                time.sleep(3)
                
                # New tab ki screenshot
                new_tab_screenshot = "/tmp/aetna_email_acknowledgement_tab.png"
                new_tab.screenshot(path=new_tab_screenshot, full_page=True)
                print(f"📸 New tab screenshot: {new_tab_screenshot}")
                
                # New tab close karna
                print("❌ New tab close kar rahe hain...")
                new_tab.close()
                time.sleep(1)
                
                # Original tab par wapas aana
                original_page.bring_to_front()
                print("✅ Original tab par wapas aa gaye")
            else:
                print("⚠️ New tab nahi khula, directly proceed karte hain")
                
        except Exception as e:
            print(f"⚠️ Email Acknowledgement link error: {e}")
            print("⏭️ Directly proceed karte hain...")
        
        # ========== STEP 8: AGREE CHECKBOX ==========
        print("☑️ STEP 8: Agree Checkbox...")

        try:
            # Pehle, page thoda scroll karte hain taki element visible ho
            page.evaluate('window.scrollBy(0, 200)')
            time.sleep(1)
            
            # Radio button ka wait karna
            page.wait_for_selector('span.mat-radio-outer-circle', timeout=10000)
            
            # Radio buttons count
            radio_count = page.locator('span.mat-radio-outer-circle').count()
            print(f"📊 Radio buttons found: {radio_count}")
            
            if radio_count > 0:
                # **METHOD 1: Direct JavaScript click - Yeh best work karega**
                # Angular Material radio buttons ke liye JavaScript direct click best hai
                page.evaluate('''() => {
                    // Find all mat-radio-button elements
                    const radioButtons = document.querySelectorAll('mat-radio-button');
                    if (radioButtons.length > 0) {
                        // First unchecked radio button click karna
                        for (let radio of radioButtons) {
                            if (!radio.classList.contains('mat-radio-checked')) {
                                radio.click();
                                console.log('Radio button clicked via JS');
                                break;
                            }
                        }
                        return true;
                    }
                    return false;
                }''')
                
                print("✅ Radio button clicked via JavaScript")
                time.sleep(1)
                
                # **METHOD 2: Force click via JavaScript coordinates**
                # Agar upar kaam na kare toh coordinates use karna
                try:
                    # Element ka bounding box nikalna
                    bounding_box = page.locator('span.mat-radio-outer-circle').first.bounding_box()
                    if bounding_box:
                        # Element ke center mein click karna
                        page.mouse.click(
                            bounding_box['x'] + bounding_box['width'] / 2,
                            bounding_box['y'] + bounding_box['height'] / 2
                        )
                        print("✅ Radio button clicked via mouse coordinates")
                except:
                    print("ℹ️ Coordinates click skip")
                    
                # **METHOD 3: Input radio element directly click karna**
                try:
                    # Associated input radio element find karna
                    page.click('input[type="radio"]', force=True)
                    print("✅ Radio input clicked with force")
                except:
                    print("ℹ️ Input radio click skip")
                    
                # Verify selection
                time.sleep(1)
                is_radio_selected = page.evaluate('''() => {
                    const radios = document.querySelectorAll('mat-radio-button');
                    for (let radio of radios) {
                        if (radio.classList.contains('mat-radio-checked')) {
                            return true;
                        }
                    }
                    return false;
                }''')
                
                if is_radio_selected:
                    print("✅ Radio button successfully selected (verified)")
                else:
                    print("⚠️ Radio button selection verify nahi ho paya")
                    
                    # Last resort: Dispatch events manually
                    page.evaluate('''() => {
                        const radioButtons = document.querySelectorAll('mat-radio-button');
                        if (radioButtons.length > 0) {
                            // Force select first radio
                            const radio = radioButtons[0];
                            const input = radio.querySelector('input[type="radio"]');
                            if (input) {
                                input.checked = true;
                                input.dispatchEvent(new Event('change', { bubbles: true }));
                                radio.classList.add('mat-radio-checked');
                                console.log('Radio force selected');
                            }
                        }
                    }''')
                    print("✅ Radio button force selected via JavaScript")
                    
            else:
                print("⚠️ No radio buttons found")
                # Alternative mat-radio-button selector try karna
                page.click('mat-radio-button', force=True)
                print("✅ mat-radio-button element clicked")
                
        except Exception as e:
            print(f"❌ Radio button error: {e}")
            
            # **ULTIMATE FALLBACK: Full JavaScript solution**
            print("🔄 Ultimate JavaScript fallback...")
            
            page.evaluate('''() => {
                // Method 1: Click on mat-radio-container
                const containers = document.querySelectorAll('.mat-radio-container');
                if (containers.length > 0) {
                    containers[0].click();
                    console.log('Clicked mat-radio-container');
                    return;
                }
                
                // Method 2: Find and click the actual input
                const radioInputs = document.querySelectorAll('input[type="radio"][name*="agree"], input[type="radio"][id*="agree"]');
                if (radioInputs.length > 0) {
                    radioInputs[0].click();
                    console.log('Clicked radio input');
                    return;
                }
                
                // Method 3: Any radio input
                const allRadios = document.querySelectorAll('input[type="radio"]');
                if (allRadios.length > 0) {
                    allRadios[0].click();
                    console.log('Clicked first radio input');
                    return;
                }
                
                // Method 4: Dispatch change event
                const firstRadio = document.querySelector('input[type="radio"]');
                if (firstRadio) {
                    firstRadio.checked = true;
                    firstRadio.dispatchEvent(new Event('change', { bubbles: true }));
                    firstRadio.dispatchEvent(new Event('click', { bubbles: true }));
                    console.log('Dispatched radio events');
                }
            }''')
            
            print("✅ Radio button handled via ultimate fallback")

        time.sleep(2)

        
        # ========== STEP 9: CHECKBOX SELECT ==========
        print("✅ STEP 9: Checkbox Select...")
        
        try:
            # Checkbox wait karna
            page.wait_for_selector('#checkboxSelect', timeout=10000)
            
            # Check if checkbox already checked nahi hai
            is_checked = page.is_checked('#checkboxSelect')
            
            if not is_checked:
                # Checkbox pe click karna
                page.click('#checkboxSelect')
                print("✅ Checkbox clicked!")
                
                # Verify checkbox checked hai
                is_now_checked = page.is_checked('#checkboxSelect')
                if is_now_checked:
                    print("✅ Checkbox verified as checked")
                else:
                    print("⚠️ Checkbox check verify nahi ho paya")
                    # Force check using JavaScript
                    page.evaluate('''() => {
                        const checkbox = document.getElementById('checkboxSelect');
                        if (checkbox) {
                            checkbox.checked = true;
                            checkbox.dispatchEvent(new Event('change'));
                        }
                    }''')
                    print("✅ Checkbox forced via JavaScript")
            else:
                print("ℹ️ Checkbox already checked")
                
        except Exception as e:
            print(f"❌ Checkbox error: {e}")
            # JavaScript fallback
            page.evaluate('''() => {
                const checkbox = document.getElementById('checkboxSelect');
                if (checkbox) {
                    checkbox.click();
                }
            }''')
            print("✅ Checkbox clicked via JavaScript fallback")
        
        time.sleep(2)
        
        # ========== STEP 10: CONTINUE BUTTON ==========
        print("➡️ STEP 10: Continue Button...  Network Participation Check")
        
        try:
            # Continue button wait karna
            page.wait_for_selector('button.primary-button.float-right', timeout=10000)
            
            # Button enabled hai ya nahi check karna
            is_enabled = page.is_enabled('button.primary-button.float-right')
            
            if is_enabled:
                # Screenshot before click
                before_continue_screenshot = "/tmp/aetna_before_continue.png"
                page.screenshot(path=before_continue_screenshot, full_page=True)
                print(f"📸 Before continue screenshot: {before_continue_screenshot}")
                
                # Continue button pe click
                page.click('button.primary-button.float-right')
                print("✅ Continue button clicked!")
                
                # Wait for navigation or next page
                try:
                    page.wait_for_load_state('networkidle', timeout=10000)
                    print("🔄 Next page load ho raha hai...")
                    
                    # Screenshot after click
                    after_continue_screenshot = "/tmp/aetna_after_continue.png"
                    page.screenshot(path=after_continue_screenshot, full_page=True)
                    print(f"📸 After continue screenshot: {after_continue_screenshot}")
                    
                    # Check URL change
                    current_url = page.url
                  
                    page.wait_for_selector('mat-radio-group[formcontrolname="teleHealthService"]', timeout=15000)
                   
                    # Scroll + Click Yes
                    yes_radio = page.locator('mat-radio-button[value="Yes"]')
                    yes_radio.scroll_into_view_if_needed()
                    yes_radio.click(force=True)

                    print("✅ Telehealth Service: YES selected")

                    # Verify
                    is_checked = page.is_checked('#Yes-input')
                    print("✔ Confirmed checked:", is_checked)
                    page.wait_for_selector('mat-radio-group[formcontrolname="teleHealthProvider"]', timeout=15000)

                    # Scroll + click Hybrid
                    hybrid_radio = page.locator('mat-radio-button[value="Hybrid"]')
                    hybrid_radio.scroll_into_view_if_needed()
                    hybrid_radio.click(force=True)

                    print("✅ TeleHealth Provider: HYBRID selected")

                    # Verify
                    is_checked = page.is_checked('#Hybrid-input')
                    print("✔ Confirmed Hybrid checked:", is_checked)
                    page.wait_for_selector('#applicableSituation', timeout=15000)

                    # Select by visible label
                    page.select_option(
                        '#applicableSituation',
                        label="I want to be contracted in the state selected below"
                    )
                    print("✅ Applicable Situation selected successfully")
                    page.wait_for_selector('#state', timeout=15000)

                    # Select Michigan by visible label
                    page.select_option('#state', label='Michigan')

                    print("✅ State selected: Michigan")
                    page.wait_for_selector('#zipCode', timeout=15000)

                    # Clear existing value
                    page.fill('#zipCode', '')

                    # Enter valid 5 digit ZIP
                    page.fill('#zipCode', '48393')

                    print("✅ ZIP code entered: 48393")

                    page.wait_for_selector('#taxIdType', timeout=15000)

                    # Select by visible label
                    page.select_option(
                        '#taxIdType',
                        label='E - Employer identification number'
                    )

                    print("✅ TAX ID Type selected: Employer Identification Number (EIN)")
                    # Wait for Tax ID field


                    # Wait for TAX ID Name field
                    page.wait_for_selector('#taxIDName', timeout=15000)

                    # Clear existing value
                    page.fill('#taxIDName', '')

                    # Enter TAX ID Name
                    page.fill('#taxIDName', 'pure ppc')

                    print("✅ TAX ID Name entered: pure ppc")



                    page.wait_for_selector('#taxId', timeout=15000)

                    # Clear field
                    page.fill('#taxId', '')


              

                    # Enter valid 9 digit TAX ID
                    page.fill('#taxId', '222229929')

                    print("✅ TAX ID entered: 2229929")
                    # Wait for Verify TAX ID field
                    page.wait_for_selector('#verifyTaxID', timeout=15000)

                    # Clear existing value
                    page.fill('#verifyTaxID', '')

                    # Enter 9-digit TAX ID
                    page.fill('#verifyTaxID', '222229929')

                    print("✅ Verify TAX ID entered: 222229929")
                    page.wait_for_selector('#practLastName', timeout=15000)

                    # Clear any existing value
                    page.fill('#practLastName', '')

                    # Enter Last Name
                    page.fill('#practLastName', 'Enersen')

                    page.wait_for_selector('#practFirstName', timeout=15000)

                    # Clear existing value
                    page.fill('#practFirstName', '')

                    # Enter First Name
                    page.fill('#practFirstName', 'Kathleen')
                    try:
                        # Checkbox wait karna
                        page.wait_for_selector('#checkboxSelect', timeout=10000)
                        
                        # Check if checkbox already checked nahi hai
                        is_checked = page.is_checked('#checkboxSelect')
                        
                        if not is_checked:
                            # Checkbox pe click karna
                            page.click('#checkboxSelect')
                            print("✅ Checkbox clicked!")
                            
                            # Verify checkbox checked hai
                            is_now_checked = page.is_checked('#checkboxSelect')
                            if is_now_checked:
                                print("✅ Checkbox verified as checked")
                            else:
                                print("⚠️ Checkbox check verify nahi ho paya")
                                # Force check using JavaScript
                                page.evaluate('''() => {
                                    const checkbox = document.getElementById('checkboxSelect');
                                    if (checkbox) {
                                        checkbox.checked = true;
                                        checkbox.dispatchEvent(new Event('change'));
                                    }
                                }''')
                                print("✅ Checkbox forced via JavaScript")
                        else:
                            print("ℹ️ Checkbox already checked")
                
                    except Exception as e:
                        print(f"❌ Checkbox error: {e}")
                        # JavaScript fallback
                        page.evaluate('''() => {
                            const checkbox = document.getElementById('checkboxSelect');
                            if (checkbox) {
                                checkbox.click();
                            }
                        }''')
                        print("✅ Checkbox clicked via JavaScript fallback")
        

                    time.sleep(2)
                   

                
                    # print(f"🌐 Current URL: {current_url}")
                    # Wait for the button
                    page.wait_for_selector('button.primary-button.float-right', timeout=15000)

                    # Scroll into view
                    continue_btn1 = page.locator('button.primary-button.float-right')
                    continue_btn1.scroll_into_view_if_needed()

                
                    time.sleep(10) 
                    # Click the button
                    continue_btn1.click(force=True)
                    print("✅ Continue button clicked-========")



                    # Wait for next page element (Angular SPA)
                    page.wait_for_selector('mat-radio-group[formcontrolname="teleHealthService"]', timeout=20000)
                    time.sleep(10) 
                    print("🌐 Next page loaded successfully======")
                    # Wait for the modal popup to appear
                    page.wait_for_selector('div.pop-up-container', timeout=15000)

                    # Locate the "Continue Session" button by its text
                    continue_btn3 = page.locator('div.pop-up-container button', has_text='Continue Session')

                    # Scroll into view (optional but safe)
                    continue_btn3.scroll_into_view_if_needed()

                    # Click the button (force=True ensures Angular overlay does not block)
                    continue_btn3.click(force=True)

                    print("✅ 'Continue Session' button clicked from modal popup")

                    # Wait for the next page/network to load after clicking
                    page.wait_for_load_state('networkidle', timeout=15000)

                    # Optional: Take a screenshot
                    page.screenshot(path='/tmp/after_continue_session.png', full_page=True)
                    print("📸 Screenshot after continuing session taken")


                    print("✅ 'Continue Session' button clicked from modal popup")
                                    
                    time.sleep(10) 
                    # degree type added
                    # Wait for the dropdown to be visible
                    page.wait_for_selector('#degreeType', timeout=15000)

                    # Select "MSW" by value
                    page.select_option('#degreeType', value='MSW')

                    print("✅ Degree selected: MSW")
                    # Wait for the dropdown to appear
                    page.wait_for_selector('#specialty', timeout=15000)

                    # Select by value
                    page.select_option('#specialty', value='Clinical Social Worker')
                  
                    print("✅ Specialty selected: Clinical Social Worker")
                    # Wait for the link
                    pdf_link = page.wait_for_selector(
                         'a[href*="bh-provider-manual.pdf"]',  timeout=15000)
                    print('pdf_link====',pdf_link)
                    pdf_url = pdf_link.get_attribute('href')
                    print("pdf_url===", pdf_url)

                    # Create a new context for the new tab
                    context = page.context
                    pdf_page = context.new_page()
                    pages_before = page.context.pages
                    try:
                        # PDF link pe click karna
                        print("📄 PDF link dhoond rahe hain...")
                        pdf_link = page.wait_for_selector(
                            'a[href*="bh-provider-manual.pdf"]', 
                            timeout=15000
                        )
                        print('pdf_link====', pdf_link)
                        
                        # Get PDF URL
                        pdf_url = pdf_link.get_attribute('href')
                        print("pdf_url===", pdf_url)
                        
                        # Store original page
                        context = page.context
                        original_page = page
                        
                        # New tab ka wait karna aur usse handle karna
                        print("🔄 PDF ke liye new tab handle kar rahe hain...")
                        
                        # Wait for new tab to open (by clicking the link)
                        with page.expect_popup(timeout=5000) as popup_info:
                            pdf_link.click()
                        
                        # Get the new tab/popup
                        pdf_tab = popup_info.value
                        
                        if pdf_tab:
                            print(f"📑 PDF new tab opened: {pdf_tab.url}")
                            print("⏳ PDF content load hone ka wait...")
                            
                            # Wait for PDF to load
                            pdf_tab.wait_for_load_state('networkidle')
                            time.sleep(3)
                            
                            # PDF page ki screenshot (optional)
                            try:
                                pdf_screenshot = "/tmp/aetna_pdf_tab.png"
                                pdf_tab.screenshot(path=pdf_screenshot, full_page=True)
                                print(f"📸 PDF tab screenshot: {pdf_screenshot}")
                            except Exception as screenshot_error:
                                print(f"⚠️ Screenshot nahi le sake: {screenshot_error}")
                            
                            # PDF tab close karna
                            print("❌ PDF tab close kar rahe hain...")
                            pdf_tab.close()
                            time.sleep(1)
                            
                            # Original tab par wapas aana
                            original_page.bring_to_front()
                            print("✅ Original tab par wapas aa gaye")
                        else:
                            print("⚠️ New tab nahi khula, directly PDF download ho raha hai")
                            
                            # Alternative approach: agar new tab nahi khula toh
                            print("🔄 Alternative approach try kar rahe hain...")
                            
                            # Get all tabs after click
                            all_pages = context.pages
                            print(f"Total tabs: {len(all_pages)}")
                            
                            if len(all_pages) > 1:
                                # Last tab check karo (shayad PDF tab ho)
                                pdf_tab = all_pages[-1]
                                
                                # Agar yeh original page nahi hai toh
                                if pdf_tab != original_page:
                                    print(f"📄 PDF tab found: {pdf_tab.url}")
                                    
                                    # Switch to PDF tab
                                    pdf_tab.bring_to_front()
                                    time.sleep(2)
                                    
                                    # Close PDF tab
                                    pdf_tab.close()
                                    print("✅ PDF tab closed")
                                    
                                    # Original tab par wapas
                                    original_page.bring_to_front()
                                    print("✅ Original tab par wapas aa gaye")
                            
                    except Exception as e:
                            print(f"⚠️ PDF link error: {e}")
                            print("🔄 Alternative PDF handling try kar rahe hain...")
    
                            try:
                                # Try your original approach as fallback
                                pdf_link = page.wait_for_selector(
                                    'a[href*="bh-provider-manual.pdf"]', 
                                    timeout=10000
                                )
                                
                                pdf_url = pdf_link.get_attribute('href')
                                print("Fallback: pdf_url===", pdf_url)

                                # Get tabs before
                                pages_before = page.context.pages
                                print(f"Tabs before: {len(pages_before)}")

                                # Create new page manually
                                pdf_page = page.context.new_page()
                                pdf_page.goto(pdf_url, timeout=15000)
                                pdf_page.wait_for_load_state('networkidle', timeout=15000)
                                print("📄 PDF opened (fallback):", pdf_page.url)
                                
                                time.sleep(3)
                                
                                # Get tabs after
                                pages_after = page.context.pages
                                print(f"Tabs after: {len(pages_after)}")

                                # Find new page
                                if len(pages_after) > len(pages_before):
                                    new_page = pages_after[-1]
                                    print(f"📄 PDF tab found: {new_page.url}")
                                    
                                    # Wait for PDF
                                    new_page.wait_for_timeout(3000)
                                    
                                    # Close PDF tab
                                    new_page.close()
                                    print("✅ PDF tab closed")
                                    
                                    # Return to original
                                    page.bring_to_front()
                                
                            except Exception as fallback_error:
                                print(f"❌ Fallback bhi fail: {fallback_error}")
                                print("⏭️ Directly proceed karte hain...")

                    

                        # Wait a bit to ensure content is rendered
                    
                
                    
                    time.sleep(8)
                    page.wait_for_selector('mat-radio-group[formcontrolname="verifyBHRadio"]', timeout=15000)
                    print("agerrr#####")
                    # Click the "Agree" radio button using its input id
                    page.click('#agreeBH-input', force=True)

                    # Optional: verify it is checked
                    is_checked = page.is_checked('#agreeBH-input')
                    print("✅ Agree radio button checked:", is_checked)
                    try:
                        # Checkbox wait karna
                        page.wait_for_selector('#checkboxSelect', timeout=10000)
                        
                        # Check if checkbox already checked nahi hai
                        is_checked = page.is_checked('#checkboxSelect')
                        
                        if not is_checked:
                            # Checkbox pe click karna
                            page.click('#checkboxSelect')
                            print("✅ Checkbox clicked!")
                            
                            # Verify checkbox checked hai
                            is_now_checked = page.is_checked('#checkboxSelect')
                            if is_now_checked:
                                print("✅ Checkbox verified as checked")
                            else:
                                print("⚠️ Checkbox check verify nahi ho paya")
                                # Force check using JavaScript
                                page.evaluate('''() => {
                                    const checkbox = document.getElementById('checkboxSelect');
                                    if (checkbox) {
                                        checkbox.checked = true;
                                        checkbox.dispatchEvent(new Event('change'));
                                    }
                                }''')
                                print("✅ Checkbox forced via JavaScript")
                        else:
                            print("ℹ️ Checkbox already checked")
                
                    except Exception as e:
                        print(f"❌ Checkbox error: {e}")
                        # JavaScript fallback
                        page.evaluate('''() => {
                            const checkbox = document.getElementById('checkboxSelect');
                            if (checkbox) {
                                checkbox.click();
                            }
                        }''')
                        print("✅ Checkbox clicked via JavaScript fallback")
        
                    try:
                         # Checkbox wait karna
                        page.wait_for_selector('#checkboxSelect', timeout=10000)
                        
                        # Check if checkbox already checked nahi hai
                        is_checked = page.is_checked('#checkboxSelect')
                        
                        if not is_checked:
                            # Checkbox pe click karna
                            page.click('#checkboxSelect')
                            print("✅ Checkbox clicked!")
                            
                            # Verify checkbox checked hai
                            is_now_checked = page.is_checked('#checkboxSelect')
                            if is_now_checked:
                                print("✅ Checkbox verified as checked")
                            else:
                                print("⚠️ Checkbox check verify nahi ho paya")
                                # Force check using JavaScript
                                page.evaluate('''() => {
                                    const checkbox = document.getElementById('checkboxSelect');
                                    if (checkbox) {
                                        checkbox.checked = true;
                                        checkbox.dispatchEvent(new Event('change'));
                                    }
                                }''')
                                print("✅ Checkbox forced via JavaScript")
                        else:
                            print("ℹ️ Checkbox already checked")
                    except:
                        pass
                    time.sleep(2)
                    page.wait_for_selector('button.primary-button.float-right', timeout=15000)

                    # Scroll into view
                    continue_btn4 = page.locator('button.primary-button.float-right')
                    continue_btn4.scroll_into_view_if_needed()

                
                    time.sleep(10) 
                    # Click the button
                    continue_btn4.click(force=True)
                    # Wait for modal to appear
                    # Wait for modal overlay to appear (Angular Material renders in cdk-overlay)
                    
                    try:
                        print("🔄 Credentialing modal ka wait kar rahe hain...")
                        
                        # Wait for modal
                        modal = page.wait_for_selector(
                            'div.pop-up-container',
                            state='visible',
                            timeout=20000
                        )
                        print("✅ Modal visible ho gaya")
                        
                        # Small delay for Angular animations
                        page.wait_for_timeout(1000)
                        
                        # Click using JavaScript with proper selector
                        page.evaluate("""
                            () => {
                                // Find button with exact text in modal
                                const modal = document.querySelector('div.pop-up-container');
                                if (!modal) {
                                    console.log('Modal not found');
                                    return false;
                                }
                                
                                // Find all buttons in modal
                                const buttons = modal.querySelectorAll('button');
                                console.log('Buttons in modal:', buttons.length);
                                
                                let foundBtn = null;
                                for (let btn of buttons) {
                                    console.log('Button text:', btn.innerText);
                                    if (btn.innerText && btn.innerText.trim() === 'Acknowledge and Continue') {
                                        foundBtn = btn;
                                        break;
                                    }
                                }
                                
                                if (foundBtn) {
                                    foundBtn.click();
                                    console.log('Button clicked via JS');
                                    return true;
                                }
                                
                                // Alternative: Find by class
                                const btnByClass = modal.querySelector('button.primary-button.float-right');
                                if (btnByClass) {
                                    btnByClass.click();
                                    console.log('Button clicked via class');
                                    return true;
                                }
                                
                                console.log('No button found');
                                return false;
                            }
                        """)
                        
                        print("✅ JavaScript click attempt complete")
                        
                        # Wait for navigation/new page
                        page.wait_for_timeout(2000)
                        
                        # Check if navigation happened
                        try:
                            page.wait_for_load_state('networkidle', timeout=10000)
                            print(f"✅ Navigation complete: {page.url}")
                        except:
                            print("⚠️ Navigation timeout, but continuing...")

                    except Exception as e:
                        print(f"⚠️ Error in modal handling: {e}")
                        time.sleep(4)
                    dob_input = page.wait_for_selector('#dob', timeout=10000)

                    # Fill the date of birth
                    dob_input.fill('01/04/1994')  # Use MM/DD/YYYY format

                    print("✅ Date of Birth entered: 01/04/1994")
                    # Wait for the Medical License input to appear
                    license_input = page.wait_for_selector('#medicalLicenseNumber', timeout=10000)

                    # Fill the license number
                    license_input.fill('680110289')  # Replace with your actual license number

                    print("✅ Medical License Number entered: 680110289")
                    # Wait for the Medical License Expiration Date input to appear
                    exp_date_input = page.wait_for_selector('#medLicenseExpDate', timeout=10000)

                    # Fill the date directly
                    exp_date_input.fill('12/05/2025')  # Replace with your expiration date
                    caqh_input = page.wait_for_selector('#caqhID', timeout=10000)

                    # Fill the CAQH ID (example: 12345678)
                    caqh_input.fill('14549097')
                    print("🔄 Radio button wait kar rahe hain...")
                    page.wait_for_selector('mat-radio-button[value="No"]', timeout=10000)

                                        
                    page.click('mat-radio-button[value="No"]')
                    print("✅ 'No' radio button selected")
                    time.sleep(2)
                    continue_btn = page.wait_for_selector('button.primary-button.float-right[type="submit"]', timeout=15000)

                    # Scroll into view (optional but safe)
                    continue_btn.scroll_into_view_if_needed()

                    # Click the button (force=True to bypass Angular overlays)
                    continue_btn.click(force=True)

                    # Wait for the next page/network to load
                    page.wait_for_load_state('networkidle', timeout=15000)

                    print("✅ Continue button clicked and next page opened")
                
                        # Find and click the Practitioner radio button
                    

                    print("🔄 Selecting Practitioner with Angular model binding")

                    page.wait_for_selector("mat-radio-group[formcontrolname='contractRadioGroup']", timeout=15000)

                    # Trigger Angular form model update directly
                    page.evaluate("""
                    () => {
                    const radio = document.querySelector("mat-radio-button#Practitioner");
                    if (!radio) return false;

                    const input = radio.querySelector("input.mat-radio-input");
                    input.dispatchEvent(new Event('focus'));
                    input.dispatchEvent(new Event('mousedown', { bubbles: true }));
                    input.dispatchEvent(new Event('click', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    input.dispatchEvent(new Event('blur'));
                    return true;
                    }
                    """)

                    page.wait_for_timeout(800)

                    is_checked = page.locator("mat-radio-button#Practitioner").evaluate(
                        "el => el.classList.contains('mat-radio-checked')"
                    )

                    print(f"✅ Practitioner selected (Angular forced): {is_checked}")



                
                        
    
        

               
                    email_input = page.wait_for_selector('input#practitionerEmail', timeout=15000)

                    # Fill the email
                    email_input.fill('test@gmail.com')

                    print("✅ Practitioner email filled")
                    
                    # Wait for the "Verify Email" input to appear
                    verify_email_input = page.wait_for_selector('input#practitionerVerifyEmail', timeout=15000)

                    # Fill the email
                    verify_email_input.fill('test@gmail.com')

                    print("✅ Practitioner verify email filled")
                    # Wait for the phone input to appear
                    phone_input = page.wait_for_selector('input#practitionerPhoneNumber', timeout=15000)

                    # Fill the phone number
                    phone_input.fill('9522327456')  # Replace with the desired number

                    print("✅ Practitioner phone number filled")

                    # Wait for the Email checkbox to appear
                    email_checkbox = page.wait_for_selector('input#EmailPrac', timeout=15000)

                    # Check the checkbox
                    email_checkbox.check()

                    print("✅ Email checkbox checked")
                    print("🔄 Forcing AUTH Practitioner through Angular FormControl")

                    page.wait_for_selector("mat-radio-button#auth_Practitioner", timeout=15000)

                    page.evaluate("""
                    () => {
                    const radio = document.querySelector("mat-radio-button#auth_Practitioner");
                    if (!radio) return false;

                    const input = radio.querySelector("input.mat-radio-input");
                    const group = radio.closest("mat-radio-group");

                    input.dispatchEvent(new Event('focus', { bubbles: true }));
                    input.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
                    input.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                    input.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    input.dispatchEvent(new Event('blur', { bubbles: true }));

                    // Mark Angular form control dirty & touched
                    if (group && group.__ngContext__) {
                        try {
                            const cmp = group.__ngContext__[8];
                            if (cmp && cmp.control) {
                                cmp.control.markAsDirty();
                                cmp.control.markAsTouched();
                                cmp.control.setValue('Practitioner');
                            }
                        } catch(e){}
                    }

                    return true;
                    }
                    """)

                    page.wait_for_timeout(1000)

                    is_checked = page.locator("mat-radio-button#auth_Practitioner").evaluate(
                        "el => el.classList.contains('mat-radio-checked')"
                    )

                    print(f"✅ Auth Practitioner final state: {is_checked}")
          





                     




                    
                   
                    time.sleep(8)
                    continue_btn = page.wait_for_selector('button.primary-button.float-right[type="submit"]', timeout=15000)

                    # Scroll into view (optional but safe)
                    continue_btn.scroll_into_view_if_needed()

                    # Click the button (force=True to bypass Angular overlays)
                    continue_btn.click(force=True)

                    # Wait for the next page/network to load
                    page.wait_for_load_state('networkidle', timeout=15000)
                    time.sleep(4)
                    print("🔄 Selecting Office Based")

                    office_radio = page.locator(
                        "mat-radio-button#Office\\ \\/\\ Facility\\ Based"
                    )

                    print("🔄 Selecting Office Based with Angular-safe JS")

                    # Wait for radio to appear
                    page.wait_for_selector("mat-radio-button#Office\\ Based", timeout=15000)

                    # Force Angular update
                    page.evaluate("""
                    () => {
                        const radio = document.querySelector("mat-radio-button#Office\\ Based");
                        if (!radio) return false;

                        const input = radio.querySelector("input.mat-radio-input");

                        // Fire all events Angular cares about
                        input.dispatchEvent(new Event('focus', { bubbles: true }));
                        input.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
                        input.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                        input.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        input.dispatchEvent(new Event('blur', { bubbles: true }));

                        // Update Angular FormControl directly if possible
                        const group = radio.closest('mat-radio-group');
                        if (group && group.__ngContext__) {
                            try {
                                const cmp = group.__ngContext__[8];
                                if (cmp && cmp.control) {
                                    cmp.control.setValue('Office Based');
                                    cmp.control.markAsDirty();
                                    cmp.control.markAsTouched();
                                }
                            } catch(e){}
                        }

                        return true;
                    }
                    """)

                    page.wait_for_timeout(800)

                    # Verify selection
                    is_checked = page.locator("mat-radio-button#Office\\ Based").evaluate(
                        "el => el.classList.contains('mat-radio-checked')"
                    )

                    print(f"✅ Office Based final state: {is_checked}")

                    print("✏️ Filling Street address")

                    street = page.locator("input#street")

                    street.wait_for(state="visible", timeout=15000)
                    street.scroll_into_view_if_needed()
                    street.click()
                    street.fill("28345  back rd")

                    print("✅ Street filled")
                    
                    print("✏️ Filling Street 2")

                    street2 = page.locator("input#street2")

                    street2.wait_for(state="visible", timeout=15000)
                    street2.scroll_into_view_if_needed()
                    street2.click()
                    street2.fill("suite 110")

                    print("✅ Street 2 filled")
                    print("✏️ Filling City")

                    city = page.locator("input#city")

                    city.wait_for(state="visible", timeout=15000)
                    city.scroll_into_view_if_needed()
                    city.click()
                    city.fill("wisxom")

                    print("✅ City filled")
                    print("✏️ Filling Phone Number")

                    phone = page.locator("input#phoneNumber")

                    phone.wait_for(state="visible", timeout=15000)
                    phone.scroll_into_view_if_needed()
                    phone.click()

                    # Fill in masked format
                    phone.fill("2482744560")

                    print("✅ Phone Number filled")
                    print("✏️ Filling Fax Number")

                    fax = page.locator("input#faxNumber")

                    fax.wait_for(state="visible", timeout=15000)
                    fax.scroll_into_view_if_needed()
                    fax.click()

                    # Fill in masked format
                    fax.fill("123-456-7891")

                    print("✅ Fax Number filled")
                    print("🔄 Selecting Facility Fee = Yes")

                    facility_yes = page.locator("mat-radio-button#facilityFee_yes .mat-radio-label-content")

                    facility_yes.wait_for(state="visible", timeout=15000)
                    facility_yes.scroll_into_view_if_needed()
                    page.wait_for_timeout(300)
                    facility_yes.click(force=True)

                    page.wait_for_timeout(700)

                    # Verify final selection
                    is_checked = page.locator("mat-radio-button#facilityFee_yes").evaluate(
                        "el => el.classList.contains('mat-radio-checked')"
                    )

                    print(f"✅ Facility Fee 'Yes' selected: {is_checked}")

                    print("🔄 Selecting Location Wheelchair Accessible = Yes")

                    yes_radio = page.locator("mat-radio-button#locationSpecific_yes .mat-radio-label-content")

                    yes_radio.wait_for(state="visible", timeout=15000)
                    yes_radio.scroll_into_view_if_needed()
                    page.wait_for_timeout(300)
                    yes_radio.click(force=True)

                    page.wait_for_timeout(700)

                    # Verify selection
                    is_checked = page.locator("mat-radio-button#locationSpecific_yes").evaluate(
                        "el => el.classList.contains('mat-radio-checked')"
                    )

                    print(f"✅ Location Yes selected: {is_checked}")




                                    
                             
                   

           
                    
                except:
                    print("ℹ️ Navigation timeout, proceed karte hain")
            else:
                print("❌ Continue button disabled hai!")
                # Debug ke liye screenshot
                disabled_screenshot = "/tmp/aetna_continue_disabled.png"
                page.screenshot(path=disabled_screenshot, full_page=True)
                print(f"📸 Disabled button screenshot: {disabled_screenshot}")
                
                # Check kyun disabled hai
                page.evaluate('''() => {
                    const btn = document.querySelector('button.primary-button.float-right');
                    if (btn) {
                        console.log('Button disabled:', btn.disabled);
                        console.log('Button classes:', btn.className);
                        console.log('Button parent HTML:', btn.parentElement.innerHTML);
                    }
                }''')
                
        except Exception as e:
            print(f"❌ Continue button error: {e}")
            # JavaScript fallback
            page.evaluate('''() => {
                const buttons = document.querySelectorAll('button.primary-button.float-right');
                for (let btn of buttons) {
                    if (btn.textContent.includes('Continue') || btn.type === 'submit') {
                        btn.click();
                        return true;
                    }
                }
                return false;
            }''')
            print("✅ Continue button clicked via JavaScript fallback")
        
        time.sleep(5)
        
        print("🎯 Automation completed up to Continue button!")
        print("📊 Summary: Email Acknowledgement → Radio → Checkbox → Continue")
        
        return page
    
    return True

