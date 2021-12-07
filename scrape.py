import time
import datetime
import requests
import sys

class ScrapeError(Exception):
    pass

def scrape(n):
    """
    Scrape AoC website for inputs
    """
    from credentials import credentials
    
    s = 'Day' + str(n).zfill(2)
    
    uri = f'https://adventofcode.com/2021/day/{n}/input'

    d = datetime.datetime(2021, 12, n, 15, 30, 0)
    delta = time.mktime(d.timetuple()) - time.time()

    if delta < 30:
        time.sleep(max(0, delta + 0.1))

        with requests.Session() as r:
            response = r.get(uri, cookies=credentials, timeout=5).text

        with open(f"{s}/{s}.in", 'w') as f:
            f.write(response)
    else:
        raise ScrapeError("You are running this too early.")

if __name__ == "__main__":
    # If an argument is passed to script, run for that day else do next day from max
    if len(sys.argv) > 1:
        d = int(sys.argv[1])
        scrape(d)
    else:
        print("Specify day when running as main.\nE.g. py scrape.py <day>")
    
