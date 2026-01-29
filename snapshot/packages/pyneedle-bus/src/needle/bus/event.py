from collections import defaultdict
from typing import Callable, List, Type, Dict, Any, Union
from needle.pointer import SemanticPointer

Handler = Callable[[Any], None]


class EventBus:
    """
    A high-performance, in-memory bus for system event distribution.
    Supports subscribing by event type, semantic pointer, or string topic.
    """

    def __init__(self):
        # Type-based subscriptions: {EventType: [handler1, handler2]}
        self._type_subscribers: Dict[Type, List[Handler]] = defaultdict(list)
        # Topic-based subscriptions: {"topic.string": [handler1, handler2]}
        self._topic_subscribers: Dict[str, List[Handler]] = defaultdict(list)
        # Wildcard subscribers that receive all events
        self._wildcard_subscribers: List[Handler] = []

    def subscribe(self, topic: Union[Type, str, SemanticPointer], handler: Handler) -> None:
        """Subscribes a handler to a specific event type or topic."""
        if isinstance(topic, type):
            self._type_subscribers[topic].append(handler)
        elif isinstance(topic, (str, SemanticPointer)):
            self._topic_subscribers[str(topic)].append(handler)
        else:
            # A special case for a global wildcard subscription
            self._wildcard_subscribers.append(handler)

    def publish(self, event: Any, topic: Union[str, SemanticPointer, None] = None) -> None:
        """Publishes an event object or a topic with data to all relevant subscribers."""
        # 1. Notify type-based subscribers
        event_type = type(event)
        if event_type in self._type_subscribers:
            for handler in self._type_subscribers[event_type]:
                handler(event)

        # 2. Determine topic and notify topic-based subscribers
        final_topic = topic or getattr(event, "topic", None)
        if final_topic:
            topic_str = str(final_topic)
            if topic_str in self._topic_subscribers:
                for handler in self._topic_subscribers[topic_str]:
                    # For topic-based events, the event object itself is passed
                    handler(event)
        
        # TODO: Implement glob/wildcard matching for topics.

        # 3. Notify global wildcard subscribers
        for handler in self._wildcard_subscribers:
            handler(event)