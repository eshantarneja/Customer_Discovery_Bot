from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser

class Sender:
    def __init__(self, name, resume, career_interest, key_accomplishments, llm):
        self.name = name
        self.resume = resume
        self.career_interest = career_interest
        self.key_accomplishments = key_accomplishments
        self.relevant_content = None
        self.llm = llm

    def process_relevant_content(self):
        """Process all sender information into relevant content"""
        print("Extracting content from resume...")
        resume_content = self.extract_from_resume()
        
        print("Extracting content from career interests...")
        interests_content = self.extract_from_career_interests()
        
        print("Extracting content from key accomplishments...")
        accomplishments_content = self.extract_from_key_accomplishments()

        print("Combining extracted content...")
        self.relevant_content = self.combine_extracted_content(
            resume_content,
            interests_content,
            accomplishments_content
        )
        
        print("Content processing complete!")
        return self.relevant_content

    def extract_from_resume(self):
        """Extract relevant information from resume"""
        template = """
        Given the following resume, extract the most relevant information that would be valuable for professional emails. 
        Focus on:
        - Educational background
        - Key work experiences or internships
        - Technical skills or certifications
        - Notable projects or achievements

        Resume:
        {resume}

        Extracted relevant content:
        """
        
        prompt = PromptTemplate(
            input_variables=["resume"],
            template=template
        )
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"resume": self.resume})

    def extract_from_career_interests(self):
        """Extract relevant information from career interests"""
        template = """
        Given the following career interests, extract the most relevant information for professional emails.
        Focus on:
        - Key areas of interest
        - Professional goals
        - Industry focus
        - Specific technologies or fields of interest

        Career Interests:
        {interests}

        Extracted relevant content:
        """
        
        prompt = PromptTemplate(
            input_variables=["interests"],
            template=template
        )
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"interests": self.career_interest})

    def extract_from_key_accomplishments(self):
        """Extract relevant information from key accomplishments"""
        template = """
        Given the following key accomplishments, extract the most relevant information for professional emails.
        Focus on:
        - Most significant achievements
        - Leadership experiences
        - Project outcomes
        - Skills demonstrated

        Key Accomplishments:
        {accomplishments}

        Extracted relevant content:
        """
        
        prompt = PromptTemplate(
            input_variables=["accomplishments"],
            template=template
        )
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"accomplishments": "\n".join(self.key_accomplishments)})

    def combine_extracted_content(self, resume_content, interests_content, accomplishments_content):
        """Combine and summarize all extracted content"""
        template = """
        Combine and summarize the following extracted information into a cohesive summary 
        that would be useful for professional emails. Focus on creating a clear narrative 
        that highlights the most relevant aspects of the person's background and interests.

        Resume Content:
        {resume_content}

        Career Interests:
        {interests_content}

        Key Accomplishments:
        {accomplishments_content}

        Combined Summary:
        """
        
        prompt = PromptTemplate(
            input_variables=["resume_content", "interests_content", "accomplishments_content"],
            template=template
        )
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({
            "resume_content": resume_content,
            "interests_content": interests_content,
            "accomplishments_content": accomplishments_content
        })

    def get_relevant_content(self):
        """Get the processed relevant content, processing it if not already done"""
        if self.relevant_content is None:
            self.process_relevant_content()
        return self.relevant_content
