import os
from supabase import create_client, Client
url: str = os.environ.get("https://zydpwkgiuhkwrqxokatb.supabase.co")
key: str = os.environ.get("sb_publishable_Y9QENj5oiW1h7fIl67S14A_zRNV90Ot")
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
