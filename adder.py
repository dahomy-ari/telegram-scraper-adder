from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest
import configparser
import os
import sys
import csv
import traceback
import time
import random
import asyncio  # Import the asyncio library
from telethon.errors import FloodWaitError

# Color codes for terminal output
re = "\033[1;31m"
gr = "\033[1;32m"
cy = "\033[1;36m"

SLEEP_TIME_1 = 10  # Sleep time between requests
SLEEP_TIME_2 = 100  # Sleep time for flood errors

# Initial instructions
print(re + "NOTE:")
print("1. Telegram only allows adding 200 members to a group per user.")
print("2. Use multiple Telegram accounts to add more members.")
print("3. Add only 50 members in group each time to avoid flood errors.")
print("4. Then wait for 15-30 minutes before adding members again.")
print("5. Ensure you enable 'Add User' permission in your group.")

# Read configuration settings
cpass = configparser.RawConfigParser()
cpass.read('config.data')

# Get API credentials
try:
    api_id = cpass['cred']['id']
    api_hash = cpass['cred']['hash']
    phone = cpass['cred']['phone']
    client = TelegramClient(phone, api_id, api_hash)
except KeyError:
    os.system('clear')
    print(re + "[!] Run python setup.py first !!\n")
    sys.exit(1)

async def main():
    await client.start()
    
    # Load users from CSV file
    users = []
    with open("members.csv", encoding='UTF-8') as f:
        rows = csv.reader(f, delimiter=",", lineterminator="\n")
        next(rows, None)  # Skip header
        for row in rows:
            user = {
                'username': row[0],
                'id': int(row[1]),
                'access_hash': int(row[2]),
                'name': row[3]
            }
            users.append(user)

    # Retrieve groups
    chats = []
    last_date = None
    chunk_size = 200
    groups = []

    result = await client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=chunk_size,
        hash=0
    ))
    chats.extend(result.chats)

    for chat in chats:
        try:
            if chat.megagroup:
                groups.append(chat)
        except Exception as e:
            continue

    # Choose target group
    print(gr + 'Choose a group to add members:' + cy)
    for i, group in enumerate(groups):
        print(str(i) + '- ' + group.title)

    g_index = int(input(gr + "Enter a Number: " + re))
    target_group = groups[g_index]
    target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)

    mode = int(input(gr + "Enter 1 to add by username or 2 to add by ID: " + cy))

    # Adding users
    n = 0
    for user in users:
        n += 1
        if n % 80 == 0:
            await asyncio.sleep(10)  # Enforce a wait after every 80 attempts
        
        try:
            print("Checking if {} is a bot.".format(user['id']))
            # Check if the user is a bot
            user_entity = await client.get_entity(user['username'] if mode == 1 else InputPeerUser(user['id'], user['access_hash']))

            if user_entity.bot:
                print("Skipping bot: {}".format(user['username']))
                continue

            print("Adding {}".format(user['id']))

            user_to_add = (await client.get_input_entity(user['username']) if mode == 1 else InputPeerUser(user['id'], user['access_hash']))
            await client(InviteToChannelRequest(target_group_entity, [user_to_add]))
            print("User added. Waiting for a short while...")
            await asyncio.sleep(random.uniform(1, 3))  # Random sleep between 1-3 seconds

        except FloodWaitError as e:
            print(f"{re}Flood wait for {e.seconds} seconds. Waiting...")
            await asyncio.sleep(e.seconds)  # Wait for the specified amount of time
            continue  # Continue to the next user after waiting
            
        except PeerFloodError:
            print("Flood error from Telegram. Stopping. Please try again later.")
            await asyncio.sleep(SLEEP_TIME_2)
            break
            
        except UserPrivacyRestrictedError:
            print("User's privacy settings prevent adding them. Skipping...")
            await asyncio.sleep(random.uniform(1, 2))  # Short wait before next action
            
        except Exception as e:
            traceback.print_exc()
            print("Unexpected Error, skipping...")
            continue

# Run the main function using asyncio
asyncio.run(main())