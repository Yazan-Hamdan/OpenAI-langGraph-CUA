import logging
import json
from typing import Any, Dict
from collections import OrderedDict

from playwright.async_api import Page
from langchain_core.tools import tool
import jsonschema

from models import BrowserAction
from config import Config


config = Config()
# Configure logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

async def handle_model_action(page: Page, action: Dict[str, Any]):
    action_type = action["type"]
    
    if action_type == "navigate":
        url = action.get("url")
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        logger.info(f"Navigated to {url}")
    
    elif action_type in ["click", "double_click"]:
        x, y = action["x"], action["y"]
        button = action.get("button", "left")
        print(f"Action: {action_type} at ({x}, {y}) with button '{button}'")

        if button not in ["left", "right"]:
            button = "left"

        click_count = 2 if action_type == "double_click" else 1
        await page.mouse.click(x, y, button=button, click_count=click_count)

    elif action_type == "type":
        text = action["text"]
        print(f"Action: type text: {text}")
        await page.keyboard.type(text)
    
    elif action_type == "keypress":
        keys = action["keys"]
        for k in keys:
            print(f"Action: keypress '{k}'")
            if k.lower() == "enter":
                await page.keyboard.press("Enter")
            elif k.lower() == "space":
                await page.keyboard.press(" ")
            else:
                await page.keyboard.press(k)
    
    elif action_type == "scroll":
        x, y = action["x"], action["y"]
        scroll_x, scroll_y = action["scroll_x"], action["scroll_y"]
        print(f"Action: scroll at ({x}, {y}) with offsets (scroll_x={scroll_x}, scroll_y={scroll_y})")
        await page.mouse.move(x, y)
        await page.evaluate(f"window.scrollBy({scroll_x}, {scroll_y})")
    
    elif action_type == "wait":
        wait_time = 1  # Default wait time
        await page.wait_for_timeout(wait_time * 1000)
        logger.info(f"Waited for {wait_time} seconds")

    elif action_type == "get_current_url":
        return page.url()
    
    elif action_type == 'get_environment':
        return 'browser'
    
    elif action_type in ["screenshot", "drag", "get_dimensions"]:
        print(f"Action: {action_type}")

    else:
        logger.error(f"Unsupported action type: {action_type}")

async def execute_browser_action(page: Page, action: BrowserAction):
    action_type = action["type"]
    
    if action_type == "openurl":
        url = action["url"]
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        logger.info(f"Navigated to {url}")
        
        # Inject element IDs if requested
        if action.get("inject_element_ids", False):
            await inject_element_ids(page)
    
    elif action_type == "click":
        xpath = action["xpath"]
        element = await page.locator(f"xpath={xpath}").first
        await element.click()
        logger.info(f"Clicked element with xpath: {xpath}")
    
    elif action_type == "entertext":
        xpath = action["xpath"]
        text = action["text"]
        element = await page.locator(f"xpath={xpath}").first
        await element.fill(text)
        logger.info(f"Entered text '{text}' in element with xpath: {xpath}")
    
    elif action_type == "enter_text_and_click":
        text_xpath = action["text_xpath"]
        click_xpath = action["click_xpath"]
        text = action["text"]
        
        # Enter text
        text_element = await page.locator(f"xpath={text_xpath}").first
        await text_element.fill(text)
        
        # Click
        click_element = await page.locator(f"xpath={click_xpath}").first
        await click_element.click()
        
        logger.info(f"Entered text '{text}' and clicked")
    
    elif action_type == "press_key_combination":
        key_combination = action["key_combination"]
        await page.keyboard.press(key_combination)
        logger.info(f"Pressed key combination: {key_combination}")
    
    elif action_type == "dismiss_dialog":
        selector = action["selector"]
        try:
            element = await page.locator(selector).first
            await element.click()
            logger.info(f"Dismissed dialog with selector: {selector}")
        except Exception as e:
            logger.warning(f"Could not dismiss dialog: {e}")
    
    elif action_type == "inject_element_ids":
        await inject_element_ids(page)
    
    elif action_type == "load_mhtml":
        logger.warning("load_mhtml action not implemented")
    
    else:
        logger.error(f"Unsupported browser action type: {action_type}")

async def inject_element_ids(page: Page):
    """Inject unique IDs into interactive elements for easier targeting"""
    await page.evaluate('''
        () => {
            let counter = 0;
            const elements = document.querySelectorAll('button, a, input, select, textarea, [onclick], [role="button"]');
            elements.forEach(el => {
                if (!el.id) {
                    el.id = `injected-id-${counter++}`;
                }
            });
        }
    ''')
    logger.info("Injected element IDs")


def structured_output_tool_factory(schema: Dict[str, Any]):
    @tool(args_schema=schema)
    def submit_result(input_json: Dict[str, Any]) -> str:
        """
        Submit the final result in JSON format.
        """
        try:
            if not isinstance(input_json, dict):
                input_json = json.loads(input_json)
            
            jsonschema.validate(instance=input_json, schema=schema)
            print("Valid submission received:", input_json)
            return input_json
        except jsonschema.exceptions.ValidationError as e:
            return f"Schema validation error: {e.message}"
    return submit_result

def reorder_properties(schema):
    """
    Reorders properties so that if a 'type' with 'const' exists, it comes first.
    """
    props = schema.get("properties", {})
    if "type" in props and isinstance(props["type"], dict) and "const" in props["type"]:
        # Move 'type' to the beginning
        reordered = OrderedDict()
        reordered["type"] = props["type"]
        for key, value in props.items():
            if key != "type":
                reordered[key] = value
        schema["properties"] = reordered
    return schema

def transform_schema(schema):
    if "$defs" in schema:
        for def_name, def_schema in schema["$defs"].items():
            reorder_properties(def_schema)

    if "properties" in schema:
        for key, prop in schema["properties"].items():
            if isinstance(prop, dict) and "properties" in prop:
                reorder_properties(prop)
    
    return schema