"""AI Agent for the Acme Dental Clinic using LangGraph."""

import os
from typing import Literal
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END

from .state import AgentState
from .tools import (
    get_available_times, 
    create_booking, 
    get_clinic_info, 
    search_knowledge_base,
    cancel_appointment,
    reschedule_appointment,
    find_user_bookings
)


def create_acme_dental_agent():
    """Create and configure the Acme Dental booking agent."""
    
    # Initialize the LLM with Claude
    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        temperature=0.7,
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    # Bind tools to the LLM
    tools = [
    get_available_times, 
    create_booking, 
    get_clinic_info, 
    search_knowledge_base,
    cancel_appointment,
    reschedule_appointment,
    find_user_bookings]

    llm_with_tools = llm.bind_tools(tools)
    
    # Create a tool map for execution
    tool_map = {
        "get_available_times": get_available_times,
        "create_booking": create_booking,
        "get_clinic_info": get_clinic_info,
        "search_knowledge_base": search_knowledge_base,
        "cancel_appointment": cancel_appointment,
        "reschedule_appointment": reschedule_appointment,
        "find_user_bookings": find_user_bookings
            }
    
    system_prompt = """You are a helpful AI assistant for Acme Dental clinic. Your role is to help patients book dental checkup appointments and answer their questions.

Your capabilities:
1. Book new appointments
2. Find existing appointments by email
3. Cancel existing appointments
4. Reschedule existing appointments
5. Answer questions from the knowledge base (pricing, policies, what to bring, etc.)
6. Check available appointment times
7. Generate booking confirmations

Booking process:
1. Greet the patient warmly
2. Ask for their name and email
3. Ask what date they'd like
4. Use get_available_times tool to show available slots
5. Once they choose a time, use create_booking tool
6. Provide confirmation with appointment details

For questions about the clinic:
- Use search_knowledge_base tool to answer questions about:
  - Pricing (€60 standard, €50 student/senior discount)
  - Appointment duration (30 minutes)
  - What to bring
  - Cancellation policy (24 hours notice)
  - Payment methods
  - And other clinic FAQs

Important:
- Be conversational and friendly
- Ask one question at a time
- Date format should be YYYY-MM-DD
- Always collect name, email, date, and time before booking
- Answer FAQ questions using the knowledge base tool

Current date: February 15, 2026"""

    def should_continue(state: AgentState) -> Literal["tools", "end"]:
        """Determine if we should continue to tools or end."""
        messages = state["messages"]
        last_message = messages[-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "end"
    
    def call_model(state: AgentState):
        """Call Claude with the current conversation state."""
        messages = state["messages"]
        
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt)] + list(messages)
        
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def execute_tools(state: AgentState):
        """Execute the tools that Claude requested."""
        messages = state["messages"]
        last_message = messages[-1]
        
        tool_messages = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Get the actual tool function
            tool_func = tool_map[tool_name]
            
            # Execute the tool
            result = tool_func.invoke(tool_args)
            
            # Create a tool message with the result
            tool_message = ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]
            )
            tool_messages.append(tool_message)
        
        return {"messages": tool_messages}
    
    # Create the workflow graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", execute_tools)  # ← Manual execution, NOT ToolNode
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    
    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")
    
    # Compile the graph
    agent = workflow.compile()
    
    return agent
