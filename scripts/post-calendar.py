#!/usr/bin/env python

import os, sys
from icalendar import Calendar, Event, vText
from datetime import datetime, date, time, timedelta
from PyHugo import *
from termcolor import cprint

defaultName = "Projektmacher"
paths = ["blogs/*/content", "content"]
posts = Posts.Posts(paths).postList()


def blogName(post):
    global defaultName
    path, file = os.path.split(post["__source"])
    path = path.split(os.sep)
    if path[0] == "content":
        return defaultName
    else:
        return path[1].title()


# See https://icalendar.readthedocs.io/en/latest/usage.html
cal = Calendar()
cal.add("prodid", "-//Projektemacher Calendar//projektemacher.org//")
cal.add("version", "2.0")

for post in posts:
    if "displayInList" in posts and post["displayInList"] == False:
        continue
    if "draft" in posts and post["draft"] == True:
        continue
    if "date" in post and post["date"] != None:
        event = Event()
        blog = blogName(post)
        title = "Untitled"
        if "title" in post:
            title = post["title"]
        event.add("summary", title)
        event.add("categories", [blog])

        if isinstance(post["date"], str):
            cprint("Ignoring {}: {}".format(post["__source"], post["date"]), "red")
        else:
            postDate = post["date"].date()
            event.add("dtstart", datetime.combine(postDate, time()))
            postDate += timedelta(days=1)
            event.add("dtend", datetime.combine(postDate, time()))

            cal.add_component(event)

sys.stdout.buffer.write(cal.to_ical())
