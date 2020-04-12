from abc import ABC
import threading
import time

import pygame
import praw
import prawcore

import pgx
from reference import references
import info


# Abstract base class
class Scene(ABC):
    def __init__(self):
        pass

    def run(self):
        pass


class EnterUsername(Scene):
    def __init__(self):
        self.input = pgx.ui.InputGetter(
            pgx.Location(["center", 100], "center"),
            pgx.Text("Username Here", 45),
            pgx.ui.Box(
                pgx.Location([-10, -10, "width+20", "height+20"]), (255, 255, 255), 2
            ),
            length_limit=20,
            allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_",
        )
        self.status_box = self.input.get_components()[0]

        self.status_text = pgx.ui.TextBox(
            pgx.Location(["center", 54], "center"), pgx.Text("TESTING", 20)
        )
        self.input.add(self.status_text)

        self.last_text = self.input.text.text
        self.users_valid = {}  # dictionary of usernames : validity

    def run(self):
        text = self.input.text.text

        if text != self.last_text:
            self.last_text = text
            checker = threading.Thread(
                target=self._is_user_valid, args=(text,), daemon=True
            )
            checker.start()

        user_valid = False if text not in self.users_valid else self.users_valid[text]
        self.status_box.color = (0, 255, 0) if user_valid else (255, 0, 0)
        self.status_text.color = (0, 255, 0) if user_valid else (255, 0, 0)

        self.status_text.text.text = (
            "Press Space to Proceed" if user_valid else "This is not a real person"
        )

        if (
            text in self.users_valid
            and self.users_valid[text]
            and pygame.K_SPACE in pgx.key.downs()
        ):
            references.redditor = references.reddit.redditor(text)
            references.redditor_info = None
            print(references.redditor.name)
            info_getter = threading.Thread(target=info.Info)
            info_getter.start()

            # removes old info displays
            for i, scene in enumerate(references.active_scenes):
                if isinstance(scene, DisplayInfo):
                    del references.active_scenes[i]

            # adds a new info display
            references.active_scenes.append(DisplayInfo())

        self.input.display()

    def _is_user_valid(self, name):
        if len(name) > 2:  # usernames must be between 3 and 20 characters
            try:
                redditor = references.reddit.redditor(name)
                redditor.id
                self.users_valid[name] = True
            except prawcore.exceptions.NotFound:
                self.users_valid[name] = False
            except AttributeError:
                self.users_valid[name] = True


