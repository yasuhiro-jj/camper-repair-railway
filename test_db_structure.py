import os 
from dotenv import load_dotenv 
from notion_client import Client 
 
load_dotenv() 
 
print("Testing database structure with current IDs...") 
 
notion_api_key = os.getenv("NOTION_API_KEY") 
client = Client(auth=notion_api_key) 
 
# 現在のデータベースIDを取得 
node_db_id = os.getenv("NODE_DB_ID") 
case_db_id = os.getenv("CASE_DB_ID") 
item_db_id = os.getenv("ITEM_DB_ID") 
 
print(f"Current Node DB ID: {node_db_id}") 
print(f"Current Case DB ID: {case_db_id}") 
print(f"Current Item DB ID: {item_db_id}") 
 
# データベース構造を確認 
try: 
    response = client.databases.retrieve(database_id=node_db_id) 
    print(f"? Node DB accessible: {response.get('title', [{}])[0].get('plain_text', 'No title')}") 
    print("Properties:", list(response.get('properties', {}).keys())) 
except Exception as e: 
    print(f"? Node DB error: {e}") 
 
try: 
    response = client.databases.retrieve(database_id=case_db_id) 
    print(f"? Case DB accessible: {response.get('title', [{}])[0].get('plain_text', 'No title')}") 
    print("Properties:", list(response.get('properties', {}).keys())) 
except Exception as e: 
    print(f"? Case DB error: {e}") 
 
try: 
    response = client.databases.retrieve(database_id=item_db_id) 
    print(f"? Item DB accessible: {response.get('title', [{}])[0].get('plain_text', 'No title')}") 
    print("Properties:", list(response.get('properties', {}).keys())) 
except Exception as e: 
    print(f"? Item DB error: {e}") 
