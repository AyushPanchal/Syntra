from src.states.state import State


class BasicChatbotNode:
    def __init__(self, llm):
        self.llm = llm

    def process(self, state: State) -> dict:
        """
        Process the state and return the response from the LLM.

        Args:
            state (State): The current state of the chatbot.

        Returns:
            dict: A dictionary containing the response from the LLM.
        """
        return {"messages": self.llm.invoke(state["messages"])}
