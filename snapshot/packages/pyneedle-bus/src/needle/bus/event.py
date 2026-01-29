import asyncio
from collections import defaultdict
from typing import Any, Callable, Dict, List, Type, Union

from needle.spec import EventProtocol, SemanticPointerProtocol

# Handler type alias
Handler = Callable[[Any], None]


class EventBus:
    """
    The Nervous System of PyNeedle.
    
    A high-performance, in-memory event bus supporting both 
    Type-based subscription (for logic) and Topic-based subscription (for routing).
    """

    def __init__(self):
        # Type-based subscribers: EventClass -> [handlers]
        self._type_subscribers: Dict[Type[Any], List[Handler]] = defaultdict(list)
        
        # Topic-based subscribers: "topic.string" -> [handlers]
        self._topic_subscribers: Dict[str, List[Handler]] = defaultdict(list)
        
        # Wildcard topic subscribers: "topic.*" -> [handlers]
        # Currently we support simple prefix matching logic or just global wildcard.
        # For simplicity in V1, we handle "*" specially.
        self._wildcard_subscribers: List[Handler] = []

    def subscribe(
        self, 
        target: Union[str, SemanticPointerProtocol, Type[Any]], 
        handler: Handler
    ):
        """
        Subscribe a handler to an event type or topic.
        
        Args:
            target: Can be a Python class (Type), a string topic, or a SemanticPointer.
            handler: The function to call when the event occurs.
        """
        if isinstance(target, str):
            if target == "*":
                self._wildcard_subscribers.append(handler)
            else:
                self._topic_subscribers[target].append(handler)
        elif hasattr(target, "__str__") and not isinstance(target, type):
            # SemanticPointer or similar object
            self._topic_subscribers[str(target)].append(handler)
        else:
            # Assume it's a type (Class)
            self._type_subscribers[target].append(handler)

    def publish(self, event: Any):
        """
        Publish an event to all interested subscribers.
        
        Dispatch Logic:
        1. Exact Type match
        2. Exact Topic match (if event has .topic)
        3. Wildcards
        """
        # 1. Dispatch by Type
        event_type = type(event)
        if event_type in self._type_subscribers:
            for handler in self._type_subscribers[event_type]:
                self._safe_call(handler, event)

        # 2. Dispatch by Topic
        topic = getattr(event, "topic", None)
        # If it's a SemanticPointer, convert to string
        if hasattr(topic, "__str__"):
            topic = str(topic)
            
        if topic and isinstance(topic, str):
            if topic in self._topic_subscribers:
                for handler in self._topic_subscribers[topic]:
                    self._safe_call(handler, event)

        # 3. Wildcards
        for handler in self._wildcard_subscribers:
            self._safe_call(handler, event)

    def _safe_call(self, handler: Handler, event: Any):
        """Execute handler, suppressing exceptions to prevent bus crash."""
        try:
            handler(event)
        except Exception as e:
            # In a real scenario, we might want to log this via a fallback mechanism
            # or emit a SystemError event (careful of infinite loops).
            # For now, we print to stderr as a last resort.
            import sys
            print(f"[EventBus] Error in handler {handler}: {e}", file=sys.stderr)