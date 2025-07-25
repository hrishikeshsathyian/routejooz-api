import os
from supabase import create_client, Client
import dotenv

# Load environment variables from a .env file
dotenv.load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)