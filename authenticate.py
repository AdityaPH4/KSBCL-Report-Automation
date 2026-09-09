# import os
# from dotenv import load_dotenv
# from playwright.sync_api import sync_playwright
# from seleniumbase import sb_cdp

# # =========================================================
# # CONFIGURATION
# # =========================================================

# load_dotenv()

# KSBCL_URL = "https://ksbclonline.karnataka.gov.in/KSBCL/"

# USERNAME = os.getenv("KSBCL_USERNAME")
# PASSWORD = os.getenv("KSBCL_PASSWORD")

# # sb = sb_cdp.Chrome(locale="en")

# # endpoint_url=sb.get_endpoint_url()


# # =========================================================
# # MAIN
# # =========================================================

# def main():

#     sb = sb_cdp.Chrome(locale="en")

#     endpoint_url=sb.get_endpoint_url()

#     if not USERNAME:
#         raise RuntimeError(
#             "KSBCL_USERNAME is missing from .env"
#         )

#     if not PASSWORD:
#         raise RuntimeError(
#             "KSBCL_PASSWORD is missing from .env"
#         )

#     with sync_playwright() as p:

#         # browser = p.chromium.launch(
#         #     headless=False #to show the UI of the automation-> used for debugging
#         # )
#         browser = p.chromium.connect_over_cdp(
#             endpoint_url
#         ) 
#         context=browser.contexts[0]


#         # context = browser.new_context()
#         # page = context.new_page()

#         page=context.pages[0]
#         # page.goto(KSBCL_URL, wait_until="domcontentloaded")  
        



#         # =====================================================
#         # OPEN KSBCL
#         # =====================================================

#         print("Opening KSBCL...")

#         page.goto(
#             KSBCL_URL,
#             wait_until="domcontentloaded"
#         )

#         # =====================================================
#         # FILL CREDENTIALS
#         # =====================================================

#         print("Filling username...")

#         page.fill(
#             "#login_name",
#             USERNAME
#         )

#         print("Filling password...")

#         page.fill(
#             "#password",
#             PASSWORD
#         )

#         # =====================================================
#         # CAPTCHA
#         # =====================================================

#         print("catcha bypass start")

#         print()
#         print("==============================================")
#         print("CAPTCHA REQUIRED")
#         sb.sleep(2)
#         sb.solve_captcha()
#         sb.wait_for_element_absent("input[disabled]")
#         print("==============================================")
        
        

#         print("captcha bypass finishhh")

#         # =====================================================
#         # WAIT FOR LOGIN
#         # =====================================================

#         print("Waiting for successful login...")

#         try:

#             page.wait_for_url(
#                 lambda url: url != KSBCL_URL,
#                 timeout=120000
#             )

#         except Exception:

#             print()
#             print("ERROR: Login was not detected.")

#             print(
#                 "Current URL:",
#                 page.url
#             )

#             input(
#                 "\nPress ENTER to close..."
#             )

#             browser.close()

#             raise SystemExit(1)

#         # =====================================================
#         # SUCCESS
#         # =====================================================

#         print()
#         print("==============================================")
#         print("LOGIN SUCCESSFUL")
#         print("==============================================")

#         print(
#             "Current URL:",
#             page.url
#         )

#         input(
#             "\nPress ENTER to close the browser..."
#         )

#         browser.close()


# # =========================================================
# # ENTRY POINT
# # =========================================================

# if __name__ == "__main__":
#     main()












import os

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from seleniumbase import sb_cdp


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

KSBCL_URL = "https://ksbclonline.karnataka.gov.in/KSBCL/"

USERNAME = os.getenv("KSBCL_USERNAME")
PASSWORD = os.getenv("KSBCL_PASSWORD")


# =========================================================
# MAIN
# =========================================================

