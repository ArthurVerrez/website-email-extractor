# Website Email Extractor
## Description
This is a simple python script that extracts email addresses from a website. It uses the requests and re modules to do so. It also uses the argparse module to parse command line arguments.

## Installation
```bash
git clone https://github.com/ArthurVerrez/website-email-extractor.git
cd website-email-extractor
pip install -r requirements.txt
```

## Usage

```bash
python email_extractor.py -u <URL or file> [-o <output file>] [-m <max pages>]
```

*-u*: the URL to start crawling from or a file containing a list of URLs to start crawling from\
*-o*: the output file to write the results to (Optional, default: emails.csv)\
*-m*: the maximum number of pages to crawl (Optional, default: 100)
    
## Examples
```bash
python email_extractor.py -u https://www.flaneer.com -o flaneer_emails.csv -m 200
```

```bash
python email_extractor.py -u urls.txt
```

## Disclaimer
This script is intended to be used on websites that you own or have permission to crawl. It is mostly useful to verify you haven't left any email addresses in your website's source code.

Any misuse of this script is not the responsibility of the developer.