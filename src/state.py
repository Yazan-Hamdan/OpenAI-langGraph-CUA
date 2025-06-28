from typing import Any, Optional, TypedDict, List, Dict
from langchain_core.messages import AnyMessage
from playwright.async_api import Page

class CUAState(TypedDict):
    messages: List[AnyMessage]
    page: Page
    instruction: str
    previous_response_id: Optional[str]
    last_call_id: Optional[str]
    screenshot_base64: Optional[str]
    current_response: Any
    has_computer_call: bool
    final_output: Any
    has_tool_call: bool
    result_schema: Optional[Dict]