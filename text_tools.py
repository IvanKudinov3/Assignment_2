"""Regex sanitization, stable-sequence, and incident-index functions."""
import re


#task6
def sanitize_report(text):#changes seal, container, email and gives back sanitized version of it
    email_pattern = r'(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}'
    seal_pattern = r'(?i)\bSEAL-\d{6}\b'
    container_pattern = r'(?i)\b[a-z]{4}\d{7}\b'

    sanitized = text
    sanitized = re.sub(email_pattern, "[EMAIL]", sanitized)
    sanitized = re.sub(seal_pattern, "[SEAL]", sanitized)
    sanitized = re.sub(container_pattern, "[CONTAINER]", sanitized)

    is_changed = (sanitized != text)
    return sanitized, is_changed


#task7
def longest_unique_sequence(events):#gives the longest sequence without repetiotion and its length
    last_seen = {}   
    start = 0    
    best_length = 0
    best_start = 0

    for position, event in enumerate(events):
        if event in last_seen and last_seen[event] >= start:
            start = last_seen[event] + 1
        last_seen[event] = position

        length = position - start + 1
        if length > best_length:  
            best_length = length
            best_start = start

    return best_length, events[best_start:best_start + best_length]

# Task 9: Make text easier to search.
def normalize_words(text):
    """Convert text to lowercase words and remove punctuation."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return text.split()


# Build an index connecting each word to incident IDs.
def build_incident_index(incidents):
    word_to_ids = {}
    titles = {}

    for incident in sorted(incidents, key=lambda item: str(item["incident_id"])):
        incident_id = str(incident["incident_id"])
        titles[incident_id] = str(incident["title"])

        # Sets stop the same word adding an ID more than once.
        for word in set(normalize_words(incident["report"])):
            word_to_ids.setdefault(word, set()).add(incident_id)

    sorted_index = {
        word: sorted(ids)
        for word, ids in sorted(word_to_ids.items())
    }

    return {
        "index": sorted_index,
        "titles": dict(sorted(titles.items()))
    }


# Find incidents matching the user's search words.
def search_incident_index(index_data, query):
    index = index_data["index"]
    titles = index_data["titles"]
    scores = {}

    # A repeated query word should only count once.
    for word in set(normalize_words(query)):
        for incident_id in index.get(word, []):
            scores[incident_id] = scores.get(incident_id, 0) + 1

    # Highest score first; incident ID breaks ties.
    ranked_ids = sorted(
        scores,
        key=lambda incident_id: (-scores[incident_id], incident_id)
    )

    return [
        (incident_id, scores[incident_id], titles[incident_id])
        for incident_id in ranked_ids
        if incident_id in titles
    ]