def main():

    # ---------------------------------------------------------
    # Check credentials
    # ---------------------------------------------------------

    if not USERNAME:
        raise RuntimeError(
            "KSBCL_USERNAME is missing from .env"
        )

    if not PASSWORD:
        raise RuntimeError(
            "KSBCL_PASSWORD is missing from .env"
        )

    # ---------------------------------------------------------
    # Start Chrome using SeleniumBase
    # ---------------------------------------------------------

    print("Starting Chrome...")

    sb = sb_cdp.Chrome(
        locale="en"
    )

    endpoint_url = sb.get_endpoint_url()

    print("Chrome started.")
    print("CDP endpoint obtained.")

    # ---------------------------------------------------------
    # Connect Playwright to SeleniumBase Chrome
    # ---------------------------------------------------------

    with sync_playwright() as p:

        print("Connecting Playwright to Chrome...")

        browser = p.chromium.connect_over_cdp(
            endpoint_url
        )

        context = browser.contexts[0]

        # Get existing tab or create one
        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()

        print("Playwright connected successfully.")

        # -----------------------------------------------------
        # OPEN KSBCL
        # -----------------------------------------------------

        print("Opening KSBCL...")

        try:

            page.goto(
                KSBCL_URL,
                wait_until="commit",
                timeout=60000
            )

        except Exception as e:

            print()
            print("KSBCL navigation produced an error:")
            print(type(e).__name__)
            print(e)
            print()
            print("Current URL:")
            print(page.url)

            input(
                "\nPress ENTER to close..."
            )

            browser.close()
            sb.quit()

            return

        print("KSBCL navigation started.")

        # Give the page a little time to render.
        sb.sleep(5)

        print(
            "Current URL:",
            page.url
        )

        # -----------------------------------------------------
        # CHECK LOGIN FIELDS
        # -----------------------------------------------------

        print("\nChecking login fields...")

        try:

            page.locator(
                "#login_name"
            ).wait_for(
                state="visible",
                timeout=30000
            )

            print(
                "Username field found."
            )

        except Exception:

            print(
                "Username field was not found."
            )

            print(
                "Current URL:",
                page.url
            )

            input(
                "\nPress ENTER to close..."
            )

            browser.close()
            sb.quit()

            return

        # -----------------------------------------------------
        # FILL USERNAME
        # -----------------------------------------------------

        print(
            "Filling username..."
        )

        page.locator(
            "#login_name"
        ).fill(
            USERNAME
        )

        # -----------------------------------------------------
        # FILL PASSWORD
        # -----------------------------------------------------

        print(
            "Filling password..."
        )

        page.locator(
            "#password"
        ).fill(
            PASSWORD
        )

        # -----------------------------------------------------
        # # CAPTCHA
        # sb.sleep(2)
        # sb.solve_captcha()
        # sb.wait_for_element_absent("input[disabled]")
        # sb.sleep(2)
        # -----------------------------------------------------

        
        # -----------------------------------------------------
# CAPTCHA
# -----------------------------------------------------

       # -----------------------------------------------------
# CAPTCHA
# -----------------------------------------------------

        print("Reading CAPTCHA...")

        captcha = page.locator("#captcha-text").inner_text().strip()

        print(f"CAPTCHA detected: {captcha}")

        page.locator("#varification-code").fill(captcha)

        print("CAPTCHA filled.")

        # -----------------------------------------------------
        # LOGIN 
        # -----------------------------------------------------

        print("Clicking Login...")

        page.locator("#loginBtnId").click()

        print("Login button clicked.")
        
        print(
            "=============================================="
        )

        # -----------------------------------------------------
        # WAIT FOR LOGIN
        # -----------------------------------------------------

        print()
        print(
            "Waiting for login..."
        )

        try:

            page.wait_for_url(
                lambda url: url != KSBCL_URL,
                timeout=120000
            )

            print()
            print(
                "LOGIN SUCCESSFUL"
            )

            print(
                "Current URL:",
                page.url
            )

        except Exception:

            print()
            print(
                "Login was not detected within 120 seconds."
            )

            print(
                "Current URL:",
                page.url
            )

        # -----------------------------------------------------
        # KEEP BROWSER OPEN
        # -----------------------------------------------------

        input(
            "\nPress ENTER to close..."
        )

        browser.close()
        sb.quit()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()