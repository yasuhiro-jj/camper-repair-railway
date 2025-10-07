#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
Notion�f�[�^�x�[�X�\���m�F�X�N���v�g�i�X�V�Łj 
 
import os 
from dotenv import load_dotenv 
 
# .env�t�@�C���̓ǂݍ��� 
load_dotenv() 
 
def check_notion_databases(): 
    """Notion�f�[�^�x�[�X�̍\����ID���m�F""" 
    print("?? Notion�f�[�^�x�[�X�\���m�F���J�n...") 
 
    # ���ϐ��̊m�F 
    notion_api_key = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN") 
    if not notion_api_key: 
        print("? Notion API�L�[���ݒ肳��Ă��܂���") 
        return 
 
    try: 
        from notion_client import Client 
        client = Client(auth=notion_api_key) 
 
        # ���[�U�[�����擾 
        user = client.users.me() 
        print(f"? Notion�ڑ�����: {user.get('name', 'Unknown User')}") 
 
        # ���ϐ�����f�[�^�x�[�XID���擾 
        node_db_id = os.getenv("NODE_DB_ID") 
        case_db_id = os.getenv("CASE_DB_ID") 
        item_db_id = os.getenv("ITEM_DB_ID") 
 
        print("?? ���ϐ�����擾�����f�[�^�x�[�XID�̃e�X�g:") 
 
        # �f�f�t���[DB 
        if node_db_id: 
            try: 
                response = client.databases.retrieve(database_id=node_db_id) 
                title = "�^�C�g���Ȃ�" 
                title_prop = response.get("title", []) 
                if title_prop: 
                    title = title_prop[0].get("plain_text", "�^�C�g���Ȃ�") 
                print(f"? �f�f�t���[DB ({node_db_id}): {title}") 
            except Exception as e: 
                print(f"? �f�f�t���[DB ({node_db_id}): �A�N�Z�X�s�� - {e}") 
 
        # �C���P�[�XDB 
        if case_db_id: 
            try: 
                response = client.databases.retrieve(database_id=case_db_id) 
                title = "�^�C�g���Ȃ�" 
                title_prop = response.get("title", []) 
                if title_prop: 
                    title = title_prop[0].get("plain_text", "�^�C�g���Ȃ�") 
                print(f"? �C���P�[�XDB ({case_db_id}): {title}") 
            except Exception as e: 
                print(f"? �C���P�[�XDB ({case_db_id}): �A�N�Z�X�s�� - {e}") 
 
        # ���i�E�H��DB 
        if item_db_id: 
            try: 
                response = client.databases.retrieve(database_id=item_db_id) 
                title = "�^�C�g���Ȃ�" 
                title_prop = response.get("title", []) 
                if title_prop: 
                    title = title_prop[0].get("plain_text", "�^�C�g���Ȃ�") 
                print(f"? ���i�E�H��DB ({item_db_id}): {title}") 
            except Exception as e: 
                print(f"? ���i�E�H��DB ({item_db_id}): �A�N�Z�X�s�� - {e}") 
 
    except ImportError as e: 
        print(f"? notion-client���C�u�������C���X�g�[������Ă��܂���: {e}") 
        print("?? �������@: pip install notion-client==2.2.1") 
    except Exception as e: 
        print(f"? Notion�ڑ��G���[: {e}") 
 
if __name__ == "__main__": 
    check_notion_databases() 
