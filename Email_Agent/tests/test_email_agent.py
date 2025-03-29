"""
Test the email drafting agent functionality
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Graph.email_agent import EmailAgent
from Classes.contacts import Contact

@patch('langchain_openai.ChatOpenAI')
def test_email_agent_initialization(mock_chat_openai, mock_env_variables):
    """Test that the EmailAgent initializes correctly"""
    # Setup
    mock_llm = MagicMock()
    mock_chat_openai.return_value = mock_llm
    
    # Test initialization
    agent = EmailAgent()
    
    # Verify LLM was initialized with the right parameters
    assert mock_chat_openai.called
    assert agent.llm is not None
    assert hasattr(agent, 'experience_chain')
    assert hasattr(agent, 'email_chain')

@patch('langchain.chains.LLMChain.invoke')
@patch('langchain_openai.ChatOpenAI')
def test_extract_experiences(mock_chat_openai, mock_invoke, mock_env_variables):
    """Test extracting experiences from context"""
    # Setup
    mock_llm = MagicMock()
    mock_chat_openai.return_value = mock_llm
    mock_invoke.return_value = {
        "text": "• Led a team of 10 engineers\n• Increased revenue by 30%\n• Launched 5 successful products"
    }
    
    # Create agent and test
    agent = EmailAgent()
    result = agent.extract_experiences(
        name="John Doe",
        company="Example Inc.",
        context="John Doe is a senior engineer with 10 years of experience..."
    )
    
    # Verify results
    assert "Led a team of 10 engineers" in result
    assert "Increased revenue by 30%" in result
    assert "Launched 5 successful products" in result

@patch('langchain.chains.LLMChain.invoke')
@patch('langchain_openai.ChatOpenAI')
def test_draft_email(mock_chat_openai, mock_invoke, mock_env_variables):
    """Test drafting an email"""
    # Setup
    mock_llm = MagicMock()
    mock_chat_openai.return_value = mock_llm
    mock_invoke.return_value = {
        "text": "Hello John,\n\nI am a current student at Harvard and I am interested in learning more about software engineering. Specifically, I'm curious about your work at Example Inc.\n\nYour background in leading engineering teams and launching successful products really stood out to me.\n\nWould you be open to a quick call sometime after 12p this week so I can learn more about your experiences?\n\nBest,\nBill"
    }
    
    # Create agent and test
    agent = EmailAgent()
    contact = Contact()
    contact.full_name = "John Doe"
    contact.job_title = "Senior Engineer"
    contact.company_name = "Example Inc."
    
    result = agent.draft_email(
        contact=contact,
        experiences="• Led a team of 10 engineers\n• Increased revenue by 30%\n• Launched 5 successful products"
    )
    
    # Verify results
    assert "Hello John" in result
    assert "Harvard" in result
    assert "Bill" in result
    assert "call" in result

@patch('langchain.chains.LLMChain.invoke')
@patch('langchain_openai.ChatOpenAI')
def test_process_contact(mock_chat_openai, mock_invoke, mock_env_variables):
    """Test processing a complete contact"""
    # Setup
    mock_llm = MagicMock()
    mock_chat_openai.return_value = mock_llm
    
    # First invoke is for extract_experiences
    # Second invoke is for draft_email
    mock_invoke.side_effect = [
        {"text": "• Led a team of 10 engineers\n• Increased revenue by 30%"},
        {"text": "Hello John,\n\nI am a student at Harvard...\n\nBest,\nBill"}
    ]
    
    # Create agent and test
    agent = EmailAgent()
    contact = Contact()
    contact.full_name = "John Doe"
    contact.job_title = "Senior Engineer"
    contact.company_name = "Example Inc."
    contact.context = "John has 10 years of experience in software engineering..."
    
    # Process the contact
    processed_contact = agent.process_contact(contact)
    
    # Verify the contact has a draft email
    assert hasattr(processed_contact, 'draft_email')
    assert processed_contact.draft_email is not None
    assert "Hello John" in processed_contact.draft_email
