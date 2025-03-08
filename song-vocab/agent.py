from instructor import OpenAISchema
from pydantic import Field
from typing import List, Callable, Dict, Type
from pydantic import BaseModel
import ollama  # Changed from: from ollama import Ollama
from dataclasses import dataclass

from tools.search_web import search_web
from tools.get_page_content import get_page_content
from tools.extract_vocabulary import extract_vocabulary

class LyricsAndVocabulary(OpenAISchema):
    """
    Response schema containing lyrics and vocabulary.
    """
    lyrics: str = Field(..., description="The lyrics of the song.")
    vocabulary: List[str] = Field(..., description="A list of vocabulary words from the lyrics.")

# Tool Parameter Schemas
class ToolParams(BaseModel):
    """Base class for tool parameters"""
    pass

class SearchWebParams(ToolParams):
    query: str = Field(..., description="Search query for finding lyrics")

class GetPageContentParams(ToolParams):
    url: str = Field(..., description="URL of the page to fetch")

class ExtractVocabularyParams(ToolParams):
    text: str = Field(..., description="Text to extract vocabulary from")

@dataclass
class Tool:
    name: str
    description: str
    param_schema: type[ToolParams]
    function: Callable

def format_tools(tools: List[Tool]) -> str:
    tool_descriptions = []
    for tool in tools:
        # Create an empty instance of the schema class
        schema_instance = tool.param_schema()
        params = ", ".join(schema_instance.model_json_schema().get("properties", {}).keys())
        tool_descriptions.append(f"{tool.name}({params}): {tool.description}")
    return "\n".join(tool_descriptions)

# Tool definitions
TOOLS = [
    Tool(
        name="search_web",
        description="Search the web for song lyrics",
        param_schema=SearchWebParams,
        function=search_web
    ),
    Tool(
        name="get_page_content",
        description="Get content from a webpage",
        param_schema=GetPageContentParams,
        function=get_page_content
    ),
    Tool(
        name="extract_vocabulary",
        description="Extracts vocabulary words from given lyrics.",
        param_schema=ExtractVocabularyParams,
        function=extract_vocabulary
    ),
]

def create_agent(ollama_client):
    def format_tools(tools: List[Tool]) -> str:
        tool_descriptions = []
        for tool in tools:
            params = ", ".join(tool.param_schema.model_json_schema().get("properties", {}).keys())
            tool_descriptions.append(
                f"{tool.name}({params}): {tool.description}"
            )
        return "\n".join(tool_descriptions)

    system_prompt = f"""You are a helpful assistant that finds song lyrics and extracts vocabulary.
Available tools:
{format_tools(TOOLS)}

Please use these tools to help find lyrics and extract vocabulary."""

    def run_agent(message_request: str) -> LyricsAndVocabulary:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message_request},
        ]
        
        response = ollama_client.chat(
            model="llama3.2:1b",  # Updated to use available model
            messages=messages,
            stream=False,
            options={
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.param_schema.model_json_schema(),
                        },
                    }
                    for tool in TOOLS
                ]
            }
        )
        
        return LyricsAndVocabulary(
            lyrics=response.message.content,
            vocabulary=extract_vocabulary(response.message.content)
        )

    return run_agent


if __name__ == '__main__':
    ollama_client = ollama.Client()  # Changed from: Ollama()
    agent = create_agent(ollama_client)
    request = "Find the lyrics for Bohemian Rhapsody by Queen and extract vocabulary"
    result = agent(request)
    print(result)