import curses
import re
import sys
import time
import urllib2

# Curses config for prettier output
stdscr = curses.initscr()

curses.start_color()

curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

def fetch(uri):
    # Generic http getter to retrieve ticker data from some URI
    # Error handling could use some love
    try:
        return urllib2.urlopen(uri).read()
    except urllib2.HTTPError, err:
        print("HTTP Error - Retrying in 5 seconds")
        time.sleep(5)
        return fetch(uri)
    except urllib2.URLError, err:
        print("DNS Resolution Error - Retrying in 5 seconds")
        time.sleep(5)
        return fetch(uri)

    return res

def quote(ticker):
    # So I discovered this neat trick with Google Finance...
    # This is mostly an experiment, it would be much more robust to use an official API.
    uri = "http://finance.google.com/finance/info?client=ig&q=NYSE:" + ticker
    raw = re.sub('[/\{\[\]\}\n]*', "", fetch(uri)).split(",")

    def beautify(data, delimiter):
        return data.split(delimiter)

    clean = {}

    # Remove formatting and other ugliness before printing.
    for line in raw:
        line = line.replace(": ", ":").replace(" :", ":")
        split = beautify(line, "\":\"")
        clean[split[0].replace("\"", "")] = split[-1].replace("\"", "")

    return clean

def main():
    # Iterate the inputs and pull in necessary data for each ticker, print as data become available.
    for index, ticker in enumerate(sys.argv[1:]):
        data = quote(ticker)

        # Prettify output so that indentation is consistent regardless of ticker length.
        while len(ticker) < 4:
            ticker += " "
        ticker += ": "

        # Print ticker symbol.
        stdscr.addstr(index, 0, ticker.upper(), curses.color_pair(1))
        stdscr.addstr(data["l_cur"])
        stdscr.addstr(index, 13, "(")

        # Print % change for the day, write negative changes in red and positive changes in green.
        if data["cp"][0] == "-":
            stdscr.addstr(data["cp"], curses.color_pair(2))
        else:
            stdscr.addstr(index, 14, " ")
            stdscr.addstr(index, 15, data["cp"], curses.color_pair(3))
        stdscr.addstr("%)")

        stdscr.refresh()

while True:
    main()
    time.sleep(15)
