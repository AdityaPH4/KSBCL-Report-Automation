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

USERNAME = os.getenv("KSBCL_CIDER_USERNAME")
PASSWORD = os.getenv("KSBCL_CIDER_PASSWORD")

# D94 uses ONE date field: "As On Date"
DATE_INPUT = 'input[placeholder="As On Date"]'

SEARCH_MENU = "#searchMenu"

REPORT_ENDPOINT = "searchDepotCommanReportData"

D94_NAME = "Depot Wise Closing Stock"


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

        # -----------------------------------------------------
        # CAPTCHA
        # -----------------------------------------------------

        print(
            "Reading CAPTCHA..."
        )

        captcha = (
            page.locator(
                "#captcha-text"
            )
            .inner_text()
            .strip()
        )

        print(
            f"CAPTCHA detected: {captcha}"
        )

        page.locator(
            "#varification-code"
        ).fill(
            captcha
        )

        print(
            "CAPTCHA filled."
        )

        # -----------------------------------------------------
        # LOGIN
        # -----------------------------------------------------

        print(
            "Clicking Login..."
        )

        page.locator(
            "#loginBtnId"
        ).click()

        print(
            "Login button clicked."
        )

        print(
            "=============================================="
        )

        # =====================================================
        # WAIT FOR LOGIN
        # =====================================================

        print()

        print(
            "Waiting for login..."
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
        # AUTOMATIC D94 NAVIGATION
        # =====================================================

        print(
            "\nOpening D94 automatically..."
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
        # Look for D94 directly.
        # -----------------------------------------------------

        d94 = page.get_by_text(
            D94_NAME,
            exact=False
        )

        print(
            "D94 text matches:",
            d94.count()
        )

        if d94.count() > 0:

            try:

                print(
                    "Opening D94 from menu..."
                )

                d94.first.click()

            except Exception as e:

                print(
                    "Direct D94 click failed:",
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

                    # D94 report name
                    search_menu.fill(
                        D94_NAME
                    )

                    page.wait_for_timeout(
                        2000
                    )

                    d94_result = page.get_by_text(
                        D94_NAME,
                        exact=False
                    )

                    print(
                        "D94 search results:",
                        d94_result.count()
                    )

                    if d94_result.count() > 0:

                        d94_result.first.click()

                    else:

                        print(
                            "\nERROR: Could not find D94 "
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
                "D94 is not directly visible."
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

                # D94 report name
                search_menu.fill(
                    D94_NAME
                )

                page.wait_for_timeout(
                    2000
                )

                d94_result = page.get_by_text(
                    D94_NAME,
                    exact=False
                )

                print(
                    "D94 search results:",
                    d94_result.count()
                )

                if d94_result.count() > 0:

                    d94_result.first.click()

                else:

                    print(
                        "\nERROR: Could not find D94 "
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
        # WAIT FOR D94 PAGE
        # =====================================================

        print(
            "\nWaiting for D94 report page..."
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
                "\nERROR: D94 did not open."
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
            "D94 opened successfully."
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

        print(
            "\nReport date:",
            report_date_str
        )

        # =====================================================
        # SET D94 AS-ON DATE
        # =====================================================

        print(
            "\nSetting D94 As On Date..."
        )

        date_input = page.locator(
            DATE_INPUT
        )

        # Click the date field to open the datepicker
        date_input.click()

        page.wait_for_timeout(500)

        # Calculate yesterday
        report_date_str = report_date.strftime("%d/%m/%Y")

        print(
            "Selecting date:",
            report_date_str
        )

        # -----------------------------------------------------
        # Select the day from the visible datepicker
        # -----------------------------------------------------

        day_number = str(report_date.day)

        # Find the visible datepicker
        datepicker = page.locator(
            ".datepicker:visible"
        )

        if datepicker.count() == 0:

            # Fallback: search visible calendar containers
            datepicker = page.locator(
                "div:visible"
            ).filter(
                has_text="September 2026"
            )

        # Click the exact day
        day_button = datepicker.get_by_text(
            day_number,
            exact=True
        )

        print(
            "Matching day buttons:",
            day_button.count()
        )

        if day_button.count() == 0:

            print(
                "\nERROR: Could not find the required date in the datepicker."
            )

            input(
                "\nPress ENTER to close..."
            )

            browser.close()

            raise SystemExit(1)

        # Click the last matching visible day.
        # This avoids accidentally selecting a duplicate
        # day from another calendar element.
        for i in range(day_button.count() - 1, -1, -1):

            candidate = day_button.nth(i)

            try:

                if candidate.is_visible():

                    candidate.click()

                    break

            except Exception:

                pass

        page.wait_for_timeout(500)

        print(
            "Date selected:",
            report_date_str
        )

        # Verify the actual input value
        try:

            selected_value = date_input.input_value()

            print(
                "Date field now contains:",
                selected_value
            )

        except Exception as e:

            print(
                "Could not read date field:",
                e
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
                "\nERROR: Visible D94 Search button "
                "was not found."
            )

            input(
                "\nPress ENTER to close..."
            )

            browser.close()

            raise SystemExit(1)

        print(
            "D94 Search button found."
        )

        # =====================================================
        # RUN REPORT
        # =====================================================

        print(
            "\nRunning D94 report..."
        )

        # -----------------------------------------------------
        # Click Search and capture ONLY the response caused
        # by this Search click.
        # -----------------------------------------------------

        try:

            with page.expect_response(
                lambda response: REPORT_ENDPOINT in response.url,
                timeout=30000
            ) as response_info:

                visible_search.click()

            report_response = response_info.value

            print(
                "\nReport API response detected."
            )

            print(
                "URL:",
                report_response.url
            )

            print(
                "HTTP status:",
                report_response.status
            )

        except Exception as e:

            print(
                "\nERROR: Report API response "
                "was not detected after clicking Search."
            )

            print(
                "Error:",
                e
            )

            browser.close()

            raise SystemExit(1)

        # =====================================================
        # CHECK RESPONSE
        # =====================================================

        if report_response.status != 200:

            print(
                "\nERROR: Report API returned HTTP",
                report_response.status
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

            print(
                e
            )

            browser.close()

            raise SystemExit(1)

        # =====================================================
        # CHECK PAYLOAD
        # =====================================================

        if "payload" not in result:

            print(
                "\nERROR: API response has no payload."
            )

            print(
                "Response keys:",
                list(result.keys())
            )

            browser.close()

            raise SystemExit(1)

        payload = result["payload"]

        # =====================================================
        # PARSE PAYLOAD
        # =====================================================

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

            print(
                e
            )

            browser.close()

            raise SystemExit(1)

        # =====================================================
        # VALIDATE ROWS
        # =====================================================

        if not isinstance(
            rows,
            list
        ):

            print(
                "\nERROR: Report payload is not a list."
            )

            browser.close()

            raise SystemExit(1)

        # =====================================================
        # ZERO DATA CHECK
        # =====================================================

        # Case 1:
        # API returns an empty list.

        if len(rows) == 0:

            print()

            print(
                f"Zero data for {report_date_str}."
            )

            print(
                "No report file will be created."
            )

            browser.close()

            return

        # Case 2:
        # KSBCL returns a dummy row when there is no data.

        if len(rows) == 1:

            first_row = rows[0]

            if isinstance(
                first_row,
                dict
            ):

                values = [
                    str(value).strip().lower()
                    for value in first_row.values()
                ]

                if "dummy" in values:

                    print()

                    print(
                        f"Zero data for {report_date_str}."
                    )

                    print(
                        "No report file will be created."
                    )

                    browser.close()

                    return

        # =====================================================
        # REAL DATA FOUND
        # =====================================================

        df = pd.DataFrame(
            rows
        )

        print(
            "\nReal D94 data found."
        )

        print(
            "Rows received:",
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
            f"D94_Cider_Report_"
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
            "D94 REPORT SAVED SUCCESSFULLY"
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