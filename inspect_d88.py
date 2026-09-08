from playwright.sync_api import sync_playwright

KSBCL_URL = "https://ksbclonline.karnataka.gov.in/KSBCL/"


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    print("Opening KSBCL...")
    page.goto(KSBCL_URL)

    input(
        "\nLog in manually, complete CAPTCHA, and reach the KSBCL dashboard.\n"
        "Press ENTER here once you're logged in..."
    )

    print("\nAuthenticated. Now navigate to D88 manually.")
    print("Open Retailer Purchase Summary (D88).")
    print("Do NOT click Search yet.\n")

    input("Press ENTER once D88 is visible...")

    print("\n========== INPUT ELEMENTS ==========\n")

    inputs = page.locator("input")

    for i in range(inputs.count()):
        element = inputs.nth(i)

        try:
            print(f"INPUT #{i}")
            print("  type :", element.get_attribute("type"))
            print("  name :", element.get_attribute("name"))
            print("  id   :", element.get_attribute("id"))
            print("  class:", element.get_attribute("class"))
            print("  value:", element.input_value())
            print()
        except Exception as e:
            print(f"Could not inspect input #{i}: {e}")

    print("\n========== SELECT ELEMENTS ==========\n")

    selects = page.locator("select")

    for i in range(selects.count()):
        element = selects.nth(i)

        try:
            print(f"SELECT #{i}")
            print("  name :", element.get_attribute("name"))
            print("  id   :", element.get_attribute("id"))
            print("  class:", element.get_attribute("class"))

            options = element.locator("option")

            print("  options:")

            for j in range(min(options.count(), 20)):
                option = options.nth(j)

                print(
                    f"    {j}: "
                    f"value={option.get_attribute('value')!r}, "
                    f"text={option.inner_text()!r}"
                )

            print()

        except Exception as e:
            print(f"Could not inspect select #{i}: {e}")

    print("\n========== BUTTONS ==========\n")

    buttons = page.locator("button, input[type='button'], input[type='submit']")

    for i in range(buttons.count()):
        element = buttons.nth(i)

        try:
            print(f"BUTTON #{i}")
            print("  tag  :", element.evaluate("(el) => el.tagName"))
            print("  type :", element.get_attribute("type"))
            print("  name :", element.get_attribute("name"))
            print("  id   :", element.get_attribute("id"))
            print("  class:", element.get_attribute("class"))
            print("  text :", element.inner_text() if element.evaluate(
                "(el) => el.tagName !== 'INPUT'"
            ) else element.get_attribute("value"))
            print()

        except Exception as e:
            print(f"Could not inspect button #{i}: {e}")

    print("\n====================================")
    print("Inspection complete.")

    input("\nPress ENTER to close the browser...")

    browser.close()