import time
import random
from typing import List

from playwright.sync_api import Page, Locator
import browse
from util import wait, human_type
from web import get_random_profile


def go_home(page: Page):
    locator: Locator = page.locator('svg[aria-label="Home"]')
    locator.first.click()
    wait(1, 2)

def scroll_for_a_while(page: Page, seconds: int = 59):
    start = time.time()
    while time.time() - start < seconds:
        # Scroll down for a bit
        browse.scroll_down(page, min_turns=3, max_turns=6)
        wait(1, 2)
        # Occasionally scroll up a little
        if random.random() < 0.1:
            browse.scroll_up(page, min_turns=1, max_turns=2)
        wait(2, 5)

def explore(page: Page, seconds: int = 59):
    locator: Locator = page.locator('a[href="/explore/"]')
    locator.first.click()
    wait(5, 7)
    scroll_for_a_while(page, seconds)
    go_home(page)

def notifications(page: Page):
    locator: Locator = page.locator('svg[aria-label="Notifications"]')
    locator.first.click()
    wait(5, 7)
    locator.first.click()

def profile (page: Page, profile_name: str):
    selector:str = 'a[href="/' + profile_name + '/"][tabindex="0"]'
    locator: Locator = page.locator(selector)
    locator.first.click(force=True)
    wait(5, 7)
    go_home(page)

def search(page: Page, go_home_after = True, profile_name = None):
    locator: Locator = page.locator('svg[aria-label="Search"]')
    locator.first.click()
    wait(2, 4)
    if profile_name is None:
        profile_name = get_random_profile()
    human_type(page, 'input[aria-label="Search input"]', profile_name)
    page.wait_for_selector('a[href="/' + profile_name + '/"]')
    locator = page.locator('a[href="/' + profile_name + '/"]')
    locator.first.click(force=True)
    wait(5, 7)
    if go_home_after:
        go_home(page)

def follow(page: Page):
    locators: List[Locator] = browse.get_visible_locators(page, 'xpath=//button[.//div[text()="Follow"]]')
    if locators:
        random.choice(locators).click()
        wait(3, 5)
    go_home(page)

