import os 
from dotenv import load_dotenv

load_dotenv()


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1"
)

MODEL = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")

MAX_AGENT_ITERATIONS = 10

MEMORY_FILE = os.getenv("MEMORY_FILE", "memory.md")

MCP_CONFIG_FILE = "mcp_servers.json"

