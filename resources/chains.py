import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv


load_dotenv()
class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-8b-instant")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

           ### INSTRUCTION:
                Subject: Expertise in [Job Title/Relevant Skill] | Tailored Solutions for [Company Name]

                Hi [Recipient's First Name],

                I noticed [Company Name] is seeking [briefly reference specific goal/requirement from the job opening, e.g., "to streamline operations through AI automation"]. At [Your Company], we specialize in delivering [specific service, e.g., "custom AI-driven workflow solutions"] that align with objectives like yours.

                How we can support:

                [Actionable insight/relevant approach based on job description, e.g., "Designing scalable tools to automate [specific process mentioned in the job posting]"].

                [Second actionable insight, e.g., "Optimizing resource allocation to reduce operational costs by 20-40%"].

                Relevant work:

                [Portfolio Link 1]: [Briefly describe a project that mirrors the job’s requirements, e.g., "Built an AI-powered inventory system for a logistics client, cutting processing time by 35%"].

                [Portfolio Link 2]: [Highlight another project, e.g., "Developed a SaaS platform for a retail chain, boosting cross-departmental efficiency"].

                I’d love to discuss how we can tailor these strategies to [Company Name]’s needs. Could we schedule a 15-minute call this week?

                Best regards,
                [Your Full Name]
                [Your Designation]
                [Your Company]
                [Your Direct Contact] | [Your Company Website]

                ### EMAIL (NO PREAMBLE):




            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links})
        return res.content



if __name__ == "__main__":
    api_key = os.getenv("GROQ_API_KEY")
    print(f"GROQ_API_KEY: {api_key}") 