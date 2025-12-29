from langchain.messages import HumanMessage, AIMessage, SystemMessage
from .state import State
from .prompts import *
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from dotenv import load_dotenv
import os
from langgraph.graph import add_messages

load_dotenv()


def get_llm_with_max_tokens(model: str, temperature: float = 0):
    """Helper function to create LLM with max_tokens parameter"""
    return ChatOpenAI(
        temperature=temperature,
        model=model,
        api_key=os.getenv("OPENAI_API_KEY"),
        # max_tokens=max_tokens
    )


#  structured output usage
class GraderOutput(TypedDict):
    grade: float
    justification: str


# node functions
def writer(state: State) -> State:
    """Writes an essay based on the article and user query."""
    
    # max_tokens = state.get("max_tokens", 4000)
    writerllm = get_llm_with_max_tokens("gpt-4o-mini")

    messages = [
        SystemMessage(content=writer_prompt),
        HumanMessage(content=state["user_query"]),
    ]

    llm_response = writerllm.invoke(messages)

    return {
        "article": llm_response.content,
        "messages": [
            HumanMessage(content=state["user_query"]),
            AIMessage(content=llm_response.content),
        ],
    }


def grader(state: State) -> State:
    """Grades the essay and provides justification and suggested edits."""
    
    # max_tokens = state.get("max_tokens", 4000)
    graderllm = get_llm_with_max_tokens("gpt-5-nano")  # Grader needs less tokens

    messages = [
        SystemMessage(content=grader_prompt),
        HumanMessage(content=state["article"]),
    ]

    structured_grader_llm = graderllm.with_structured_output(GraderOutput)
    result: GraderOutput = structured_grader_llm.invoke(messages)

    grade_f = float(result["grade"])
    best_article = state["best_article"]
    best_score = state["best_score"]
    # update best if improved (>= keeps the latest equal-grade article)
    if grade_f >= best_score:
        best_score = grade_f
        best_article = state["article"]

    print(f'Grader : Iteration {state["iterations"]} \n \n \n')
    # print(state["article"])
    print(f"Grade: {result['grade']}")
    print(f"Best Score so far: {best_score}")

    return {
        "grade": result["grade"],
        "justification": result["justification"],
        "iterations": state["iterations"] + 1,
        "best_score": best_score,
        "best_article": best_article,
        "messages": [
            # record what we sent the model
            HumanMessage(content=state["article"]),
            # only record grade; record what the model returned (raw structured output content)
            AIMessage(
                content=f"Grade: {float(result['grade'])}, Justification: {result['justification']}"
            ),
        ],
    }


def routerfunction(state: State) -> str:
    """Routes to END if grade is satisfactory, else to suggestion_provider."""
    target_score = state.get("target_score", 8.0)
    max_iterations = state.get("max_iterations", 3)
    
    if state["grade"] >= target_score or state["iterations"] >= max_iterations:
        return "end"
    else:
        return "suggestion_provider"


def suggestion_provider(state: State) -> State:
    """Improves the essay based on suggested edits."""
    
    # max_tokens = state.get("max_tokens", 4000)
    improverllm = get_llm_with_max_tokens("gpt-5-nano")

    messages = [
        SystemMessage(content=suggestion_provider_prompt),
        HumanMessage(
            content=f"Article: {state['article']}\n Justification: {state['justification']}"
        ),
    ]

    suggestor_llm_response = improverllm.invoke(messages)
    # print(suggestor_llm_response.content)

    return {
        "suggested_edits": suggestor_llm_response.content,
        "messages": [
            HumanMessage(
                content=f"Article: {state['article']}\n Justification: {state['justification']}"
            ),
            AIMessage(content=suggestor_llm_response.content),
        ],
    }


def changer(state: State) -> State:
    """Changes the article based on suggested edits."""
    
    # max_tokens = state.get("max_tokens", 4000)
    changerllm = get_llm_with_max_tokens("gpt-4.1")

    messages = [
        SystemMessage(content=changer_prompt),
        HumanMessage(
            content=f"Article: {state['article']}\n Suggested Edits: {state['suggested_edits']}"
        ),
    ]

    changer_llm_response = changerllm.invoke(messages)
    print("*"*50, )
    # print("Changer:", )
    print(f"CHANGER : {state['iterations']}")
    # print(changer_llm_response.content)

    return {
        "article": changer_llm_response.content,
        "messages": [
            HumanMessage(
                content=f"Article: {state['article']}\nSuggested Edits: {state['suggested_edits']}"
            ),
            AIMessage(content=changer_llm_response.content),
        ],
    }