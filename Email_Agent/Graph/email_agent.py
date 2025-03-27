from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import os
from secrets import get_secret
from dotenv import load_dotenv
from Classes.contacts import Contact

class EmailAgent:
    def __init__(self, email_template=None):
        # Load environment variables
        load_dotenv()
        
        # Get OpenAI API key and verify it exists
        openai_api_key = os.getenv('OpenAPI_KEY') or get_secret('OpenAPI_KEY')
        if not openai_api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model_name="gpt-4o-mini",
            temperature=0.7
        )
        
        # Initialize experience chain
        experience_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI assistant that extracts key experiences and achievements."),
            ("user", "Given the following information about {name} from {company}, extract key experiences and achievements: \n\n{context} no more than 15 bullet points")
        ])
        
        self.experience_chain = LLMChain(
            llm=self.llm,
            prompt=experience_prompt
        )
        
        # Initialize email chain with default or custom template
        default_template = """
        Please stick to the following format only! Do not deviate from it:


        Hello [Insert First Name],

        I am a current student at Harvard and I am interested in learning more about grocery store operations. Specifically, [Insert whatever they do at the company as what I am interested in learning about].

        [Insert a explanation of why their background is an interesting profile for me to talk to and learn more about]
         
        Would you be open to a quick call sometime after 12p this week so I can learn more about your experiences?

        Best,
        Bill
        """
        
        # Use the provided template or fall back to the default
        template_to_use = email_template if email_template else default_template
        
        email_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a script that follows explicit instructions to fill in a template. You DO NOT add ANY content that is not requested. You DO NOT create your own template or modify the given template structure in any way."),
            ("user", f"""
            COPY AND PASTE THE FOLLOWING TEMPLATE EXACTLY AS IT IS, but ONLY replace the parts in [brackets] with appropriate content based on the person's information. DO NOT change ANY other text. DO NOT add ANY content outside the specified placeholders. DO NOT create your own format or structure:
            
            {template_to_use}
            
            Person information:
            - Name: {{name}}
            - Company: {{company}}
            - Background information: {{experiences}}
            
            CRITICAL INSTRUCTION: Your ONLY job is to replace [bracketed text] with appropriate content based on the person's information. DO NOT modify ANY other part of the template. DO NOT add signatures, additional greetings, or any other text not explicitly specified in the template.
            """)
        ])
        
        self.email_chain = LLMChain(
            llm=self.llm,
            prompt=email_prompt
        )

    async def process_contact(self, contact: Contact):
        """
        Process a contact asynchronously
        """
        try:
            # Run the experience chain
            experience_response = await self.experience_chain.ainvoke({
                "name": contact.full_name,
                "company": contact.company_name,
                "context": contact.context
            })
            experiences = experience_response.get('text', '')
            contact.context += experiences
            #print(f"In email agent, contacts context: {contact.context}")

            # Run the email chain
            email_response = await self.email_chain.ainvoke({
                "name": contact.full_name,
                "company": contact.company_name,
                "experiences": experiences
            })
            email_body = email_response.get('text', '')
            contact.draft_email = email_body

            print(f"In email agent, draft email: {contact.draft_email}")

            return experiences, email_body
            
        except Exception as e:
            print(f"Error in process_contact: {str(e)}")
            return "", ""

# Example usage:
# agent = EmailAgent()
# raw_context = "John Doe has 15 years of experience in automotive manufacturing, specializing in lean production methods. He led a team that reduced production costs by 30% at Tesla."
# person_name = "John Doe"
# company_name = "Tesla"
# experiences, email = agent.process_contact(person_name, company_name, raw_context)
# print("Extracted Experiences:")
# print(experiences)
# print("\nDraft Email:")
# print(email)


#            Hello [Insert First Name],
#
#           My name is Bill and I am building a tool to automate data entry into CRMs like Hubspot and Salesforce for manufacturers and distributors. 
#
#           [Insert Pithy explanation of why company could be a good fit for the product]
#                        
#         Would you be willing to jump on a call sometime after 1p this week so I can learn more about how you use your CRM and what other problems you might be facing?
#
#           Best,
#          Bill
#
#

