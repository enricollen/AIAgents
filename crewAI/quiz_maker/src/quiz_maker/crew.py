""" # UNCOMMENT BLOCK TO ENABLE LANGTRACE MONITORING
import os
from dotenv import load_dotenv
load_dotenv()
from langtrace_python_sdk import langtrace
langtrace.init(os.getenv("LANGTRACE_API_KEY"))"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool
from .tools.divide_topics_into_txt import TopicsDivider

@CrewBase
class ThemeExtractorCrew:
	"""ThemeExtractorCrew for extracting themes from web pages"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def web_scraper(self) -> Agent:
		return Agent(
			config=self.agents_config['web_scraper'],
			tools=[ScrapeWebsiteTool()],
			verbose=True
		)
  
	@agent
	def content_cleaner(self) -> Agent:
		return Agent(
			config=self.agents_config['content_cleaner'],
			verbose=True
		)

	@agent
	def content_organizer(self) -> Agent:
		return Agent(
			config=self.agents_config['content_organizer'],
			verbose=True
		)
  
	@agent
	def topics_divider(self) -> Agent:
		return Agent(
			config=self.agents_config['topics_divider'],
			tools=[TopicsDivider()],
			verbose=True
		)

	def get_manager(self) -> Agent:
		return Agent(
			config=self.agents_config['manager'],
			allow_delegation=True,
			verbose=True
		)

	@task
	def analyze_webpage(self) -> Task:
		return Task(
			config=self.tasks_config['analyze_webpage'],
			agent=self.web_scraper()
		)
  
	@task
	def clean_web_content(self) -> Task:
		return Task(
			config=self.tasks_config['clean_web_content'],
			agent=self.content_cleaner(),
			depends_on=[self.analyze_webpage()]
		)

	@task
	def organize_content(self) -> Task:
		return Task(
			config=self.tasks_config['organize_content'],
			agent=self.content_organizer(),
			output_file='output/original_content.txt',
			depends_on=[self.clean_web_content()]
		)
  
	@task
	def divide_topics(self) -> Task:
		return Task(
		config=self.tasks_config['divide_topics'],
		agent=self.topics_divider()
	)

	@crew
	def crew(self) -> Crew:
		"""Creates the ThemeExtractorCrew crew"""
		return Crew(
			agents=[self.web_scraper(), self.content_cleaner(), self.content_organizer(), self.topics_divider()],
			tasks=self.tasks,
			#manager_agent=self.get_manager(),
			process=Process.sequential,
			verbose=True
		)