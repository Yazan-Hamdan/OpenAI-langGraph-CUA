import base64

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

from state import CUAState
from utils import handle_model_action, structured_output_tool_factory
from config import Config

config = Config()
client=ChatOpenAI(model="computer-use-preview", model_kwargs={"truncation": "auto"}, use_responses_api=True)


@tool
def submit(response: str) -> None:
    """
        use it to submit the result of your work when done.

        args:
            response (str): The response to be submitted.
    """
    raise NotImplementedError("This tool is not implemented yet. Please use the 'finalize' command to submit your work.")

async def send_request(state: CUAState) -> CUAState:
    if not state['messages']: 
        state['messages'] = [HumanMessage(state["instruction"])]

    tools = [{
        "type": "computer_use_preview",
        "display_width": config.BROWSER_WIDTH,
        "display_height": config.BROWSER_HEIGHT,
        "environment": "browser"
    }]

    if state.get("result_schema"):
        structured_output_tool = structured_output_tool_factory(state["result_schema"])
        tools.append(structured_output_tool)
    else:
        tools.append(submit)

    model_with_tools = client.bind_tools(tools)

    if state["previous_response_id"] is None:
        response = await model_with_tools.ainvoke(state['messages'])
    else:
        response = await model_with_tools.ainvoke([state['messages'][-1]], previous_response_id=state["previous_response_id"])
    
    state['messages'].append(response)
    state["current_response"] = response
    state["previous_response_id"] = response.response_metadata['id']
    return state

def process_response(state: CUAState) -> str:
    if not state['current_response'].additional_kwargs:
        return 'execute_action_command'

    computer_calls = [item for item in state["current_response"].additional_kwargs.get('tool_outputs', []) if item["type"] == "computer_call"]
    tool_calls = state["current_response"].tool_calls

    if tool_calls or computer_calls:
        submit_call = [item for item in tool_calls if item.get('name') == "submit" or item.get('name') == "submit_result"]
        if submit_call:
            return 'finalize_command'

        return 'execute_action_command'

    return 'default'

async def execute_action(state: CUAState) -> CUAState:
    computer_call = None

    if state['current_response'].additional_kwargs:
        computer_call = [item for item in state["current_response"].additional_kwargs['tool_outputs'] if item["type"] == "computer_call"][0]

    if computer_call:
        state["has_computer_call"] = True
        state["last_call_id"] = computer_call["call_id"]

        action = computer_call["action"]
        page = state["page"]
        
        await handle_model_action(page, action)
        
        screenshot_bytes = await page.screenshot()
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
        state["screenshot_base64"] = screenshot_base64

        tool_message = ToolMessage(tool_call_id=computer_call["call_id"], content=[{"type": "input_image", "image_url": f"data:image/png;base64,{screenshot_base64}"}])

        tool_message.additional_kwargs = {"type": "computer_call_output"}
        
        state["messages"].append(tool_message)
    
    else:
        state['messages'].append(HumanMessage(content="use submit tool to submit result or keep working on the task"))
        state["has_computer_call"] = False

    return state

def finalize(state: CUAState) -> CUAState:
    tool_calls = state["current_response"].tool_calls
    target_name = "submit_result" if state.get("result_schema") else "submit"

    submit_call = next((item for item in tool_calls if item.get("name") == target_name), None)

    if submit_call:
        if target_name == "submit_result":
            state["final_output"] = submit_call.get("args", {})
        else:
            state["final_output"] = submit_call.get("args", {}).get("response", "")

    return state