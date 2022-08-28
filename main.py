from dataclasses import dataclass
import json
import logging
from typing import Any

import google.cloud.logging

client = google.cloud.logging.Client()
client.setup_logging()


@dataclass
class RankedProduct:
    name: str
    url: str
    rank: float


class RankedProductEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        return o.__dict__


def normalize(v, min=0, max=100):
    full_range = max - min
    return 0.5 if full_range == 0 else (v - min) / full_range


def rank(product, config, max_price) -> RankedProduct:
    price_factor = normalize(max_price - product['price'], max=max_price)
    review_score = product['reviewScore']
    rating_factor = normalize(review_score['score'], max=review_score['maxScore'])
    trusted_brands = config['trustedBrands'] if 'trustedBrands' in config else []
    brand_factor = 1 if product['brandName'] in trusted_brands else 0
    price_importance = normalize(config['priceImportance'])
    rating_importance = normalize(config['ratingImportance'])
    brand_importance = normalize(config['brandImportance'])
    rank = (price_factor * price_importance +
            rating_factor * rating_importance +
            brand_factor * brand_importance) / (price_importance + rating_importance + brand_importance)
    return RankedProduct(product['name'], product['url'] if 'url' in product else None, round(rank, 2))


def main(request):
    logging.info(f"Incoming request\n{request.json}")
    rank_request = request.get_json()
    max_price = max(
        map(lambda product: product['price'], rank_request['products']))
    ranked_products = list(map(lambda product: rank(
        product, rank_request['config'], max_price), rank_request['products']))
    logging.info(f"Calucalted ranks\n{ranked_products}")
    return json.dumps(ranked_products, cls=RankedProductEncoder)
