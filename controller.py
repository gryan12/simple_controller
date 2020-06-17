
import asyncio
import aiohttp
import os
import sys
import random
import subprocess
import logging 

##logging
LOGGER = logging.getLogger(__name__)

event_stream_handler = logging.StreamHandler()
event_stream_handler.setFormatter(logging.Formatter("\nEVENT: %(message)s"))

DEBUG_EVENTS = os.getenv("EVENTS")
EVENT_LOGGER = logging.getLogger("event")
EVENT_LOGGER.setLevel(logging.DEBUG if DEBUG_EVENTS else logging.NOTSET)
EVENT_LOGGER.addHandler(event_stream_handler)
EVENT_LOGGER.propagate = False

my_env = os.environ.copy()
DOCKER_PATH = "/home/blint/projects/aries-cloudagent-python/scripts/run_docker"
INTERNAL_HOST = "127.0.0.1"
ADMIN_PORT = "7000"
INBOUND_PORT = "8000"
OUTBOUND_PROTOCOL = "http"
INBOUND_PROTOCOL  = "http"


LEDGER_URL = "http://" + INTERNAL_HOST + ":9000"
GENESIS_URL = LEDGER_URL + "/genesis"

#helper
flatten = lambda l: [item for sublist in l for item in sublist]

def start_docker_process(args): 
    #p1 = subprocess.run(args, stdout = subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    p1 = subprocess.run([
                         DOCKER_PATH, 
                         "start", 
                         "--inbound-transport", 
                         "http", 
                         "127.0.0.1", 
                         "8000", 
                         "--outbound-transport", 
                         "http", 
                         "--admin", 
                         "127.0.0.1", 
                         "7000", 
                         "--admin-insecure-mode",
                         ],
                         encoding="utf-8")

    return p1

async def get_genesis_text(): 
    genesis = None
    try: 
        async with aiohttp.ClientSession() as session: 
            async with session.get(GENESIS_URL) as response: 
                genesis = await response.text()
        
    except Exception: 
        LOGGER.exception("Error loading genesis transactions:")

    print(genesis)
    return genesis

def gen_rand_seed(): 
    seed = None
    rand_name = str(random.randint(100_000, 999_999))
    seed = ("my_seed_000000000000000000000000" + rand_name)[-32:]
    return seed 

async def register_did(loop):
    seed = gen_rand_seed()
    ident = "My.Agent"
    print(f"Registering with seed {seed}")
    client_session = aiohttp.ClientSession(loop=loop)

    data = {"alias": ident, "seed": seed, "role": "TRUST_ANCHOR"}

    async with client_session.post(
        LEDGER_URL + "/register", json=data
    ) as resp:
        if resp.status != 200:
            raise Exception(f"Error registering DID, response code {resp.status}")
        nym_info = await resp.json()
        did = nym_info["did"]
    print(f"Got DID: {did}")
    await client_session.close()



def send_simple_msg(agent_endpoint): 
    return None


loop = asyncio.get_event_loop()
loop.run_until_complete(register_did(loop))








