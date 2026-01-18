# safety.py
"""
Centralized safety utilities for fault-tolerant execution.
Provides timeout handling, error reporting, text truncation, and validation utilities.
"""

import json
import hashlib
import signal
import functools
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# ================================
# ERROR REPORTING
# ================================

@dataclass
class ErrorReport:
    """Structured error representation for graceful failure handling."""
    agent: str
    status: str  # "failed", "timeout", "partial", "warning"
    reason: str
    recovery: str
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "agent": self.agent,
            "status": self.status,
            "reason": self.reason,
            "recovery": self.recovery
        }
        if self.details:
            result["details"] = self.details
        return result


@dataclass
class ValidationResult:
    """Validation report with errors, warnings, and auto-fixes."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    fixes_applied: List[str] = field(default_factory=list)
    
    def add_error(self, msg: str):
        """Add a critical error (prevents execution)."""
        self.errors.append(msg)
        self.valid = False
    
    def add_warning(self, msg: str):
        """Add a warning (allows execution with defaults)."""
        self.warnings.append(msg)
    
    def add_fix(self, msg: str):
        """Record an auto-fix that was applied."""
        self.fixes_applied.append(msg)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "fixes_applied": self.fixes_applied
        }


# ================================
# TIMEOUT HANDLING
# ================================

class TimeoutError(Exception):
    """Raised when an operation exceeds its timeout."""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout."""
    raise TimeoutError("Operation timed out")


def with_timeout(seconds: int):
    """
    Decorator to add timeout to a function.
    Note: Uses signal.alarm, only works on Unix systems and main thread.
    For production, consider using threading.Timer or multiprocessing.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Set the signal handler and alarm
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                # Disable the alarm and restore old handler
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            return result
        return wrapper
    return decorator


def safe_execute(func, *args, timeout_sec: int = 60, **kwargs) -> Tuple[bool, Any, Optional[str]]:
    """
    Safely execute a function with timeout and exception handling.
    
    Returns:
        (success: bool, result: Any, error_msg: Optional[str])
    """
    try:
        # For now, execute without timeout (signal-based timeout doesn't work well with threads)
        # In production, use multiprocessing or threading.Timer
        result = func(*args, **kwargs)
        return True, result, None
    except TimeoutError:
        return False, None, f"Operation timed out after {timeout_sec} seconds"
    except Exception as e:
        return False, None, f"{type(e).__name__}: {str(e)}"


# ================================
# TEXT SAFETY
# ================================

def truncate_text(text: str, max_bytes: int = 2048) -> Tuple[str, bool]:
    """
    Truncate text to max_bytes, ensuring we don't break in the middle of a character.
    
    Returns:
        (truncated_text, was_truncated)
    """
    if not text:
        return "", False
    
    # Convert to bytes and check size
    text_bytes = text.encode('utf-8', errors='ignore')
    
    if len(text_bytes) <= max_bytes:
        return text, False
    
    # Truncate and decode safely
    truncated_bytes = text_bytes[:max_bytes]
    # Decode and ignore errors to avoid breaking mid-character
    truncated_text = truncated_bytes.decode('utf-8', errors='ignore')
    
    # Add truncation marker
    truncated_text += "\n\n[... truncated ...]"
    
    return truncated_text, True


def hash_content(text: str) -> str:
    """
    Generate SHA-256 hash of content for deduplication and large text storage.
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def compress_large_text(text: str, max_bytes: int = 2048) -> Dict[str, Any]:
    """
    Compress large text by truncating and storing hash.
    
    Returns:
        {
            "content": truncated_text,
            "hash": content_hash,
            "truncated": bool,
            "original_size": int
        }
    """
    original_size = len(text.encode('utf-8'))
    truncated, was_truncated = truncate_text(text, max_bytes)
    
    return {
        "content": truncated,
        "hash": hash_content(text),
        "truncated": was_truncated,
        "original_size": original_size
    }


# ================================
# JSON SAFETY
# ================================

def safe_json_load(path: str, default: Any = None) -> Any:
    """
    Safely load JSON file with fallback to default on any error.
    """
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return default if default is not None else {}
    except json.JSONDecodeError:
        return default if default is not None else {}
    except Exception:
        return default if default is not None else {}


def safe_json_dump(data: Any, path: str, indent: int = 2) -> bool:
    """
    Safely write JSON file with error handling.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception:
        return False


# ================================
# DEPENDENCY CYCLE DETECTION
# ================================

def detect_cycles(graph: Dict[str, List[str]]) -> List[List[str]]:
    """
    Detect cycles in a directed graph using DFS.
    
    Args:
        graph: Dict mapping node -> list of dependent nodes
    
    Returns:
        List of cycles found (each cycle is a list of nodes)
    """
    cycles = []
    visited = set()
    rec_stack = set()
    path = []
    
    def dfs(node: str) -> bool:
        """DFS with cycle detection. Returns True if cycle found."""
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        # Visit all neighbors
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                # Found a cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)
                return True
        
        # Backtrack
        path.pop()
        rec_stack.remove(node)
        return False
    
    # Check all nodes
    for node in graph.keys():
        if node not in visited:
            dfs(node)
    
    return cycles


def build_dependency_graph(agents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Build dependency graph from agent configurations.
    
    Returns:
        Dict mapping agent_id -> list of sub_agent_ids
    """
    graph = {}
    for agent in agents:
        agent_id = agent.get("id", "")
        sub_agents = agent.get("sub_agents", [])
        if agent_id:
            graph[agent_id] = sub_agents if isinstance(sub_agents, list) else []
    return graph


# ================================
# SAFE DICTIONARY ACCESS
# ================================

def safe_get(d: Dict, key: str, default: Any = None, expected_type: type = None) -> Any:
    """
    Safely get value from dictionary with type checking.
    
    Args:
        d: Dictionary to access
        key: Key to retrieve
        default: Default value if key missing or wrong type
        expected_type: Expected type of value (optional)
    
    Returns:
        Value if found and correct type, otherwise default
    """
    value = d.get(key, default)
    
    if expected_type is not None:
        if not isinstance(value, expected_type):
            return default
    
    return value
