import os
from supabase import create_client, Client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def post(gr, material, success):
  if gr not in [9, 10, 11, 12]:
    print("Error Encountered - Grade out of Range")
    return
  try:
    response = (
        supabase.table("posts")
        .upsert({"Grade": gr, "Material": material, "Success": success, "is_published": True})
        .execute()
    )
    print("Publish Success")
  except:
    print("Publish failed")
