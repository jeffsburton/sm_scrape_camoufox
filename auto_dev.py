from instagram import scroll_for_a_while, explore, notifications, profile, search, follow
from profile import Profile
from util import print_filtered_traceback, wait, human_type
from camoufox_browser_manager import CamoufoxBrowser
from playwright.sync_api import Page
from camoufox.sync_api import BrowserContext # Import BrowserContext


# Example Playwright activity function
# Modified to accept the BrowserContext object
def my_playwright_activity(browser_instance: CamoufoxBrowser, ctx: BrowserContext, page: Page):


    page.goto("https://instagram.com", wait_until="domcontentloaded")
    wait(3, 3)
    follow(page)


    ctx.wait_for_event("close", timeout=0)


def main():
    try:
        profile: Profile = Profile(profile="beast_tmodee", password="6wE2L4*VSZBy", code=None, authenticator=None, recovery=None)

        browser_manager = CamoufoxBrowser(profile)
        browser_manager.launch(my_playwright_activity)


    except Exception as e:
        print(f"An error occurred: {e}")
        print_filtered_traceback()

if __name__ == "__main__":


    main()