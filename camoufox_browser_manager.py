import asyncio
import os
import pprint

from camoufox.sync_api import Camoufox, BrowserContext # Import BrowserContext
from profile_store import load_or_create_fp, _paths
from typing import Callable, Any

from profile import Profile
from vpn import connect_and_verify, disconnect_vpn


class CamoufoxBrowser:
    """
    Manages the lifecycle of a Camoufox browser instance for a specific profile.
    Initializes with a Profile object.
    """
    def __init__(self, profile_data: Profile):
        self.profile = profile_data

    """
        if not all([self.profile.profile,
                    self.profile.proxy_address,
                    self.profile.proxy_port,
                    self.profile.proxy_username,
                    self.profile.proxy_password]):
            raise ValueError(
                f"Incomplete profile data provided for CamoufoxBrowser for profile: {self.profile.profile}"
            )
        if self.profile.proxy_username is None:
            raise ValueError(
                f"Proxy username is missing for profile: {self.profile.profile}"
            )
    """


    # Update the type hint for playwright_activity to include BrowserContext
    def launch(self, playwright_activity: Callable[[Any, Any, BrowserContext], None]):
        """
        Launches a Camoufox browser instance with the configured profile and proxy,
        then executes the provided Playwright activity.

        Args:
            playwright_activity: A callable (function) that takes three arguments:
                                 1. The CamoufoxBrowser instance itself.
                                 2. The Playwright `page` object.
                                 3. The Camoufox `BrowserContext` object.
                                 This function should contain all the specific Playwright actions
                                 you want to perform within the browser.
        """



        asyncio.run(connect_and_verify(self.profile))

        fp = load_or_create_fp(self.profile.profile)
        #pprint.pprint(fp)
        profile_dir, _ = _paths(self.profile.profile)

        try:
            with Camoufox(

                    persistent_context=True,
                    user_data_dir=str(profile_dir),
                    fingerprint=fp,
                    geoip=True,
                    i_know_what_im_doing=True,
                    #proxy={
                    #    "server": f"http://{self.profile.proxy_address}:{self.profile.proxy_port}",
                    #    "username": self.profile.proxy_username,
                    #    "password": self.profile.proxy_password,
                    #},
                    humanize = 1.0,
                    locale="en-US",
                    config={
                        'disableTheming': True
                    }
            ) as ctx:
                page = ctx.pages[0]

                # Pass the ctx object to the playwright_activity
                playwright_activity(self, ctx, page)

        except Exception as e:
            print(f"An error occurred for profile {self.profile.profile}: {e}")