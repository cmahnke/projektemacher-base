#!/usr/bin/env python

import os, argparse, pathlib, sys, asyncio, httpcore, time
from urllib.parse import urlparse
from dateutil.parser import parse
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
from termcolor import cprint

archive_prefix = "https://web.archive.org/save/"
available_prefix = "http://archive.org/wayback/available?url="
default_dir = "./docs"
exclude = [
    "localhost",
    "static.projektemacher.org",
    "projektemacher.org",
    "de.wikipedia.org",
    "en.wikipedia.org",
    "github.com",
    "gohugo.io",
    "archive.org",
    "www.worldcat.org",
    "www.wikidata.org",
]
# Maximal age in days
max_age = 60


def check_availability(url):
    available_url = f"{available_prefix}{url}"
    try:
        req = httpx.get(available_url)
        req.raise_for_status()
        json = req.json()
        if "archived_snapshots" in json and json["archived_snapshots"]:
            last = json["archived_snapshots"]["closest"]["timestamp"]
            last = parse(last, fuzzy=True)
            age = datetime.now() - last
            if age.days > max_age:
                cprint(f"URL {url} snapshot is older then {max_age}!", "yellow")
                return False
            cprint(f"URL {url} has been archived within the last {max_age} days!", "green")
            return True
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            cprint(f"Rate limited checking availability for {url}. Assuming not archived.", "yellow")
            return False
        cprint(f"HTTP Error checking availability for {url}: {e}", "red")

    cprint(f"URL {url} is not archived!", "yellow")
    return False


async def archive_api(url, access_key, secret_key, client):
    api_url = "https://web.archive.org/save/"
    headers = {
        "Accept": "application/json",
        "Authorization": f"LOW {access_key}:{secret_key}"
    }
    data = {
        "url": url,
        "capture_outlinks": "1",
        "skip_first_archive": "1"
    }

    response = await client.post(api_url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()

async def archive(urls, client, access_key=None, secret_key=None):
    async_reqs = []
    for url in urls:
        archive_url = f"{archive_prefix}{url}"
        try:
            if not check_availability(url):

                async def req(url, original_url):
                    try:
                        retries = 3
                        for i in range(retries):
                            try:
                                if access_key and secret_key:
                                    await archive_api(original_url, access_key, secret_key, client)
                                else:
                                    resp = await client.get(url)
                                    resp.raise_for_status()
                                return  # Success
                            except httpx.HTTPStatusError as e:
                                if e.response.status_code == 429 and i < retries - 1:
                                    retry_after = int(e.response.headers.get("Retry-After", "5"))
                                    cprint(f"Rate limited saving {url}. Retrying after {retry_after} seconds...", "yellow")
                                    await asyncio.sleep(retry_after)
                                else:
                                    raise
                    except (
                        httpx.ReadTimeout,
                        httpx.TimeoutException,
                        httpx.NetworkError,
                        httpx.HTTPStatusError,
                        httpcore.ReadTimeout,
                    ) as error:
                        cprint(f"HTTP Error {error.__class__.__name__}: {str(error)}", "red")

                async_reqs.append(req(archive_url, url))
                print(f"Saving {archive_url}")
        except:
            cprint(f"Failed to check availability of {url}", "red")
    return async_reqs


def filter_links(links):
    def url_filter(item):
        if item is not None and item.startswith("http"):
            up = urlparse(item)
            if not up.hostname in exclude:
                return item

    flat = sum(links, [])
    unique = list(set(flat))

    return list(filter(url_filter, unique))


def extract_links(file):
    urls = []
    with open(file, "r") as handle:
        soup = BeautifulSoup(handle.read(), "html.parser")
        for link in soup.find_all("a"):
            urls.append(link.get("href"))
    return urls


def build_file_list(dir):
    htmls = []
    for path, dirnames, files in os.walk(dir):
        for file in files:
            (base, ext) = os.path.splitext(file)
            if ext != "" and ext in (".html"):
                htmls.append(os.path.join(path, file))
    return htmls


def build_url_list(dir):
    files = build_file_list(dir)
    urls = []
    for file in files:
        urls.append(extract_links(file))
    urls = filter_links(urls)
    return urls


async def main() -> int:
    global max_age
    parser = argparse.ArgumentParser(prog="archive.py")
    parser.add_argument("--dir", "-d", type=pathlib.Path, help="Path to posts to process")
    parser.add_argument("--exclude", "-e", nargs="+", help="Host names to exclude")
    parser.add_argument("--age", "-a", type=int, default=max_age, help=f"Maximum age (default {max_age})")
    parser.add_argument("--output", "-o", type=str, help=f"Output URL list file name")
    parser.add_argument("--access-key", help="Internet Archive Access Key")
    parser.add_argument("--secret-key", help="Internet Archive Secret Key")

    args = parser.parse_args()

    if args.access_key is None and "INTERNET_ARCHIVE_ACCESS_KEY" in os.environ:
        args.access_key = os.environ["INTERNET_ARCHIVE_ACCESS_KEY"]
        cprint("Using INTERNET_ARCHIVE_ACCESS_KEY from environment", "yellow")

    if args.secret_key is None and "INTERNET_ARCHIVE_SECRET_KEY" in os.environ:
        args.secret_key = os.environ["INTERNET_ARCHIVE_SECRET_KEY"]
        cprint("Using INTERNET_ARCHIVE_SECRET_KEY from environment", "yellow")

    max_age = args.age

    if args.dir is not None:
        dir = args.dir
    else:
        dir = default_dir

    if args.exclude is not None:
        for excl in args.exclude:
            exclude.extend(excl.split(","))
        cprint(f"Excluding {exclude}", "green")

    urls = build_url_list(dir)

    # Try to avoid "Too many requests" see https://www.python-httpx.org/advanced/resource-limits/
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    client = httpx.AsyncClient(timeout=120, limits=limits)
    async_reqs = await archive(urls, client, access_key=args.access_key, secret_key=args.secret_key)
    await asyncio.gather(*async_reqs)
    await client.aclose()
    if args.output is not None:
        with open(args.output, "w") as url_file:
            for url in urls:
                url_file.write(url + "\n")
        cprint(f"Saved URLs to {args.output}", "green")
    cprint(f"Saved {len(async_reqs)} URLs", "green")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
