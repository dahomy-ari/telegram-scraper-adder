from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.errors import FloodWaitError
import os, sys
import configparser
import csv
import time

re = "\033[1;31m"
gr = "\033[1;32m"
cy = "\033[1;36m"

cpass = configparser.RawConfigParser()
cpass.read('config.data')

try:
    api_id = cpass['cred']['id']
    api_hash = cpass['cred']['hash']
    phone = cpass['cred']['phone']
    client = TelegramClient(phone, api_id, api_hash)
except KeyError:
    os.system('cls')
    print(re + "[!] Run python3 setup.py first !!\n")
    sys.exit(1)

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    client.sign_in(phone, input(gr + '[+] Enter the code: ' + re))

os.system('cls')
chats = []
last_date = None
chunk_size = 200
groups = []

result = client(GetDialogsRequest(
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
    except:
        continue

print(gr + '[+] Choose a group to scrape members :' + re)
i = 0
for g in groups:
    print(gr + '[' + cy + str(i) + '] - ' + g.title)
    i += 1

print('')
g_index = input(gr + "[+] Enter a Number : " + re)
target_group = groups[int(g_index)]

print(gr + '[+] Fetching Members...')
time.sleep(1)
all_participants = []
all_participants = client.get_participants(target_group, aggressive=True)

print(gr + '[+] Saving In file...')
time.sleep(1)

with open("members.csv", "w", encoding='UTF-8') as f:
    writer = csv.writer(f, delimiter=",", lineterminator="\n")
    writer.writerow(['username', 'user id', 'access hash', 'name', 'group', 'group id'])

    for user in all_participants:
        if user.bot:  # Skip bots
            continue  # Skip this iteration if the user is a bot
        
        # Get username
        username = user.username if user.username else ""
        
        # Get user name
        first_name = user.first_name if user.first_name else ""
        last_name = user.last_name if user.last_name else ""
        name = (first_name + ' ' + last_name).strip()

        # Write user information to the CSV file
        try:
            writer.writerow([username, user.id, user.access_hash, name, target_group.title, target_group.id])      
        except Exception as e:
            print(re + f"[!] Error writing to file: {e}")

        # Add sleep to prevent hitting throttle limits
        time.sleep(1)  # Adjust the sleep duration as needed

print(gr + '[+] Members scraped successfully. Subscribe to the Termux Professor YouTube Channel For Add Members')