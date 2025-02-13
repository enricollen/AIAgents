import os
import re
from crewai.tools import BaseTool

class TopicsDivider(BaseTool):
    name: str = "Topics Divider"
    description: str = (
        "A tool for dividing topics into individual text files."
    )

    def _run(self):
        try:
            input_file = "output/original_content.txt"
            output_dir = "output/divided_topics"

            os.makedirs(output_dir, exist_ok=True)

            # read the content of the file
            with open(input_file, "r", encoding="utf-8") as f:
                content = f.read()

            # here we split content into topics with regex
            topics = re.split(r"(#\d+)", content)

            if not topics or len(topics) < 2:
                return "No topics found in the file."

            # process topics
            current_topic = None
            for part in topics:
                if re.match(r"#\d+", part.strip()):  # get topic number
                    if current_topic:
                        self._save_topic_file(output_dir, topic_number, current_topic.strip())

                    topic_number = part.strip() 
                    current_topic = ""
                else:
                    if current_topic is not None:
                        current_topic += part  # append content to the current topic

            # Save the last topic
            if current_topic:
                self._save_topic_file(output_dir, topic_number, current_topic.strip())

            return f"Topics successfully divided and saved in '{output_dir}' directory."

        except Exception as e:
            return f"Error processing topics: {str(e)}"

    def _save_topic_file(self, output_dir: str, topic_number: str, content: str):
        """Helper function to save a topic to a separate text file."""
        topic_filename = os.path.join(output_dir, f"topic_{topic_number[1:]}.txt")  # remove # from filename
        with open(topic_filename, "w", encoding="utf-8") as f:
            f.write(content)