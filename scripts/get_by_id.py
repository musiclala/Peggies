import os
from dotenv import load_dotenv

import harvest_api_MR


load_dotenv(r"D:\PycharmProj\working_projects\time-managment-internal\.env")
TOKEN = os.getenv("TOKEN")
ACCOUNT_ID = os.getenv("ACCOUNTID")

harvest = harvest_api_MR.Harvest(TOKEN, ACCOUNT_ID)
users = harvest.get_active_users()
for i in users:
    print(i)

result = harvest.get_by_user_id('', '20230101', '20230131')
print(result)