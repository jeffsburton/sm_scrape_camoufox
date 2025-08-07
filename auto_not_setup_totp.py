import asyncio
import os
import pyotp

from util import print_filtered_traceback, wait, human_type
from vpn import disconnect_vpn
# Ensure these imports are available in your environment
from web import get_accounts, AccountStatus, json_web_call
from camoufox_browser_manager import CamoufoxBrowser
from playwright.sync_api import Page
from camoufox.sync_api import BrowserContext # Import BrowserContext


# Example Playwright activity function
# Modified to accept the BrowserContext object
def my_playwright_activity(browser_instance: CamoufoxBrowser, ctx: BrowserContext, page: Page):


    page.goto("https://www.instagram.com", wait_until="domcontentloaded")
    wait (6, 8)
    page.wait_for_selector("input[name='username']")

    #page.click("input[type='username']")
    human_type(page, "input[name='username']", browser_instance.profile.profile)
    wait (1, 2)
    page.wait_for_selector("input[name='password']")
    page.click("input[type='password']")
    human_type(page, "input[name='password']", browser_instance.profile.password)
    wait (1, 2)
    page.wait_for_selector("button[type='submit']")
    page.click("button[type='submit']")

    page.wait_for_selector("input[name='verificationCode']")
    totp = pyotp.TOTP(browser_instance.profile.authenticator)
    totp_code = totp.now()
    human_type(page, "input[name='verificationCode']", totp_code)
    page.click("button")

    ctx.wait_for_event("close", timeout=0)

    json_web_call(
        "change_account_status.php", # Keep "accounts.php" as discussed previously
        {
            "profile": browser_instance.profile.profile,
            "status": AccountStatus.FRAGILE.value
        },
    )


def main():
    try:
        accounts = get_accounts(status=AccountStatus.NOT_SETUP)

        if not accounts:
            print("No accounts found with status 'ready'.")
            return

        print(f"Found {len(accounts)} accounts:")
        print("=" * 40)

        for i, profile_obj in enumerate(accounts):
            print(f"--- Iteration {i + 1} of {len(accounts)} ---")
            print(f"  Profile: {profile_obj.profile}")
            print(f"  Password: {profile_obj.password}")

            browser_manager = CamoufoxBrowser(profile_obj)
            browser_manager.launch(my_playwright_activity)
            print("-" * 30)

        asyncio.run(disconnect_vpn())

    except Exception as e:
        print(f"An error occurred: {e}")
        print_filtered_traceback()

if __name__ == "__main__":
    if 'COMPUTERNAME' not in os.environ:
        os.environ['COMPUTERNAME'] = 'MY_DEV_MACHINE'
        print("Set dummy COMPUTERNAME environment variable for testing.")

    main()