import asyncio
import json
from typing import Any, Dict

from playwright.async_api import async_playwright, BrowserContext, Page

from config import Config
from workflow import setup_workflow
from models import BrowserList
from utils import execute_browser_action, transform_schema
from langsmith import Client

config = Config()

async def execute_action_or_query(
    page: Page, 
    browser_actions: BrowserList, 
    task: str, 
    result_schema: Dict[str, Any], 
    context: BrowserContext = None
) -> Dict[str, Any]:
    """
    Execute browser actions and then use AI to complete a task with structured output using a submit tool.
    
    Args:
        page: Playwright Page object
        browser_actions: List of browser actions to execute
        task: The task description for the AI to complete
        result_schema: JSON schema for the expected result format
        context: Optional browser context (not used in current implementation)
    
    Returns:
        Structured result matching the provided schema
    """

    for action in browser_actions:
        await execute_browser_action(page, action)
        await asyncio.sleep(1)  # Brief pause between actions

    
    initial_state = {
        "messages": [],
        "page": page,
        "instruction": task,
        "previous_response_id": None,
        "last_call_id": None,
        "screenshot_base64": None,
        "current_response": None,
        "has_computer_call": False,
        "final_output": "",
        "has_tool_call": False,
        "result_schema": result_schema
    }
    
    app = setup_workflow()
    final_state = await app.ainvoke(initial_state, {"recursion_limit": config.RECURSION_LIMIT})
    
    return final_state['final_output']

async def main():
    langsmith_client = Client()
    async def run_example(example: dict):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(viewport={"width": config.BROWSER_WIDTH, "height": config.BROWSER_HEIGHT})
            page = await context.new_page()
            
            test_actions = example['actions']
            
            test_schema = transform_schema(example['result_json_schema'])

            
            test_task = example['task']
            
            print("Testing structured execution with submit tool...")
            print(f"Task: {test_task}")
            print(f"Actions: {test_actions}")
            
            result = await execute_action_or_query(
                page=page,
                browser_actions=test_actions,
                task=test_task,
                result_schema=test_schema,
                context=context
            )
            
            print(f"\nStructured Result:")
            print(json.dumps(result, indent=2))
            
            await context.close()

            return result
    
    await langsmith_client.aevaluate(
            run_example,  # Wrapped function that handles conversion
            data=config.EXPERIMENT_NAME,
            max_concurrency=1,
        )


if __name__ == "__main__":
    asyncio.run(main())