class DisplayInfo(Scene):
    def __init__(self):
        self.info = references.redditor_info

        # UI elements
        self.pic = pgx.ui.ImageBox(
            pgx.Location([50, 50, 128, 128]), pygame.Surface((128, 128))
        )
        self.date = pgx.ui.TextBox(
            pgx.Location([50, 200]),
            pgx.Text("Account Created: ...", 20, color=(40, 40, 40)),
        )
        self.age = pgx.ui.TextBox(
            pgx.Location([50, 230]),
            pgx.Text("Account Age: ...", 20, color=(40, 40, 40)),
        )
        self.last_activity = pgx.ui.TextBox(
            pgx.Location([50, 260]),
            pgx.Text("Last Active: ...", 20, color=(40, 40, 40)),
        )
        self.karma = pgx.ui.TextBox(
            pgx.Location([50, 290]),
            pgx.Text("Account Karma: ...", 20, color=(40, 40, 40)),
        )
        self.section = pgx.ui.TextBox(
            pgx.Location([50, 320]),
            pgx.Text(
                f"Loading analysis of u/{references.redditor.name}'s activity",
                20,
                color=(40, 40, 40),
            ),
        )
        self.posts_comments = pgx.ui.TextBox(
            pgx.Location([50, 350]),
            pgx.Text("Post: Comment ratio", 20, color=(40, 40, 40)),
        )
        self.subs_frequented = pgx.ui.TextBox(
            pgx.Location([50, 380]),
            pgx.Text("Their frequented subreddits:", 20, color=(40, 40, 40)),
        )
        self.subs_obscure = pgx.ui.TextBox(
            pgx.Location([50, 410]),
            pgx.Text("Their most obscure subreddit activity:", 20, color=(40, 40, 40)),
        )
        self.subs_popular = pgx.ui.TextBox(
            pgx.Location([50, 440]),
            pgx.Text("Their most popular subreddit activity:", 20, color=(40, 40, 40)),
        )

        self.entry_loading = pgx.ui.TextBox(
            pgx.Location(["right-10", "bottom-30"], "right"), pgx.Text("", 20)
        )

        self.panel = pgx.ui.Panel(pgx.Location())
        self.panel.add(
            self.pic,
            self.date,
            self.age,
            self.last_activity,
            self.karma,
            self.section,
            self.posts_comments,
            self.subs_frequented,
            self.subs_obscure,
            self.subs_popular,
            self.entry_loading,
        )

        self.karma_displayed = False
        self.pic_displayed = False
        self.age_displayed = False
        self.last_activity_displayed = False
        self.analysis_displayed = False

    def run(self):
        if self.info.suspended:
            self.panel.clear_components()
            self.panel.add(
                pgx.ui.TextBox(
                    pgx.Location(["center", 200], "center"),
                    pgx.Text("This account has most likely been suspended", 20),
                )
            )

        else:
            if (
                self.info.link_karma != None
                and self.info.total_karma != None
                and self.info.comment_karma != None
                and not self.karma_displayed
            ):
                self._display_account_karma()
                self.karma_displayed = True

            if self.info.profile_pic != None and not self.pic_displayed:
                self._display_account_pic()
                self.pic_displayed = True

            if (
                self.info.created_date != None
                and self.info.age != None
                and not self.age_displayed
            ):
                self._display_account_times()
                self.age_displayed = True

            if self.info.last_activity != None and not self.last_activity_displayed:
                self._display_account_last_active()
                self.last_activity_displayed = True

            if (
                self.info.subreddit_activity != None
                and self.info.subreddit_size != None
                and self.info.num_posts != None
                and self.info.num_comments != None
                and not self.analysis_displayed
            ):
                self._display_account_analysis()
                self.analysis_displayed = True
                self.entry_loading.visible = False

            if not self.analysis_displayed:
                try:
                    num_events = len(self.info.entries)
                except:
                    num_events = 0
                self.entry_loading.text.text = f"Processing Events: {num_events}"

        self.panel.display()

    def _display_account_pic(self):
        self.pic.image = pygame.transform.scale(self.info.profile_pic, (128, 128))

    # timedelta -> string days and years
    def _format_dates(self, age):
        days_old = age.days
        years_old = days_old // 365
        days_old -= years_old * 365

        years_old = (
            f"{years_old} year{'s' if years_old > 1 else ''}, " if years_old > 0 else ""
        )
        days_old = (
            f"{days_old} day{'s' if days_old > 1 else ''}" if days_old > 0 else ""
        )

        return years_old + days_old

    def _display_account_times(self):
        self.date.text.text = "Account Created: " + self.info.created_date.strftime(
            f"%B {self.info.created_date.day}, %Y"
        )
        self.date.text.color = (0, 0, 0)

        str_time = self._format_dates(self.info.age)
        self.age.text.text = f"Account Age: {str_time} old"
        self.age.text.color = (0, 0, 0)

    def _display_account_last_active(self):
        last_activity = self.info.last_activity
        if last_activity["time"] == "never":
            self.last_activity.text.text = f"Last Active: Never"
            self.last_activity.text.color = (0, 0, 0)
        else:
            str_time = self._format_dates(last_activity["time"])
            str_time = "today" if str_time == "" else str_time + " ago"
            act_type = (
                "post"
                if isinstance(
                    last_activity["item"], praw.models.reddit.submission.Submission
                )
                else "comment"
            )
            act_sub = last_activity["item"].subreddit.display_name
            self.last_activity.text.text = (
                f"Last Active: {str_time}, with a {act_type} in r/{act_sub}"
            )
            self.last_activity.text.color = (0, 0, 0)

    def _format_nums(self, num):
        # setting start number : (suffix, rounding, divisor)
        configurations = {
            1000: ("K", 1, 1000),
            10000: ("K", 1, 1000),
            100000: ("K", 0, 1000),
            1000000: ("M", 1, 1000000),
            10000000: ("M", 1, 1000000),
            100000000: ("M", 0, 1000000),
        }
        search_config = list(configurations.keys())
        search_config.sort()

        if num < search_config[0]:
            return str(num)

        config = False
        for s in search_config:
            if s < num:
                config = configurations[s]

        if config:
            return str(round(num / config[2], config[1])) + config[0]

        raise NotImplementedError("Numbers this big '{num}' can not yet be formatted")

    def _display_account_karma(self):
        total = self._format_nums(self.info.total_karma)
        link = self._format_nums(self.info.link_karma)
        comment = self._format_nums(self.info.comment_karma)
        self.karma.text.text = (
            f"Account Karma: {total} -- {link} from posts and {comment} from comments"
        )
        self.karma.text.color = (0, 0, 0)

    def _display_account_analysis(self):
        self.section.text.text = (
            f"Over the last 250 actions, u/{references.redditor.name}:"
        )
        self.section.text.color = (0, 0, 0)

        posts = self.info.num_posts
        comments = self.info.num_comments
        self.posts_comments.text.text = f"Has posted {posts} time{'s' if posts != 1 else ''}, and commented {comments} time{'s' if comments != 1 else ''}"
        self.posts_comments.text.color = (0, 0, 0)

        activity = self.info.subreddit_activity
        freqsubs = "Their frequented subreddits:"
        if not activity:
            freqsubs += " None"
        for _ in range(2):
            if activity:
                sub, num = activity.pop()
                freqsubs += f" r/{sub.display_name} {num} time{'s' if num > 1 else ''}"
        self.subs_frequented.text.text = freqsubs
        self.subs_frequented.text.color = (0, 0, 0)

        activity = self.info.subreddit_size
        obscure = " None"
        popular = " None"
        if activity:
            obscure = list(activity[0])
            obscure[1] = self._format_nums(obscure[1])
            obscure = f" r/{obscure[0].display_name} ({obscure[1]} subs)"
            popular = list(activity[-1])
            popular[1] = self._format_nums(popular[1])
            popular = f" r/{popular[0].display_name} ({popular[1]} subs)"

        self.subs_obscure.text.text += obscure
        self.subs_obscure.text.color = (0, 0, 0)
        self.subs_popular.text.text += popular
        self.subs_popular.text.color = (0, 0, 0)
