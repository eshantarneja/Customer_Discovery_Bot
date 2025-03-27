from langgraph.graph import StateGraph
from typing import Dict, TypedDict, Annotated
import json

class EmailState(TypedDict):
    draft: str
    critique: str
    revision_count: int
    revision_step: str
    sender_info: str
    context: str

def create_email_graph(email_agent):
    # Initialize the graph
    workflow = StateGraph(EmailState)
    
    # Define the nodes as functions first
    def draft_initial_email(state: EmailState) -> Dict:
        """Creates the initial email draft"""
        draft = email_agent.draft_email(
            tone="professional",
            sender_info=state["sender_info"],
            new_context=state["context"]
        )
        return {
            "draft": draft,
            "revision_count": 0,
            "revision_step": "start"
        }

    def critique_email(state: EmailState) -> Dict:
        """Critiques the current draft"""
        critique = email_agent.critique_email(state["draft"])
        return {
            "critique": critique,
            "revision_step": "critiqued"
        }

    def revise_with_critique(state: EmailState) -> Dict:
        """Revises based on critique"""
        revised_draft = email_agent.revise_with_critique(
            state["draft"], 
            state["critique"]
        )
        return {
            "draft": revised_draft,
            "revision_step": "critique_revised"
        }

    def revise_with_few_shot(state: EmailState) -> Dict:
        """Revises using few-shot examples"""
        improved_draft = email_agent.improve_email(state["draft"])
        return {
            "draft": improved_draft,
            "revision_step": "few_shot_revised",
            "revision_count": state["revision_count"] + 1
        }

    def end_workflow(state: EmailState) -> Dict:
        """Final node to properly end the workflow"""
        return {
            "revision_step": "completed"
        }

    # Add nodes to the graph
    workflow.add_node("draft_initial_email", draft_initial_email)
    workflow.add_node("critique_email", critique_email)
    workflow.add_node("revise_with_critique", revise_with_critique)
    workflow.add_node("revise_with_few_shot", revise_with_few_shot)
    workflow.add_node("end", end_workflow)

    # Define the edges
    workflow.add_edge('draft_initial_email', 'critique_email')
    
    # After critique, go to either revise_with_critique or end
    workflow.add_conditional_edges(
        'critique_email',
        lambda x: 'revise_with_critique' if x['revision_count'] < 3 else 'end',
        {
            'revise_with_critique': 'revise_with_critique',  # Fixed: Direct path to revise_with_critique
            'end': 'end'
        }
    )

    # After revise_with_critique, always go to revise_with_few_shot
    workflow.add_edge('revise_with_critique', 'revise_with_few_shot')

    # After few_shot, either go back to critique or end
    workflow.add_conditional_edges(
        'revise_with_few_shot',
        lambda x: 'critique_email' if x['revision_count'] < 2 else 'end',
        {
            'critique_email': 'critique_email',
            'end': 'end'
        }
    )

    # Set the entry point
    workflow.set_entry_point("draft_initial_email")
    
    return workflow.compile()

def run_email_workflow(email_agent, sender_info, context):
    try:
        # Create the graph
        workflow = create_email_graph(email_agent)
        
        # Initialize the state
        initial_state = EmailState(
            draft="",
            critique="",
            revision_count=0,
            revision_step="start",
            sender_info=sender_info,
            context=context
        )
        
        # Run the workflow using invoke
        final_state = workflow.invoke(initial_state)
        
        return final_state
    except Exception as e:
        print(f"Error in workflow: {str(e)}")
        raise
