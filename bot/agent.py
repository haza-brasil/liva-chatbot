import logging
from typing import Callable, Optional, Text

from rasa_core.agent import Agent

from processor import CustomMessageProcessor

logger = logging.getLogger(__name__)


class CustomAgent(Agent):
    def __init__(self,
                 domain,
                 policies,
                 interpreter,
                 generator,
                 tracker_store,
                 action_endpoint):

        super(CustomAgent, self).__init__(domain,
                                          policies,
                                          interpreter,
                                          generator,
                                          tracker_store,
                                          action_endpoint)

    def create_processor(self,
                         preprocessor: Optional[Callable[[Text], Text]] = None
                         ) -> CustomMessageProcessor:
        """Instantiates a processor based on the set state of the agent."""
        # Checks that the interpreter and tracker store are set and
        # creates a processor
        self._ensure_agent_is_ready()

        return CustomMessageProcessor(
            self.interpreter,
            self.policy_ensemble,
            self.domain,
            self.tracker_store,
            self.nlg,
            action_endpoint=self.action_endpoint,
            message_preprocessor=preprocessor)
