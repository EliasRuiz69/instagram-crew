import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import TavilySearchTool
from .tools.imagen_tool import HuggingFaceImageTool
from .tools.instagram_tool import InstagramPublisherTool


def get_claude_llm():
    """Crea una instancia del LLM Claude Sonnet 4.5"""
    return LLM(
        model="anthropic/claude-sonnet-4-5-20250929",
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        max_tokens=2048,
        temperature=0.7
    )


@CrewBase
class InstagramCrew:
    """Crew de automatización de contenido para Instagram"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def trend_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["trend_researcher"],
            llm=get_claude_llm(),
            tools=[TavilySearchTool(
                search_depth="basic",
                max_results=3,
                include_answer=True
            )],
            verbose=True,
            allow_delegation=False,
            max_iter=2
        )

    @agent
    def instagram_copywriter(self) -> Agent:
        return Agent(
            config=self.agents_config["instagram_copywriter"],
            llm=get_claude_llm(),
            verbose=True,
            allow_delegation=False
        )

    @agent
    def image_creator(self) -> Agent:
        return Agent(
            config=self.agents_config["image_creator"],
            llm=get_claude_llm(),
            tools=[HuggingFaceImageTool()],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def instagram_publisher(self) -> Agent:
        return Agent(
            config=self.agents_config["instagram_publisher"],
            llm=get_claude_llm(),
            tools=[InstagramPublisherTool()],
            verbose=True,
            allow_delegation=False
        )

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config["research_task"])

    @task
    def copywriting_task(self) -> Task:
        return Task(config=self.tasks_config["copywriting_task"])

    @task
    def image_generation_task(self) -> Task:
        return Task(config=self.tasks_config["image_generation_task"])

    @task
    def instagram_publish_task(self) -> Task:
        return Task(config=self.tasks_config["instagram_publish_task"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,
            planning=False
        )
