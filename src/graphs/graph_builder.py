from langgraph.graph import StateGraph, START, END

from src.nodes.basic_chatbot_node import BasicChatbotNode
from src.states.state import State


class GraphBuilder:

    def __init__(self, llm):
        self.basic_chatbot_node = None
        self.llm = llm
        self.graph_builder = StateGraph(State)

    def basic_chatbot_build_graph(self):
        """
        Builds a basic chatbot graph using langgraph.
        This method initializes a chatbot node using the "BasicChatBotNode" class
        and integrates it into the graph. The chatbot node is set as both the entry and exit point of the graph.
        """

        self.basic_chatbot_node = BasicChatbotNode(self.llm)

        self.graph_builder.add_node("chatbot", self.basic_chatbot_node.process)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_edge("chatbot", END)


    def setup_graph(self, usecase):
        # if usecase == "topic":
        #     self.build_topic_graph()

        # if usecase == "language":
        #     self.build_language_graph()

        self.basic_chatbot_build_graph()
        return self.graph_builder.compile()
