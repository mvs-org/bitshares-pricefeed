import requests
from . import FeedSource, _request_headers


class BitcoinIndonesia(FeedSource):
    def _fetch(self):
        feed = {}
        for base in self.bases:
            for quote in self.quotes:
                if quote == base:
                    continue
                url = "https://vip.bitcoin.co.id/api/%s_%s/ticker" % (quote.lower(), base.lower())
                response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
                result = response.json()["ticker"]
                self.add_rate(feed, base, quote, float(result["last"]), float(result["vol_" + quote.lower()]))
                feed[self.alias(base)]["response"] = response.json()
        return feed
