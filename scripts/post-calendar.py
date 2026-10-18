#!/usr/bin/env python

import os, sys, glob
from icalendar import Calendar, Event, vText
from datetime import datetime, date, time, timedelta
sys.path.append(os.path.dirname(__file__))
from PyHugo import Content
from termcolor import cprint

defaultName = "Projektmacher"
paths = ["blogs/*/content", "content"]
cal = Calendar()
cal.add("prodid", "-//Projektemacher Calendar//projektemacher.org//")
cal.add("version", "2.0")


def blogName(post):
    global defaultName
    path, file = os.path.split(post.getFile())
    path = path.split(os.sep)
    if path[0] == "content":
        return defaultName
    else:
        return path[1].title()


for path in paths:
    for expandedPath in glob.glob(path):
        try:
            content = Content(expandedPath)
        except ValueError as e:
            cprint(f"Skipping {expandedPath}: no site config found ({e})", "red")
            continue
        for post in content.posts:
            # Skip language variants sharing the same (unsuffixed) file
            processedFiles = set()
            for lang, file in post.files.items():
                if file in processedFiles:
                    continue
                processedFiles.add(file)
                metadata = post.getMetadata(lang)

                def metadataParam(name):
                    """Look up a front matter key case insensitively (Hugo parameters are)."""
                    for key in metadata:
                        if key.lower() == name.lower():
                            return metadata[key]
                    return None

                if metadataParam("displayInList") == False:
                    continue
                if metadataParam("draft") == True or post.draft == True:
                    continue
                postDate = metadata.get("date")
                if postDate is None:
                    continue
                event = Event()
                blog = blogName(post)
                title = "Untitled"
                if "title" in metadata:
                    title = metadata["title"]
                event.add("summary", title)
                event.add("categories", [blog])

                if isinstance(postDate, str):
                    cprint("Ignoring {}: {}".format(file, postDate), "red")
                    continue

                event.add("dtstart", datetime.combine(postDate.date() if isinstance(postDate, datetime) else postDate, time()))
                endDate = postDate.date() if isinstance(postDate, datetime) else postDate
                endDate += timedelta(days=1)
                event.add("dtend", datetime.combine(endDate, time()))
                cal.add_component(event)

sys.stdout.buffer.write(cal.to_ical())
