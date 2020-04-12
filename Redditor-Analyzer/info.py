import time
from datetime import datetime
from datetime import timedelta
import requests
import threading
import os

import praw
import pygame

import pgx
from reference import references

"""
Ideas:
Break down activity over weekdays
"""

# object to get and store all of the information on the selected redditor
class Info:
    # redditor is a Redditor object of praw
    # attributes it finds or calculates:
    # age (timedelta)
    # created_date (datetime)
    # profile_pic (pygame.Surface)
    # total_karma (int)
    # comment_karma (int)
    # link_karma (int)
    # suspended (bool)

    def __init__(self):
        self.redditor = references.redditor

        self.suspended = False
        references.redditor_info = self

        if not getattr(self.redditor, "id", False):
            self.suspended = True

        else:
            init_methods = [
                self._find_account_age,
                self._find_account_pic,
                self._find_account_karma,
                self._find_account_activity,
            ]

            init_threads = [threading.Thread(target=method) for method in init_methods]
            [thread.start() for thread in init_threads]

    def __getattr__(self, attribute):
        if attribute in self.__dict__:
            return self.__dict__[attribute]
        else:
            return None

    def _find_account_age(self):
        created_timestamp = self.redditor.created_utc

        self.created_date = datetime.utcfromtimestamp(created_timestamp)
        self.age = datetime.utcnow() - self.created_date

    def _find_account_pic(self):
        pic_url = self.redditor.icon_img

        extensions = {".png": 0, ".jpg": 0, ".jpeg": 0}

        for extension in extensions:
            if extension in pic_url:
                extensions[extension] = 1

        if sum(extensions.values()) > 1:
            raise ValueError("Unable to determine correct filetype (found multiple)")

        if sum(extensions.values()) == 0:
            raise ValueError("Unable to determine correct filetype (found none)")

        for extension in extensions:
            if extensions[extension] == 1:
                pic_type = extension
                break

        if not os.path.isdir(pgx.handle_path("data/temp")):
            os.mkdir(pgx.handle_path("data/temp"))

        with open(pgx.handle_path(f"data/temp/profile{pic_type}"), "wb") as handle:
            response = requests.get(pic_url, stream=True)

            if not response.ok:
                print(response)

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)

        self.profile_pic = pgx.image.load(f"data/temp/profile{pic_type}")

    def _find_account_karma(self):
        self.comment_karma = self.redditor.comment_karma
        self.link_karma = self.redditor.link_karma
        self.total_karma = self.link_karma + self.comment_karma

    def _find_account_activity(self):
        self.entries = []
        subreddits = {}
        self.num_posts = 0
        self.num_comments = 0

        first_entry = True

        for entry in self.redditor.new(limit=250):
            self.entries.append(entry)

            # pinned posts show up at the top of new, but they aren't the most recent thing
            # tested out using the .stickied attribute
            if first_entry and not entry.stickied:
                when = datetime.utcnow() - datetime.utcfromtimestamp(entry.created_utc)
                self.last_activity = {"time": when, "item": entry}
                first_entry = False

            if entry.subreddit in subreddits:
                subreddits[entry.subreddit] += 1
            else:
                subreddits[entry.subreddit] = 1

            t = type(entry)
            if t == praw.models.reddit.submission.Submission:
                self.num_posts += 1
            elif t == praw.models.reddit.comment.Comment:
                self.num_comments += 1
            else:
                print(f"Unrecognized type {t}")

        if self.last_activity == None:
            self.last_activity = {"time": "never"}

        self.subreddits = list(subreddits.keys())

        # sorting subreddits into a list [(sub, members)], sorting by size
        subsorted = self.subreddits
        subsorted = [(sub, sub.subscribers) for sub in subsorted]
        subsorted.sort(key=lambda x: x[1])
        self.subreddit_size = subsorted

        # sorting subreddits into a list [(sub, events there)], sorting by event num
        subsorted = list(subreddits.items())
        subsorted.sort(key=lambda x: x[1])
        self.subreddit_activity = subsorted
