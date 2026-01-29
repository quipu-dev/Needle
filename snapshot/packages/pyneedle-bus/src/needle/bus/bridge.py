from typing import Any, Type, Union
from needle.spec import SemanticPointerProtocol

from .event import EventBus
from .feedback import FeedbackBus


class LogBridge:
    """
    The Synapse connecting the EventBus (Nervous System) to the FeedbackBus (Expression System).
    
    It listens for events and automatically renders them as user feedback 
    if a corresponding message template exists.
    """

    def __init__(self, event_bus: EventBus, feedback_bus: FeedbackBus):
        self.event_bus = event_bus
        self.feedback_bus = feedback_bus

    def connect(
        self, 
        event_type: Union[Type[Any], str, SemanticPointerProtocol], 
        ptr: SemanticPointerProtocol, 
        level: str = "info"
    ):
        """
        Establish a connection: When `event_type` occurs, render `ptr` template.
        
        Args:
            event_type: The event to listen for (Class or Topic/Pointer).
            ptr: The Semantic Pointer pointing to the I18n message key.
            level: The log level to use.
        """
        def handler(event: Any):
            # Extract data from event. 
            # We support both object attributes (via __dict__) and dictionary access.
            if isinstance(event, dict):
                data = event
            elif hasattr(event, "__dict__"):
                data = event.__dict__
            else:
                data = {}
            
            self.feedback_bus.info(ptr, **data) if level == "info" else \
            self.feedback_bus.success(ptr, **data) if level == "success" else \
            self.feedback_bus.warning(ptr, **data) if level == "warning" else \
            self.feedback_bus.error(ptr, **data) if level == "error" else \
            self.feedback_bus.debug(ptr, **data)

        self.event_bus.subscribe(event_type, handler)