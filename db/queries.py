from .client import supabase

def get_all_locations(): 
    return supabase.table("locations").select("*").execute()