
import asyncio
import aiohttp
import os
import sys
import random
import subprocess
import json 
import logging 

##logging
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


event_stream_handler = logging.StreamHandler()
event_stream_handler.setFormatter(logging.Formatter("\nEVENT: %(message)s"))

DEBUG_EVENTS = os.getenv("EVENTS")
EVENT_LOGGER = logging.getLogger("event")
EVENT_LOGGER.setLevel(logging.DEBUG if DEBUG_EVENTS else logging.NOTSET)
EVENT_LOGGER.addHandler(event_stream_handler)
EVENT_LOGGER.propagate = False

my_env = os.environ.copy()
DOCKER_PATH = "/home/george/projects/aries-cloudagent-python/scripts/run_docker"
INTERNAL_HOST = "127.0.0.1"
ADMIN_PORT = "7000"
INBOUND_PORT = "8000"
OUTBOUND_PROTOCOL = "http"
INBOUND_PROTOCOL  = "http"


VENV_ARIES_PATH = "/home/george/projects/simple_controller/simple_controller/bin/aca-py"


LEDGER_URL = "http://" + INTERNAL_HOST + ":9000"
GENESIS_URL = LEDGER_URL + "/genesis"

#helper
flatten = lambda l: [item for sublist in l for item in sublist]

def command():
    p1 = sunprocessrun([
"PORTS="8080:8080 7000:7000" ./run_docker start --wallet-type indy --seed 000000000000000000000000000Agent --wallet-key welldone --wallet-name myWallet --genesis-url http://172.17.0.1:9000/genesis --inbound-transport http 0.0.0.0 8000 --outbound-transport http --admin 0.0.0.0 8080 --admin-insecure-mode"
    ],
    encoding = "utf-8")


def start_aries_process(aries_path):
    p1 = subprocess.run([
                         aries_path,
                         "start",
                         "--inbound-transport",
                         "http",
                         "127.0.0.1",
                         "8000",
                         "--outbound-transport",
                         "http",
                         "--admin",
                         "localhost",
                         "7000",
                         "--admin-insecure-mode",
                         ],
                         encoding="utf-8")


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

    logging.debug(f"Registering with seed {seed}")
    client_session = aiohttp.ClientSession(loop=loop)

    data = {"alias": ident, "seed": seed, "role": "TRUST_ANCHOR"}

    async with client_session.post(
        LEDGER_URL + "/register", json=data
    ) as resp:
        if resp.status != 200:
            raise Exception(f"Error registering DID, response code {resp.status}")
        nym_info = await resp.json()
        did = nym_info["did"]
    logging.debug(f"Got DID: {did}")
    await client_session.close()


#returns some JSON from the agent if successful
async def post_to_admin(loop) -> aiohttp.ClientResponse:
    admin_path = "http://localhost"  + ":" + ADMIN_PORT + "/schemas"
    schema_body = {
        "schema_name": "Test Name",
        "schema_version": "1.0",
        "attributes": ["name", "date", "age"],
    }

    logging.debug("Attemtping to request ot agent")
    logging.debug("with data: {}".format(schema_body))

    session = aiohttp.ClientSession(loop=loop)

    async with session.request(
        "POST", admin_path, json=schema_body
    ) as resp:

        response_text = await resp.text()

        try:
            return json.loads(resp_text)

        except Exception as e:
            print("e")

        return resp_text
    await session.close()

logging.debug("TEST")

print(os.getenv("DOCKERHOST"))


loop = asyncio.get_event_loop()
start_docker_process()
#loop.run_until_complete(register_did(loop))
#loop.run_until_complete(post_to_admin(loop))




