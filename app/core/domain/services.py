from typing import List
from .models import Event

# Keyword lists for prioritization and categorization
CYCLING = ["cycling","bike","biking","bicycle","mtb","ride","critical mass"]
OUTDOOR = ["outdoor","park","hike","trail","run","nature","bayou","memorial park","kayak","paddle"]
MUSIC = ["music","concert","band","live music","dj","show","performance","venue"]
DOG_FRIENDLY = ["dog","dog-friendly","pet","pet-friendly","pup","canine","bark","dogs welcome"]
COUPLE_ACTIVITIES = ["wine","brewery","beer","cocktail","tasting","comedy","trivia","art walk","gallery","date night","romantic"]
KID_FOCUSED = ["kids","children","family fun","toddler","playground","bounce house","story time","baby"]

def prioritize_events(events: List[Event]) -> List[Event]:
    """
    Prioritize events for a mid-life childless couple who loves:
    1. Cycling (HIGHEST priority - OH YEAH!)
    2. Couple-friendly fun (breweries, comedy, art, etc.) - THE CREAM RISES!
    3. Music/concerts
    4. Dog-friendly activities
    5. Outdoor activities
    6. De-prioritize kid-focused events
    """
    def score(e: Event) -> int:
        txt = f"{e.title} {e.description or ''}".lower()
        s = 0
        
        # Cycling is KING! OH YEAH!
        if any(k in txt for k in CYCLING):
            s += 10
        
        # Couple-friendly activities - SECOND HIGHEST! DIG IT!
        if any(k in txt for k in COUPLE_ACTIVITIES):
            s += 9
        
        # Music and concerts - high priority
        if any(k in txt for k in MUSIC):
            s += 8
        
        # Dog-friendly gets a boost!
        if any(k in txt for k in DOG_FRIENDLY):
            s += 7
        
        # Outdoor activities
        if any(k in txt for k in OUTDOOR):
            s += 5
        
        # Penalize kid-focused events
        if any(k in txt for k in KID_FOCUSED):
            s -= 5
        
        return s
    
    return sorted(events, key=score, reverse=True)
