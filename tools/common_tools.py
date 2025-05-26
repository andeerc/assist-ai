from crewai_tools import BaseTool
from datetime import datetime

class GetCurrentDateTimeTool(BaseTool):
    name: str = "Get Current Date and Time"
    description: str = "Returns the current date and time."

    def _run(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Example of how to make an instance of the tool directly usable
# current_datetime_tool = GetCurrentDateTimeTool()
