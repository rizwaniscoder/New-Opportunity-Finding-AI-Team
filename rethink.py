import streamlit as st
import sys
import re
from crewai import Agent, Task, Crew, Process
from langchain_community.tools.google_trends import GoogleTrendsQueryRun
from langchain_community.utilities.google_trends import GoogleTrendsAPIWrapper
from langchain_openai import ChatOpenAI
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

llm = ChatOpenAI(model="gpt-4o")

# google_trends_api_wrapper = GoogleTrendsAPIWrapper()
# google_trends_tool = GoogleTrendsQueryRun(api_wrapper=google_trends_api_wrapper)
google_search = SerperDevTool()
website_scrapper = ScrapeWebsiteTool()

# StreamToExpander class for output redirection
class StreamToExpander:
    def __init__(self, expander, buffer_limit=10000):
        self.expander = expander
        self.buffer = []
        self.buffer_limit = buffer_limit

    def write(self, data):
        cleaned_data = re.sub(r'\x1B\[\d+;?\d*m', '', data)
        if len(self.buffer) >= self.buffer_limit:
            self.buffer.pop(0)
        self.buffer.append(cleaned_data)

        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer.clear()

    def flush(self):
        if self.buffer:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer.clear()

# Streamlit app
st.title("RETHINK AI - New Opportunity Finder")

with st.form("research_form"):
    industry_keywords = st.text_input("Industry Keywords")
    industry_name = st.text_input("Industry Name")
    product_name = st.text_input("Product Name")
    submit_button = st.form_submit_button("Find New Opportunities")

if submit_button:
    product_details = {
        "name": product_name
    }
    
    
    # Define Agents
    market_researcher = Agent(
        role="Market Research Specialist",
        goal="To conduct thorough research on potential new markets, identify emerging trends, and uncover untapped opportunities for the company.",
        backstory="The Market Researcher is a data-driven explorer, skilled in analyzing market data, consumer behavior, and industry dynamics to identify the most promising avenues for expansion.",
        tools=[
            google_search, 
            website_scrapper,
            # google_trends_tool,
        ],
        llm=llm,
        verbose=True, 
    )

    industry_analyst = Agent(
        role="Industry Analysis Expert",
        goal="To provide in-depth analysis of the target industry, including key players, market size, growth potential, and competitive landscape.",
        backstory="The Industry Analyst is a seasoned expert, well-versed in the intricacies of the company's industry, and adept at identifying strategic opportunities and potential challenges.",
        tools=[
            google_search, 
            website_scrapper,
            # google_trends_tool,
        ],
        llm=llm,
        verbose=True, 
    )

    opportunity_evaluator = Agent(
        role="Opportunity Evaluation Specialist",
        goal="To assess the feasibility and potential impact of identified opportunities, providing recommendations on the most promising avenues for the company to pursue.",
        backstory="The Opportunity Evaluator is a strategic thinker, capable of weighing the risks and rewards of various opportunities, and providing actionable insights to guide the company's decision-making process.",
        tools=[
            google_search, 
            website_scrapper,
            # google_trends_tool,
        ],
        llm=llm,
        verbose=True, 
    )
    
    
    # Define Tasks with user inputs
    market_research_task = Task(
        description=f"Conduct comprehensive market research using Google Trends to identify potential new markets and emerging trends for the '{industry_keywords}' industry.",
        expected_output=f"A detailed report outlining potential new markets and emerging trends in the '{industry_keywords}' industry, based on Google Trends data.",
        agent=market_researcher,
    )

    industry_analysis_task = Task(
        description=f"Analyze the '{industry_name}' industry, including key players, market size, growth potential, and competitive landscape using Serpapi.",
        expected_output=f"A comprehensive industry analysis report covering key players, market size, growth potential, and competitive landscape for the '{industry_name}' industry.",
        agent=industry_analyst
    )

    opportunity_evaluation_task = Task(
        description=f"Assess the feasibility and potential impact of identified opportunities for the '{product_name}' using Serpapi.",
        expected_output=f"A detailed evaluation of the feasibility and potential impact of the identified opportunities for the '{product_name}', including recommendations on the most promising avenues to pursue.",
        agent=opportunity_evaluator
    )


    # Define the Crew
    research_crew = Crew(
        agents=[market_researcher, industry_analyst, opportunity_evaluator],
        tasks=[market_research_task, industry_analysis_task, opportunity_evaluation_task],
        process=Process.sequential 
    )

    process_output_expander = st.expander("Processing Output:")
    sys.stdout = StreamToExpander(process_output_expander)
    
    try:
        result = research_crew.kickoff()
        st.write(result)
    except Exception as e:
        st.error(f"Failed to process tasks: {e}")



# # Define custom tools - For Phase 2
# class SEMrushTool(BaseTool):
#     def _run(self, query):
#         # Implement SEMrush logic here
#         return f"SEMrush insights for '{query}'"

# class SalesNavigatorTool(BaseTool):
#     def _run(self, query):
#         # Implement Sales Navigator logic here
#         return f"Sales Navigator results for '{query}'"

# class DuxSoupTool(BaseTool):
#     def _run(self, profile_url):
#         # Implement Dux-Soup logic here
#         return f"Dux-Soup results for '{profile_url}'"

# class LushaTool(BaseTool):
#     def _run(self, query):
#         # Implement Lusha logic here
#         return f"Lusha results for '{query}'"

# class PandaDocTool(BaseTool):
#     def _run(self, document):
#         # Implement PandaDoc logic here
#         return f"PandaDoc results for '{document}'"

# class DocuSignTool(BaseTool):
#     def _run(self, document):
#         # Implement DocuSign logic here
#         return f"DocuSign results for '{document}'"

# class HelloSignTool(BaseTool):
#     def _run(self, document):
#         # Implement HelloSign logic here
#         return f"HelloSign results for '{document}'"

# class ZoomTool(BaseTool):
#     def _run(self, meeting_details):
#         # Implement Zoom logic here
#         return f"Zoom meeting results for '{meeting_details}'"

# class SlackTool(BaseTool):
#     def _run(self, message):
#         # Implement Slack logic here
#         return f"Slack message results for '{message}'"

# class TeamsTool(BaseTool):
#     def _run(self, team_details):
#         # Implement Microsoft Teams logic here
#         return f"Microsoft Teams results for '{team_details}'"
