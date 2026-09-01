from __future__ import annotations

from chik.seeder.crawler import Crawler
from chik.seeder.crawler_api import CrawlerAPI
from chik.seeder.crawler_rpc_api import CrawlerRpcApi
from chik.server.start_service import Service

CrawlerService = Service[Crawler, CrawlerAPI, CrawlerRpcApi]
