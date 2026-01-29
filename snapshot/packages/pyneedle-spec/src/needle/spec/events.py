from typing import TypedDict, Dict, Any, Optional

class GenericEventIR(TypedDict):
    """
    The universal envelope for events in the PyNeedle ecosystem.
    
    This structure is designed to be:
    1. Serializable (JSON-safe)
    2. Minimalist (Only essential headers)
    3. Extensible (Via tags and payload)
    """
    v: str              # Protocol version (e.g. "1.0")
    ts: float           # Unix timestamp
    topic: str          # The routing key (often stringified SemanticPointer)
    
    # Metadata for routing, filtering, and tracing.
    # e.g. {"env": "prod", "source": "worker-1", "level": "error"}
    tags: Dict[str, str] 
    
    # The actual business data.
    # For Cascade, this contains 'ctx' and 'phy' data.
    payload: Dict[str, Any]