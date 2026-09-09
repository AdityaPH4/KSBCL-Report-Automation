import os
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from seleniumbase import sb_cdp

load_dotenv()

KSBCL_URL = "https://ksbclonline.karnataka.gov.in/KSBCL/"
OUT = Path("inspection_output")
OUT.mkdir(exist_ok=True)

LOG = OUT / "inspectPage.log"
HTML = OUT / "page.html"
SCREENSHOT = OUT / "login_page.png"


def main():
    with open(LOG, "w", encoding="utf-8") as log:

        def L(text=""):
            print(text)
            log.write(text + "\n")
            log.flush()

        L("=" * 70)
        L("KSBCL LOGIN PAGE INSPECTION")
        L("=" * 70)

        L("Starting Chrome using SeleniumBase...")
        sb = sb_cdp.Chrome(locale="en")
        endpoint = sb.get_endpoint_url()

        try:
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(endpoint)
                context = browser.contexts[0]

                page = context.pages[0] if context.pages else context.new_page()

                L("Opening KSBCL...")
                page.goto(
                    KSBCL_URL,
                    wait_until="commit",
                    timeout=60000,
                )

                sb.sleep(5)

                L(f"URL: {page.url}")
                L(f"TITLE: {page.title()}")

                # INPUTS
                L("\n" + "=" * 70)
                L("INPUT ELEMENTS")
                L("=" * 70)

                inputs = page.locator("input")
                L(f"Found {inputs.count()} input(s)")

                for i in range(inputs.count()):
                    e = inputs.nth(i)
                    L(f"\nINPUT #{i}")
                    for attr in ["type", "id", "name", "placeholder", "class", "value"]:
                        L(f"  {attr}: {e.get_attribute(attr)}")
                    L(f"  disabled: {e.is_disabled()}")
                    L(f"  visible: {e.is_visible()}")

                # BUTTONS
                L("\n" + "=" * 70)
                L("BUTTON ELEMENTS")
                L("=" * 70)

                buttons = page.locator("button")
                L(f"Found {buttons.count()} button(s)")

                for i in range(buttons.count()):
                    e = buttons.nth(i)
                    try:
                        text = e.inner_text().strip()
                    except Exception:
                        text = ""
                    L(f"\nBUTTON #{i}")
                    L(f"  text: {text}")
                    for attr in ["id", "name", "type", "class"]:
                        L(f"  {attr}: {e.get_attribute(attr)}")
                    L(f"  disabled: {e.is_disabled()}")
                    L(f"  visible: {e.is_visible()}")
                    L(f"  HTML: {e.evaluate('(e) => e.outerHTML')[:3000]}")

                # SUBMIT INPUTS
                L("\n" + "=" * 70)
                L("SUBMIT / BUTTON INPUTS")
                L("=" * 70)

                submits = page.locator(
                    'input[type="submit"], input[type="button"], input[type="image"]'
                )
                L(f"Found {submits.count()}")

                for i in range(submits.count()):
                    e = submits.nth(i)
                    L(f"\nSUBMIT INPUT #{i}")
                    for attr in ["type", "id", "name", "value", "class"]:
                        L(f"  {attr}: {e.get_attribute(attr)}")
                    L(f"  disabled: {e.is_disabled()}")
                    L(f"  visible: {e.is_visible()}")
                    L(f"  HTML: {e.evaluate('(e) => e.outerHTML')[:3000]}")

                # LABELS
                L("\n" + "=" * 70)
                L("LABELS")
                L("=" * 70)

                labels = page.locator("label")
                for i in range(labels.count()):
                    e = labels.nth(i)
                    try:
                        text = e.inner_text().strip()
                    except Exception:
                        text = ""
                    L(f"LABEL #{i}: text={text!r}, for={e.get_attribute('for')}, id={e.get_attribute('id')}, class={e.get_attribute('class')}")

                # CAPTCHA-RELATED ELEMENTS
                L("\n" + "=" * 70)
                L("POSSIBLE CAPTCHA ELEMENTS")
                L("=" * 70)

                selectors = [
                    '[id*="captcha" i]',
                    '[name*="captcha" i]',
                    '[class*="captcha" i]',
                    '[alt*="captcha" i]',
                    '[src*="captcha" i]',
                    '[id*="code" i]',
                    '[name*="code" i]',
                    '[class*="code" i]',
                ]

                seen = set()

                for selector in selectors:
                    elements = page.locator(selector)
                    for i in range(elements.count()):
                        e = elements.nth(i)
                        html = e.evaluate("(e) => e.outerHTML")
                        if html in seen:
                            continue
                        seen.add(html)

                        L(f"\nMATCH: {selector}")
                        L(f"  visible: {e.is_visible()}")
                        L(f"  HTML: {html[:5000]}")

                # FORMS
                L("\n" + "=" * 70)
                L("FORMS")
                L("=" * 70)

                forms = page.locator("form")
                L(f"Found {forms.count()} form(s)")

                for i in range(forms.count()):
                    e = forms.nth(i)
                    L(f"\nFORM #{i}")
                    for attr in ["id", "name", "action", "method", "class"]:
                        L(f"  {attr}: {e.get_attribute(attr)}")

                # LOGIN / CAPTCHA RELATED LINKS
                L("\n" + "=" * 70)
                L("LOGIN / CAPTCHA RELATED LINKS")
                L("=" * 70)

                links = page.locator("a")
                for i in range(links.count()):
                    e = links.nth(i)
                    try:
                        text = e.inner_text().strip()
                    except Exception:
                        text = ""

                    combined = (
                        text + " "
                        + (e.get_attribute("id") or "") + " "
                        + (e.get_attribute("class") or "") + " "
                        + (e.get_attribute("href") or "")
                    ).lower()

                    if any(x in combined for x in ["login", "captcha", "sign in"]):
                        L(f"\nLINK #{i}")
                        L(f"  text: {text}")
                        L(f"  id: {e.get_attribute('id')}")
                        L(f"  class: {e.get_attribute('class')}")
                        L(f"  href: {e.get_attribute('href')}")

                # PAGE TEXT
                L("\n" + "=" * 70)
                L("VISIBLE PAGE TEXT")
                L("=" * 70)
                try:
                    L(page.locator("body").inner_text()[:20000])
                except Exception as e:
                    L(f"Could not read body text: {e}")

                # RAW HTML + SCREENSHOT
                HTML.write_text(page.content(), encoding="utf-8")
                page.screenshot(path=str(SCREENSHOT), full_page=True)

                L("\n" + "=" * 70)
                L("INSPECTION COMPLETE")
                L("=" * 70)
                L(f"Log: {LOG}")
                L(f"HTML: {HTML}")
                L(f"Screenshot: {SCREENSHOT}")
                L("\nBrowser remains open. Press ENTER to close.")
                input()

                browser.close()

        finally:
            sb.quit()


if __name__ == "__main__":
    main()
