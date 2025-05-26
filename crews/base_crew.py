from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseCrew(ABC):
    """
    Abstract base class for all specialized crews.

    This class defines the common interface that all crew implementations
    must adhere to. It serves as a contract for how crews are structured,
    ensuring that the `CrewManager` can discover, instantiate, and run them
    dynamically.

    Subclasses must implement the `kickoff` method and provide a `description`
    class attribute. The `description` is used by `CrewManager` to list
    available crews and by `ChatManager`'s LLM to decide which crew to delegate to.

    Attributes:
        user_input (Optional[str]): The input query or task from the user,
                                    which the crew will process. This is passed
                                    during instantiation by the `CrewManager`.
        description (str): A brief description of what the crew does.
                           This MUST be overridden by subclasses.
    """
    description: str = "No description available. Subclasses must override this."

    def __init__(self, user_input: Optional[str] = None):
        """
        Initializes the BaseCrew.

        Args:
            user_input (Optional[str]): The input query or task from the user.
        """
        self.user_input = user_input

    @abstractmethod
    def kickoff(self) -> Dict[str, Any]:
        """
        Starts the execution of the crew's defined tasks.

        This method should contain the primary logic for the crew, including
        agent and task setup (typically in a helper method like `_setup_agents_and_tasks`),
        and running the `crewai.Crew.kickoff()` method.

        Returns:
            Dict[str, Any]: A dictionary containing the results of the
                            crew's execution. The structure of this dictionary
                            should be consistent for `CrewManager` to process.
                            It is expected to include a "result" key with the
                            crew's primary output, but can include other keys
                            like "status" or "error_message" if needed.
        """
        pass
