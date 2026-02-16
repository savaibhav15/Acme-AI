"""Main entry point for the Acme Dental AI Agent."""

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from src.agent import create_acme_dental_agent


def main():
    """Run the Acme Dental booking agent CLI."""
    load_dotenv()
    
    print("=" * 60)
    print("Welcome to Acme Dental AI Booking Assistant")
    print("=" * 60)
    print("\nHello! 👋 I'm here to help you book a dental checkup appointment.")
    print("Type 'exit', 'quit', or 'q' to end the conversation\n")
    
    agent = create_acme_dental_agent()
    
    # Initialize conversation state
    state = {"messages": []}
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ["exit", "quit", "q"]:
            print("\nThank you for using Acme Dental booking assistant. Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            # Add user message to state
            state["messages"].append(HumanMessage(content=user_input))
            
            # Invoke the agent (this runs the graph)
            result = agent.invoke(state)
            
            # Update state with full conversation
            state = result
            
            # Get the last message (agent's response)
            messages = result.get("messages", [])
            if messages:
                last_message = messages[-1]
                
                # Print agent response
                if hasattr(last_message, "content") and last_message.content:
                    print(f"\nAgent: {last_message.content}\n")
            else:
                print("\nAgent: I apologize, but I couldn't generate a response. Please try again.\n")
                
        except Exception as e:
            print(f"\nError: {str(e)}\n")
            print("Please try again or type 'exit' to quit.\n")


if __name__ == "__main__":
    main()
