import datetime
import json
import os
import sys
import traceback

import requests

from appdirs import user_data_dir

_request_headers = {'content-type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}


class FeedSource():
    def __init__(self, scaleVolumeBy=1.0,
                 enable=True,
                 allowFailure=True,
                 timeout=5,
                 quotes=[],
                 bases=[],
                 aliases={},
                 **kwargs):
        self.scaleVolumeBy = scaleVolumeBy
        self.enabled = enable
        self.allowFailure = allowFailure
        self.timeout = timeout
        self.bases = bases
        self.aliases = aliases
        self.quotes = quotes

        [setattr(self, key, kwargs[key]) for key in kwargs]
        # Why fail if the scaleVolumeBy is 0
        if self.scaleVolumeBy == 0.0:
            self.allowFailure = True

    def fetch(self):
        try:
            feed = self._fetch()
            self.updateCache(feed)
            return feed
        except Exception as e:
            traceback.print_exc()
            print("\n{0} encountered an error while loading live data. Trying to recover from cache!".format(type(self).__name__))

            # Terminate if not allow Failure
            if not self.allowFailure:
                sys.exit("\nExiting due to exchange importance on %s!" % type(self).__name__)

        try:
            return self.recoverFromCache()
        except:
            print("We were unable to fetch live or cached data from %s. Skipping", type(self).__name__)

    def today(self):
        return datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")

    def recoverFromCache(self):
        cacheFile = self.getCacheFileName()
        if os.path.isfile(cacheFile):
            with open(self.getCacheFileName(), 'r') as fp:
                return json.load(fp)
        return {}

    def getCacheFileName(self):
        cacheDir = os.path.join(
            user_data_dir("bitshares_pricefeed", "ChainSquad GmbH"),
            "cache",
            type(self).__name__
        )
        if not os.path.exists(cacheDir):
            os.makedirs(cacheDir)
        return os.path.join(cacheDir, self.today() + ".json")

    def updateCache(self, feed):
        with open(self.getCacheFileName(), 'w') as fp:
            json.dump(feed, fp)

    def alias(self, symbol):
        if  symbol in self.aliases:
            return self.aliases[symbol]
        return symbol

    def add_rate(self, feed, base, quote, price, volume):
        resolved_base = self.alias(base)
        if resolved_base not in feed:
            feed[resolved_base] = {}
        feed[resolved_base][self.alias(quote)] = { "price": price, "volume": volume * self.scaleVolumeBy }
        return feed
