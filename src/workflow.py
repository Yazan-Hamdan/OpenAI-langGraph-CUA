from langgraph.graph import StateGraph
from nodes import send_request, process_response, execute_action, finalize
from state import CUAState

def setup_workflow():
    graph = StateGraph(CUAState)
    graph.add_node("send_request", send_request)
    graph.add_node("execute_action", execute_action)
    graph.add_node("finalize", finalize)

    graph.set_entry_point("send_request")
    graph.add_conditional_edges(
        "send_request",
        process_response,
        {
            "execute_action_command": "execute_action",
            "finalize_command": "finalize",
            "default": "send_request"
        }
    )
    graph.add_edge("execute_action", "send_request")
    graph.set_finish_point("finalize")

    return graph.compile()