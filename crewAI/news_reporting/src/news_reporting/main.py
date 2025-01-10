#!/usr/bin/env python
import os
import sys
import warnings
from dotenv import load_dotenv
from news_reporting.crew import NewsProcessingCrew

load_dotenv()
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

RSS_FEED_URL = str(os.getenv("RSS_FEED_URL"))

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'rss_url': RSS_FEED_URL,
    }
    NewsProcessingCrew().crew().kickoff(inputs=inputs)

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'rss_url': RSS_FEED_URL
    }
    try:
        NewsProcessingCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        NewsProcessingCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'rss_url': RSS_FEED_URL
    }
    try:
        NewsProcessingCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")