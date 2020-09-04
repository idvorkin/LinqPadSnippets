rm ~/tmp/brokenlinks.csv
scrapy runspider linkchecker.py -o ~/tmp/brokenlinks.csv
cat ~/tmp/brokenlinks.csv
