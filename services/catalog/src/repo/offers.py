from services.catalog.src.domain.offer import Offer

def get_all_offers() -> list[Offer]:
    return [
        Offer(id=1, title="Сэндвич + кофе", price=299),
        Offer(id=2, title="Паста дня", price=349),
    ]
