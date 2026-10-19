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


№task7
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
