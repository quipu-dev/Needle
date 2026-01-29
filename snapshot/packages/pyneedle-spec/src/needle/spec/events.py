from typing import TypedDict, Dict, Any, Protocol, runtime_checkable


class GenericEventIR(TypedDict):
    """
    The universal envelope for events in the PyNeedle ecosystem.
    
    This structure allows disparate systems (Cascade, Stitcher, Quipu) to share
    a common event bus without sharing implementation details.
    """
    v: str              # Protocol version (e.g. "1.0")
    ts: float           # Unix timestamp
    topic: str          # The routing key (e.g. "needle.core.started")
    tags: Dict[str, str]  # Lightweight metadata for routing/filtering
    payload: Dict[str, Any] # The actual event data


@runtime_checkable
class EventProtocol(Protocol):
    """
    Protocol that any Event object must satisfy to be transmissible via the bus.
    """
    @property
    def topic(self) -> str:
        """Return the routing topic for this event."""
        ...

    def to_ir(self) -> GenericEventIR:
        """Serialize the event to the generic intermediate representation."""
        ...