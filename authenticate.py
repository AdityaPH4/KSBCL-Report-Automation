import os

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright


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

    if not USERNAME:
        raise RuntimeError(
            "KSBCL_USERNAME is missing from .env"
        )

    if not PASSWORD:
        raise RuntimeError(
            "KSBCL_PASSWORD is missing from .env"
        )

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context()

        page = context.new_page()

        # =====================================================
        # OPEN KSBCL
        # =====================================================

        print("Opening KSBCL...")

        page.goto(
            KSBCL_URL,
            wait_until="domcontentloaded"
        )

        # =====================================================
        # FILL CREDENTIALS
        # =====================================================

        print("Filling username...")

        page.fill(
            "#login_name",
            USERNAME
        )

        print("Filling password...")

        page.fill(
            "#password",
            PASSWORD
        )

        # =====================================================
        # CAPTCHA
        # =====================================================

        print()
        print("==============================================")
        print("CAPTCHA REQUIRED")
        print("==============================================")
        print("Username and password have been filled.")
        print("Solve the CAPTCHA manually.")
        print("Then click Login.")
        print("==============================================")
        print()

        # =====================================================
        # WAIT FOR LOGIN
        # =====================================================

        print("Waiting for successful login...")

        try:

            page.wait_for_url(
                lambda url: url != KSBCL_URL,
                timeout=120000
            )

        except Exception:

            print()
            print("ERROR: Login was not detected.")

            print(
                "Current URL:",
                page.url
            )

            input(
                "\nPress ENTER to close..."
            )

            browser.close()

            raise SystemExit(1)

        # =====================================================
        # SUCCESS
        # =====================================================

        print()
        print("==============================================")
        print("LOGIN SUCCESSFUL")
        print("==============================================")

        print(
            "Current URL:",
            page.url
        )

        input(
            "\nPress ENTER to close the browser..."
        )

        browser.close()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()