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


    page.goto("https://instagram.com", wait_until="domcontentloaded")

    ctx.wait_for_event("close", timeout=0)


def main():
    try:
        accounts = get_accounts(status=AccountStatus.FRAGILE)

        if not accounts:
            print("No accounts found with status 'ready'.")
            return

        print(f"Found {len(accounts)} accounts:")
        print("=" * 40)

        for i, profile_obj in enumerate(accounts):
            print(f"--- Iteration {i + 1} of {len(accounts)} ---")
            print(f"  Profile: {profile_obj.profile}")

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