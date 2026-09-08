from playwright.sync_api import sync_playwright

KSBCL_URL = "https://ksbclonline.karnataka.gov.in/KSBCL/"
REPORT_ENDPOINT = "searchDepotCommanReportData"


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    report_response = None

    def handle_response(response):
        nonlocal_report = None

        if REPORT_ENDPOINT in response.url:
            print("\n========== REPORT RESPONSE ==========")
            print("Status:", response.status)
            print("URL:", response.url)

            try:
                body = response.text()

                print("\nResponse:")
                print(body[:5000])

            except Exception as e:
                print("Could not read response:", e)

            print("====================================\n")

    page.on("response", handle_response)

    print("Opening KSBCL...")
    page.goto(KSBCL_URL)

    input(
        "\nLog in manually, complete CAPTCHA, and reach the KSBCL dashboard.\n"
        "Then press ENTER here..."
    )

    print("\nNavigate to the D88 report.")
    print("Set your filters and click SEARCH.")
    print("Waiting for the report response...\n")

    input("Press ENTER after the report has loaded...")

    # Give Playwright a moment to finish processing network events
    page.wait_for_timeout(1000)

    print("\nReport request processing complete.")

    input("\nPress ENTER to close the browser...")

    browser.close()