
from typing import Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class EndCallTool:
    def __init__(self, dynamic_variables: Dict[Any, Any], logger):
        self.logger = logger
        self.dynamic_variables = dynamic_variables

    def create_end_call_tool(self):
        @tool("end_call_tool", description="{{DESCRIPTION}}")
        def end_call_tool():
            try:
                self.logger.info(f"Tool executed:")
                return "{{RESPONSE}}"
            except Exception as e:
                self.logger.error(f"Tool error: {e}")
                return {"error": str(e), "status": "failed"}
        return end_call_tool

    def get_tools(self):
        return [self.create_end_call_tool()]
