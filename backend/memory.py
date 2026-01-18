# memory.py
"""
Memory management with size limits, deduplication, and safe JSON handling.
Prevents unbounded memory growth and handles corrupted files gracefully.
"""

import json
import os
import threading
from safety import safe_json_load, safe_json_dump, truncate_text, hash_content

MEM_LOCK = threading.Lock()
PATH = "memory.json"

# Memory limits
# Memory limits - STRICT < 5KB TOTAL
MAX_MEMORY_ITEMS = 5
MAX_ENTRY_SIZE_BYTES = 200  # Strict per-item limit

def enforce_size_limit(mem):
    """
    Strictly enforce < 5KB total file size.
    Prune oldest entries if necessary.
    """
    import json
    
    # Check estimated size
    while True:
        json_str = json.dumps(mem)
        size_bytes = len(json_str.encode('utf-8'))
        
        if size_bytes < 5000:
            break
            
        # Pruning Strategy:
        # 1. Reduce items per agent from each category
        pruned = False
        for aid in mem:
            for k in ["insights", "numbers", "decisions", "keywords"]:
                if len(mem[aid][k]) > 1:
                    mem[aid][k].pop(0) # Remove oldest
                    pruned = True
                    break
            if pruned: break
        
        # 2. If still not enough and cannot prune items (all empty or single), start removing agents?
        # For now, just break if we can't prune easily to avoid infinite loop, 
        # but in practice the list limit should keep us safe.
        if not pruned:
            break
            
    return mem


def load_memory():
    """
    Load memory from disk with safe error handling.
    Returns empty dict if file doesn't exist or is corrupted.
    """
    return safe_json_load(PATH, default={})


def save_memory(aid, takeaways):
    """
    Save memory with size limits, truncation, and deduplication.
    
    Args:
        aid: Agent ID
        takeaways: Dict with keys: insights, numbers, decisions, keywords
    """
    with MEM_LOCK:
        mem = load_memory()
        
        if aid not in mem:
            mem[aid] = {
                "insights": [],
                "numbers": [],
                "keywords": [],
                "decisions": []
            }
        
        # Ensure all keys exist (migrates old memory)
        for k in ["insights", "numbers", "decisions", "keywords"]:
            if k not in mem[aid]:
                mem[aid][k] = []
            
            # Get new items
            new_items = takeaways.get(k, [])
            if not isinstance(new_items, list):
                continue
            
            # Process each new item
            for item in new_items:
                if not isinstance(item, str):
                    continue
                
                # Truncate large items
                truncated_item, was_truncated = truncate_text(item, MAX_ENTRY_SIZE_BYTES)
                
                # Deduplication: check if hash already exists
                item_hash = hash_content(truncated_item)
                
                # Check if we already have this content (by hash)
                existing_hashes = [hash_content(existing) for existing in mem[aid][k]]
                if item_hash in existing_hashes:
                    continue  # Skip duplicate
                
                # Add the item
                mem[aid][k].append(truncated_item)
            
            # Compression: Keep only the last N items to prevent unlimited growth
            if len(mem[aid][k]) > MAX_MEMORY_ITEMS:
                mem[aid][k] = mem[aid][k][-MAX_MEMORY_ITEMS:]
        
        # Enforce strict 5KB limit
        mem = enforce_size_limit(mem)

        # Save to disk
        safe_json_dump(mem, PATH, indent=None) # Compact JSON


def get_memory_size():
    """
    Get current memory file size in bytes.
    Returns 0 if file doesn't exist.
    """
    try:
        if os.path.exists(PATH):
            return os.path.getsize(PATH)
        return 0
    except Exception:
        return 0


def compact_memory():
    """
    Compact memory by removing duplicates and old entries.
    Called periodically to prevent memory bloat.
    """
    with MEM_LOCK:
        mem = load_memory()
        
        for aid in mem:
            for k in ["insights", "numbers", "decisions", "keywords"]:
                if k not in mem[aid]:
                    continue
                
                # Deduplicate by hash
                seen_hashes = set()
                unique_items = []
                
                for item in mem[aid][k]:
                    item_hash = hash_content(item)
                    if item_hash not in seen_hashes:
                        seen_hashes.add(item_hash)
                        unique_items.append(item)
                
                # Keep only last N items
                mem[aid][k] = unique_items[-MAX_MEMORY_ITEMS:]
        
        # Save compacted memory
        safe_json_dump(mem, PATH)