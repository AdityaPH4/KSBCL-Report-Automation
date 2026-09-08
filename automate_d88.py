import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json

import pandas as pd
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

KSBCL_URL = "https://ksbclonline.karnataka.gov.in/KSBCL/"

USERNAME = os.getenv("KSBCL_USERNAME")
PASSWORD = os.getenv("KSBCL_PASSWORD")

DATE_INPUT = "#dateInpId"
FROM_DATE_INPUT = "#fromdateInpId"
TO_DATE_INPUT = "#todateInpId"

SEARCH_MENU = "#searchMenu"

REPORT_ENDPOINT = "searchDepotCommanReportData"

D88_NAME = "Retailer Purchase Summary"


# =========================================================
# VALIDATE CREDENTIALS
# =========================================================

if not USERNAME:
    raise RuntimeError(
        "KSBCL_USERNAME is missing from .env"
    )

if not PASSWORD:
    raise RuntimeError(
        "KSBCL_PASSWORD is missing from .env"
    )


# =========================================================
# MAIN
# =========================================================

def main():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context()

        page = context.new_page()

        report_response = None

        # =====================================================
        # REPORT API RESPONSE
        # =====================================================

        def handle_response(response):

            nonlocal report_response

            if REPORT_ENDPOINT in response.url:

                report_response = response

                print(
                    "\nReport API response detected."
                )

                print(
                    "HTTP status:",
                    response.status
                )

        page.on(
            "response",
            handle_response
        )

        # =====================================================
        # OPEN KSBCL
        # =====================================================

        print(
            "Opening KSBCL..."
        )

        page.goto(
            KSBCL_URL,
            wait_until="domcontentloaded"
        )

        # =====================================================
        # AUTOMATIC LOGIN
        # =====================================================

        print(
            "\nFilling username..."
        )

        page.fill(
            "#login_name",
            USERNAME
        )

        print(
            "Filling password..."
        )

        page.fill(
            "#password",
            PASSWORD
        )

        # =====================================================
        # CAPTCHA
        # =====================================================

        print()
        print(
            "=============================================="
        )
        print(
            "CAPTCHA REQUIRED"
        )
        print(
            "=============================================="
        )
        print(
            "Username and password have been filled."
        )
        print(
            "Solve the CAPTCHA manually."
        )
        print(
            "Then click Login."
        )
        print(
            "=============================================="
        )
        print()

        # =====================================================
        # WAIT FOR LOGIN TO COMPLETE
        # =====================================================

        print(
            "Waiting for successful login..."
        )

        try:

            page.wait_for_url(
                lambda url: url != KSBCL_URL,
                timeout=120000
            )

        except Exception:

            print()
            print(
                "ERROR: Login was not detected."
            )

            print(
                "Current URL:",
                page.url
            )

            input(
                "\nPress ENTER to close..."
            )

            browser.close()

            raise SystemExit(1)

        print()
        print(
            "Login successful."
        )

        print(
            "Current URL:",
            page.url
        )

        # =====================================================
        # AUTOMATIC D88 NAVIGATION
        # =====================================================

        print(
            "\nOpening D88 automatically..."
        )

        # -----------------------------------------------------
        # Make sure we are on the common reports page.
        # -----------------------------------------------------

        if "DepotCommonReports" not in page.url:

            try:

                page.goto(
                    KSBCL_URL
                    + "depotView/DepotCommonReports",
                    wait_until="domcontentloaded"
                )

            except Exception as e:

                print(
                    "Could not open reports page:",
                    e
                )

                input(
                    "\nPress ENTER to close..."
                )

                browser.close()

                raise SystemExit(1)

        # Give page JavaScript time to build the menu.

        page.wait_for_timeout(
            2000
        )

        # -----------------------------------------------------
        # METHOD 1:
        # Look for D88 directly.
        # -----------------------------------------------------

        d88 = page.get_by_text(
            D88_NAME,
            exact=False
        )

        print(
            "D88 text matches:",
            d88.count()
        )

        if d88.count() > 0:

            try:

                print(
                    "Opening D88 from menu..."
                )

                d88.first.click()

            except Exception as e:

                print(
                    "Direct D88 click failed:",
                    e
                )

                # Try report search instead.

                if page.locator(
                    SEARCH_MENU
                ).count() > 0:

                    print(
                        "Trying KSBCL report search..."
                    )

                    search_menu = page.locator(
                        SEARCH_MENU
                    )

                    search_menu.fill(
                        "Retailer Purchase Summary"
                    )

                    page.wait_for_timeout(
                        2000
                    )

                    d88_result = page.get_by_text(
                        D88_NAME,
                        exact=False
                    )

                    print(
                        "D88 search results:",
                        d88_result.count()
                    )

                    if d88_result.count() > 0:

                        d88_result.first.click()

                    else:

                        print(
                            "\nERROR: Could not find D88 "
                            "in the report menu."
                        )

                        input(
                            "\nPress ENTER to close..."
                        )

                        browser.close()

                        raise SystemExit(1)

                else:

                    print(
                        "\nERROR: KSBCL report search menu "
                        "was not found."
                    )

                    input(
                        "\nPress ENTER to close..."
                    )

                    browser.close()

                    raise SystemExit(1)

        # -----------------------------------------------------
        # METHOD 2:
        # Use report search.
        # -----------------------------------------------------

        else:

            print(
                "D88 is not directly visible."
            )

            if page.locator(
                SEARCH_MENU
            ).count() > 0:

                print(
                    "Using KSBCL report search..."
                )

                search_menu = page.locator(
                    SEARCH_MENU
                )

                search_menu.fill(
                    "Retailer Purchase Summary"
                )

                page.wait_for_timeout(
                    2000
                )

                d88_result = page.get_by_text(
                    D88_NAME,
                    exact=False
                )

                print(
                    "D88 search results:",
                    d88_result.count()
                )

                if d88_result.count() > 0:

                    d88_result.first.click()

                else:

                    print(
                        "\nERROR: Could not find D88 "
                        "in the report menu."
                    )

                    print(
                        "\nVisible text around menu:"
                    )

                    print(
                        page.locator(
                            "body"
                        ).inner_text()[:5000]
                    )

                    input(
                        "\nPress ENTER to close..."
                    )

                    browser.close()

                    raise SystemExit(1)

            else:

                print(
                    "\nERROR: KSBCL report search menu "
                    "was not found."
                )

                input(
                    "\nPress ENTER to close..."
                )

                browser.close()

                raise SystemExit(1)

        # =====================================================
        # WAIT FOR D88 PAGE
        # =====================================================

        print(
            "\nWaiting for D88 report page..."
        )

        try:

            page.locator(
                DATE_INPUT
            ).wait_for(
                state="visible",
                timeout=15000
            )

        except Exception:

            print(
                "\nERROR: D88 did not open."
            )

            print(
                "Current URL:",
                page.url
            )

            input(
                "\nPress ENTER to close..."
            )

            browser.close()

            raise SystemExit(1)

        print(
            "D88 opened successfully."
        )

        # =====================================================
        # CALCULATE YESTERDAY
        # =====================================================

        india = ZoneInfo(
            "Asia/Kolkata"
        )

        report_date = (
            datetime.now(india).date()
            - timedelta(days=1)
        )

        report_date_str = report_date.strftime(
            "%d/%m/%Y"
        )

        date_range = (
            f"{report_date_str} - "
            f"{report_date_str}"
        )

        print(
            "\nReport date:",
            report_date_str
        )

        # =====================================================
        # SET DATE
        # =====================================================

        page.locator(
            DATE_INPUT
        ).fill(
            date_range
        )

        page.locator(
            FROM_DATE_INPUT
        ).evaluate(
            "(el, value) => el.value = value",
            report_date_str
        )

        page.locator(
            TO_DATE_INPUT
        ).evaluate(
            "(el, value) => el.value = value",
            report_date_str
        )

        print(
            "Date configured:",
            date_range
        )

        # =====================================================
        # FIND VISIBLE SEARCH BUTTON
        # =====================================================

        search_buttons = page.locator(
            "button"
        ).filter(
            has_text="Search"
        )

        visible_search = None

        for i in range(
            search_buttons.count()
        ):

            button = search_buttons.nth(i)

            try:

                if button.is_visible():

                    visible_search = button

                    break

            except Exception:

                pass

        if visible_search is None:

            print(
                "\nERROR: Visible D88 Search button "
                "was not found."
            )

            input(
                "\nPress ENTER to close..."
            )

            browser.close()

            raise SystemExit(1)

        print(
            "D88 Search button found."
        )

        # =====================================================
        # RUN REPORT
        # =====================================================

        print(
            "\nRunning D88 report..."
        )

        visible_search.click()

        # =====================================================
        # WAIT FOR REPORT API
        # =====================================================

        print(
            "Waiting for report data..."
        )

        for _ in range(150):

            if report_response is not None:

                break

            page.wait_for_timeout(
                100
            )

        # =====================================================
        # CHECK RESPONSE
        # =====================================================

        if report_response is None:

            print(
                "\nERROR: Report API response "
                "was not detected."
            )

            input(
                "\nPress ENTER to close..."
            )

            browser.close()

            raise SystemExit(1)

        if report_response.status != 200:

            print(
                "\nERROR: Report API returned HTTP",
                report_response.status
            )

            input(
                "\nPress ENTER to close..."
            )

            browser.close()

            raise SystemExit(1)

        print(
            "Report API returned HTTP 200."
        )

        # =====================================================
        # PARSE JSON
        # =====================================================

        try:

            result = report_response.json()

        except Exception as e:

            print(
                "\nERROR: Could not parse API JSON."
            )

            print(e)

            input(
                "\nPress ENTER to close..."
            )

            browser.close()

            raise SystemExit(1)

        if "payload" not in result:

            print(
                "\nERROR: API response has no payload."
            )

            print(
                "Response keys:",
                list(result.keys())
            )

            input(
                "\nPress ENTER to close..."
            )

            browser.close()

            raise SystemExit(1)

        payload = result["payload"]

        try:

            if isinstance(
                payload,
                str
            ):

                rows = json.loads(
                    payload
                )

            else:

                rows = payload

        except Exception as e:

            print(
                "\nERROR: Could not parse report payload."
            )

            print(e)

            input(
                "\nPress ENTER to close..."
            )

            browser.close()

            raise SystemExit(1)

        # =====================================================
        # CREATE DATAFRAME
        # =====================================================

        if not isinstance(
            rows,
            list
        ):

            print(
                "\nERROR: Report payload is not a list."
            )

            input(
                "\nPress ENTER to close..."
            )

            browser.close()

            raise SystemExit(1)

        df = pd.DataFrame(
            rows
        )

        print(
            "\nRows received:",
            len(df)
        )

        print(
            "Columns:",
            len(df.columns)
        )

        # =====================================================
        # SAVE EXCEL
        # =====================================================

        output_filename = (
            f"D88_Report_"
            f"{report_date.isoformat()}.xlsx"
        )

        df.to_excel(
            output_filename,
            index=False
        )

        # =====================================================
        # SUCCESS
        # =====================================================

        print(
            "\n========================================"
        )

        print(
            "D88 REPORT SAVED SUCCESSFULLY"
        )

        print(
            "========================================"
        )

        print(
            "File:",
            output_filename
        )

        print(
            "Rows:",
            len(df)
        )

        print(
            "Report date:",
            report_date_str
        )

        print()

        browser.close()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()