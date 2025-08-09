import random

from playwright.sync_api import Page

from util import wait


def scroll(page: Page, up: bool, min_turns: int, max_turns: int):
    num_turns: int = int(random.uniform(min_turns, max_turns))
    delta_y: float = 100 * (-1 if up else 1);
    for i in range(num_turns):
        page.mouse.wheel(0, delta_y)
        wait(.2, .4)

def scroll_down(page: Page, min_turns: int = 2, max_turns: int = 5):
    scroll(page, up=False, min_turns=min_turns, max_turns=max_turns)

def scroll_up(page: Page, min_turns: int = 2, max_turns: int = 5):
    scroll(page, up=True, min_turns=min_turns, max_turns=max_turns)


from typing import List

from typing import List
from playwright.sync_api import Locator, Page

def get_visible_locators(page: Page, selector: str) -> List[Locator]:
    locator = page.locator(selector)

    count = locator.count()
    locators: List[Locator] = []

    # Get current viewport size
    vp = page.evaluate("() => ({ width: window.innerWidth, height: window.innerHeight })")

    for i in range(count):
        el = locator.nth(i)
        if el.is_visible():
            bb = el.bounding_box()
            if bb and bb["width"] > 0 and bb["height"] > 0:
                if (
                    bb["x"] >= 0 and bb["y"] >= 0 and
                    bb["x"] + bb["width"] <= vp["width"] and
                    bb["y"] + bb["height"] <= vp["height"]
                ):
                    locators.append(el)

    return locators