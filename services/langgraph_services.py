from ..my_agents.agents import workflow
from ..my_agents.utils.state import State


def run_workflow(user_input: str) -> State:
    """
    Run the article writing and improvement workflow.
    
    Args:
        user_input: The user's query/topic for article generation
        
    Returns:
        State: The final state containing the best article and metadata
    """
    state: State = {
        "user_query": user_input,
        "article": "",
        "grade": 0,
        "best_score": 0,
        "best_article": "",
        "justification": "",
        "iterations": 0,
        "suggested_edits": "",
        "messages": [],
        "essay": [],
    }
    
    result_state = workflow.invoke(state)
    return result_state


# For testing: python -m backend.services.langgraph_services
if __name__ == "__main__":
    result = run_workflow("Write a comprehensive article on the benefits of renewable energy.")
    print("=" * 80)
    print("FINAL BEST ARTICLE:")
    print("=" * 80)
    print(result["best_article"])
    print("=" * 80)
    print(f"Best Score: {result['best_score']}")
    print(f"Iterations: {result['iterations']}")