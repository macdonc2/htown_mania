from typing import List
from .models import Event

CYCLING = ["cycling","bike","biking","bicycle","mtb","ride","critical mass"]
OUTDOOR = ["outdoor","park","hike","trail","run","nature","bayou","memorial park"]

def prioritize_events(events: List[Event]) -> List[Event]:
    def score(e: Event) -> int:
        txt = f"{e.title} {e.description or ''}".lower()
        s = 0
        if any(k in txt for k in CYCLING): s += 2
        if any(k in txt for k in OUTDOOR): s += 1
        return s
    return sorted(events, key=score, reverse=True)
