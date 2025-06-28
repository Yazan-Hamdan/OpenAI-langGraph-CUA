import asyncio
from playwright.async_api import async_playwright, BrowserContext, Page
from workflow import setup_workflow
from config import Config

config = Config()

async def execute_action_or_query(page: Page, context: BrowserContext, instruction: str) -> str:
    initial_state = {
        "messages": [],
        "page": page,
        "instruction": instruction,
        "previous_response_id": None,
        "last_call_id": None,
        "screenshot_base64": None,
        "current_response": None,
        "has_computer_call": False,
        "final_output": "",
        "has_tool_call": False
    }
    
    app = setup_workflow()
    final_state = await app.ainvoke(initial_state, {"recursion_limit": config.RECURSION_LIMIT})
    return final_state["final_output"]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"height": config.BROWSER_HEIGHT, "width": config.BROWSER_WIDTH})
        page = await context.new_page()
        await page.goto("https://www.bing.com")
        
        test_instructions = [
            "Find out the population of Paris"
        ]
        
        for instruction in test_instructions:
            print(f"\n{'='*50}")
            print(f"Executing: {instruction}")
            print(f"{'='*50}")
            result = await execute_action_or_query(page, context, instruction)
            print(f"Result: {result}")
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())