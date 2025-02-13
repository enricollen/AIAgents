#!/usr/bin/env python
import os
import warnings
from dotenv import load_dotenv
from quiz_maker.crew import ThemeExtractorCrew

load_dotenv()
warnings.filterwarnings("ignore")

def ensure_output_dir():
    """Ensure the output directory exists"""
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

def run():
    """
    Run the crew.
    """
    ensure_output_dir()
    url = "YOUR_URL_HERE"
    inputs = {
        'url': url,
    }
    ThemeExtractorCrew().crew().kickoff(inputs=inputs)

if __name__ == "__main__":
    run()