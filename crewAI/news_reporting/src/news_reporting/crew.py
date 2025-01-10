from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from news_reporting.tools.news_parser_tool import NewsParserTool

@CrewBase
class NewsProcessingCrew:
    """News Parsing and Deduplication"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def news_parser(self) -> Agent:
        return Agent(
            config=self.agents_config['news_parser'],
            tools=[NewsParserTool()],
            verbose=True
        )
        
    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'],
            verbose=True
        )

    @task
    def fetch_news_task(self) -> Task:
        return Task(
            config=self.tasks_config['fetch_news_task'],
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
            output_file='src/news_reporting/outputs/report.md'
        )
  
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
			tasks=self.tasks, 
			process=Process.sequential,
			verbose=True,
        )