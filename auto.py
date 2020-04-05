import datetime
import schedule
import time
import threading
import os
import json
import os.path as pth

import scrapy_products.bin.parse_csv as parse_csv

from pathlib import Path


def run_threaded(job_func, *args, **kwargs):
    job_thread = threading.Thread(target=job_func, args=args, kwargs=kwargs)
    job_thread.start()


def crawl_listings(asins_csv, saved_as):
    cmd = "scrapy crawl amz_listings -a asins_csv={} -o {}".format(asins_csv, saved_as)
    os.system(cmd)


def generate_cases_keywords(titles_csv, brandsl=None, out_csv=None):
    from scrapy_products.spiders.amz import _AMZ_DOMAIN_TAB
    from scrapy_products.utils import TableHelper
    from scrapy_products.utils.cases_keywords_extractor import simple_extract

    hp = TableHelper(_AMZ_DOMAIN_TAB, "domain")
    rows, fieldnames = parse_csv.read_csv(titles_csv)

    # extract keywords from the title 
    for r in rows:
        r.update(keywords=simple_extract(
            title=r["title"],
            brandsl=brandsl,
            typecode=hp.lookup(r["domain"], "typecode")
        )) 
    fieldnames.append("keywords")

    out_csv = out_csv if out_csv else titles_csv
    parse_csv.write_csv(out_csv, rows, fieldnames)


def crawl_indicse(kwcsv, saved_as):
    cmd = "scrapy crawl amz_search_inds -a kwcsv={} -o {}".format(kwcsv, saved_as)
    os.system(cmd)


def crawl_latest_reviews(review_asins_path, saved_as):
    cmd = "scrapy crawl amz_reviews -a asins_path={} -o {}".format(review_asins_path, saved_as)
    os.system(cmd)

def clear_httpcache():
    print("clear httpcache")
    os.system("rm -rf .scrapy/httpcache")


def routine(asins_path, review_asins_path, tagname, data_dir):
    # create a subdirectory based on date
    today_str = datetime.date.today().strftime("%m%d")
    subdir = pth.join(data_dir, today_str)
    Path(subdir).mkdir(parents=True, exist_ok=True)

    listings_path = pth.join(
            subdir,
            "{}_listings.csv".format(tagname)
    )
    crawl_listings(asins_path, listings_path)

    # generate kwywords and write back
    generate_cases_keywords(listings_path)

    # search indices
    indices_path = pth.join(
        subdir,
        "{}_indices.csv".format(tagname)
    )
    crawl_indicse(listings_path, indices_path)

    # merge files from asins_path, listings_path, indices_path
    routine_path = pth.join(
        subdir,
        "{}_routine.csv".format(tagname)
    )
    parse_csv.merge_csv("asin", routine_path, asins_path, listings_path, indices_path)

    # get latesst reviews
    reviews_path = pth.join(
        subdir,
        "{}_latest_reviews.csv".format(tagname)
    )
    crawl_latest_reviews(review_asins_path, reviews_path)

def main(
        reserve_httpcache:("reserve the httpcache otherwise it will be cleared every time before routine started.", "flag", "r"),
        input_json: ("a json file contains a ( list of ) dict {'asins_path':ASINS_PATH, 'tagname':TAGNAME, 'review_asins_path':REVIEW_ASINS_PATH}, asins_path/review_asins_path is the path of a csv file with 'asin' in its header. tagname is for organizing outputs.", "option") = "./ROUTINES.json",
        data_dir : ("which directory to store collected data", "option") = "./data"
):
    """ Schedule Daily Routine
    """
    with open(input_json, "r") as json_file:
        inps = json.load(json_file)

        if not reserve_httpcache and inps:
            clear_httpcache()

        if isinstance(inps, dict):
            # Support single dict
            inps = [inps]

        for di in inps:
            asins_path, review_asins_path, tagname = di["asins_path"], di["review_asins_path"], di["tagname"]

            # schedule funcility reserved
            schedule.every().day.at("03:00").do(run_threaded, routine, asins_path, review_asins_path, tagname, data_dir)

        # run directly 
        schedule.run_all(delay_seconds=10)


if __name__ == '__main__':
    import plac; plac.call(main)
