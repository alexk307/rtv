# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import curses

from .page import Page, PageController
from .content import SubscriptionContent
from .objects import Color, Navigator
from .terminal import Terminal


class SubscriptionController(PageController):
    character_map = {}


class SubscriptionPage(Page):

    def __init__(self, reddit, term, config, oauth):
        super(SubscriptionPage, self).__init__(reddit, term, config, oauth)

        self.content = SubscriptionContent.from_user(reddit, term.loader)
        self.controller = SubscriptionController(self)
        self.nav = Navigator(self.content.get)
        self.subreddit_data = None

    @SubscriptionController.register(curses.KEY_F5, 'r')
    def refresh_content(self, order=None, name=None):
        "Re-download all subscriptions and reset the page index"

        # reddit.get_my_subreddits() does not support sorting by order
        if order:
            self.term.flash()
            return

        with self.term.loader():
            self.content = SubscriptionContent.from_user(self.reddit,
                                                         self.term.loader)
        if not self.term.loader.exception:
            self.nav = Navigator(self.content.get)

    @SubscriptionController.register(curses.KEY_ENTER, Terminal.RETURN,
                                     curses.KEY_RIGHT, 'l')
    def select_subreddit(self):
        "Store the selected subreddit and return to the subreddit page"

        self.subreddit_data = self.content.get(self.nav.absolute_index)
        self.active = False

    @SubscriptionController.register(curses.KEY_LEFT, Terminal.ESCAPE, 'h', 's')
    def close_subscriptions(self):
        "Close subscriptions and return to the subreddit page"

        self.active = False

    def _draw_banner(self):
        # Subscriptions can't be sorted, so disable showing the order menu
        pass

    def _draw_item(self, win, data, inverted):
        n_rows, n_cols = win.getmaxyx()
        n_cols -= 1  # Leave space for the cursor in the first column

        # Handle the case where the window is not large enough to fit the data.
        valid_rows = range(0, n_rows)
        offset = 0 if not inverted else -(data['n_rows'] - n_rows)

        row = offset
        if row in valid_rows:
            attr = curses.A_BOLD | Color.YELLOW
            self.term.add_line(win, '{name}'.format(**data), row, 1, attr)

        row = offset + 1
        for row, text in enumerate(data['split_title'], start=row):
            if row in valid_rows:
                self.term.add_line(win, text, row, 1)