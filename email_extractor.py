"""
This script extracts email addresses from a website.
It takes a URL or a file containing a list of URLs as input and outputs a CSV file containing the email addresses found on those pages.

Usage:
    python email_extractor.py -u <URL or file> [-o <output file>] [-m <max pages>]
    
    -u: the URL to start crawling from or a file containing a list of URLs to start crawling from
    -o: the output file to write the results to
    -m: the maximum number of pages to crawl
    
    Example:
    python email_extractor.py -u https://www.example.com -o emails.csv -m 100
    
    The output file will contain a list of email addresses and the URL of the page they were found on.

"""

import re
import requests
import bs4
from urllib.parse import urldefrag, urljoin, urlparse
import collections
import argparse

EMAIL_REGEX = r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+"


def crawler(start_url, max_pages=100):
    crawled = set()
    page_queue = collections.deque([start_url])  # queue of pages to be crawled
    domain = urlparse(start_url).netloc
    n_pages = 0  # number of pages successfully crawled so far
    n_failed = 0  # number of links that couldn't be crawled

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537"
    }

    session = requests.session()
    session.headers.update(headers)  # initialize the session

    emails = set()
    while n_pages < max_pages and page_queue:
        url = page_queue.popleft()  # get next page to crawl (FIFO queue)
        try:
            response = session.get(url, timeout=5)
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema):
            print("*FAILED*:", url)
            n_failed += 1
            continue
        if not response.headers["content-type"].startswith("text/html"):
            continue  # don't crawl non-HTML content

        for e in get_emails(response.text):
            if e not in emails:
                emails.add(e)
        soup = bs4.BeautifulSoup(response.text, "html.parser")

        # process the page
        crawled.add(url)
        n_pages += 1
        # get the links from this page and add them to the crawler queue
        links = get_links(url, domain, soup)
        for link in links:
            if link not in crawled and link not in page_queue:
                page_queue.append(link)

    print(
        f"{n_pages} pages crawled, {n_failed} links failed, {len(emails)} emails found."
    )
    return [{"address": e, "location": start_url} for e in emails]


def get_links(pageurl, domain, soup):
    links = [a.attrs.get("href") for a in soup.select("a[href]")]
    links = [urldefrag(link)[0] for link in links]
    links = [
        link if bool(urlparse(link).netloc) else urljoin(pageurl, link)
        for link in links
    ]
    links = [link for link in links if same_domain(urlparse(link).netloc, domain)]
    return links


def same_domain(netloc1, netloc2):
    return netloc1.split(".")[-2:] == netloc2.split(".")[-2:]


def get_emails(raw_text):
    return [email for email in re.findall(EMAIL_REGEX, raw_text)]


if __name__ == "__main__":
    # The arguments are:
    # -u: the URL to start crawling from or a file containing a list of URLs to start crawling from
    # -o: the output file to write the results to
    # -m: the maximum number of pages to crawl

    parser = argparse.ArgumentParser(
        description="Extract email addresses from a website."
    )
    parser.add_argument(
        "-u",
        "--url",
        help="the URL to start crawling from or a file containing a list of URLs to start crawling from",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="the output file to write the results to",
        required=False,
        default="emails.csv",
    )
    parser.add_argument(
        "-m",
        "--max",
        help="the maximum number of pages to crawl",
        type=int,
        default=100,
    )
    args = parser.parse_args()

    if args.url.startswith("http"):
        urls = [args.url]
    else:
        urls = [url.strip() for url in open(args.url).readlines()]

    emails = []
    for url in urls:
        print(f"Crawling {url}...")
        emails += crawler(url, args.max)

    with open(args.output, "w") as f:
        f.write("address,location\n")
        for e in emails:
            f.write(f"{e['address']},{e['location']}\n")

    print(f"Results written to {args.output}")
