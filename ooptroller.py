
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

DOCKER_PATH = "/home/george/projects/aries-cloudagent-python/scripts/run_docker"
INTERNAL_HOST = "127.0.0.1"
ADMIN_PORT = "8080"
INBOUND_PORT = "8000"
OUTBOUND_PROTOCOL = "http"
INBOUND_PROTOCOL  = "http"
VENV_ARIES_PATH = "/home/george/projects/simple_controller/simple_controller/bin/aca-py"
LEDGER_URL = "http://" + INTERNAL_HOST + ":9000"
GENESIS_URL = LEDGER_URL + "/genesis"




#helpers
flatten = lambda l: [item for sublist in l for item in sublist]

def is_json():
    if not None:
        return True
    return False

def synth_url(
    protocol: str = "http",
    host: str = "localhost",
    port: int = None):

    if not port:
        return None
    url = protocol + "://" + host + ":" + port
    return url

#for development
def unique_ident():
    rand_name = str(random.randint(100_000, 999_999))
    seed = ("my_seed_000000000000000000000000" + rand_name)[-32:]
    return seed

def return_dev_params():
    params = {
        "ledger_port": "9000",
        "admin_port": "8080",
        "inbound_port": "8000",
        "inbound_protocol": "http",
        "outbound_protocol": "http",
    }

def gen_schema(name, version, attrs):
    schema_body = {
        "name": name,
        "version": version,
    }
    return schema_body

#base class
class BaseAgent:
    def __init__(
        self,
        ledger_host: str = None,
        ledger_port: str = None,
        admin_host: str=None,
        admin_port: str = None,
        inbound_port: str = None,
        seed: str = None,
        name: str = None):

        self.ledger_url = synth_url(host = ledger_host, port = ledger_port)
        self.admin_url = synth_url(host = admin_host, port = admin_port)
        self.inbound_url = synth_url(port = inbound_port)
        self.seed = seed
        self.name = name
        self.session = aiohttp.ClientSession()
        self.genesis_text = None
        self.did = None

        if not self.seed:
            self.seed = unique_ident()

    async def get_genesis_text(self):
        genesis = None
        gensis_url = self.ledger_url + "/genesis"
        try:
            async with session.get(genesis_url) as response:
                genesis = await response.text()
        except Exception:
            logging.debug(f"error fetching genesis text from: {genesis_url}")
            logging.debug(f"{genesis}")
        return genesis

    async def register_did(self):
        logging.debug(f"Registering with seed {self.seed}")
        schema_data = {"alias": self.name, "seed": self.seed, "role": "TRUST_ANCHOR"}
        async with self.session.post(
            self.ledger_url + "/register", json=schema_data
        ) as resp:
            if resp.status != 200:
                raise Exception(f"Error registering DID, response code {resp.status}")

            resp_data = await resp.json()
            did = resp_data["did"]
            self.did = did
        logging.debug(f"Got DID: {did}")

#returns some JSON from the agent if successful
async def post_schema(self, schema_body) -> aiohttp.ClientResponse:
    if not schema_body :
        schema_body = {
            "schema_name": "Test Name",
            "schema_version": "1.0",
            "attributes": ["name", "date", "age"],
        }
    logging.debug("Attemtping to request to agent")
    logging.debug("with data: {}".format(schema_body))
    logging.debug(f"to link: {admin_path}")

    async with self.session.request(
        "POST", self.admin_path, json=schema_body
    ) as resp:
        resp_text = await resp.text()
        try:
            return json.loads(resp_text)
        except Exception as e:
            print("e")
        return resp_text

agent = BaseAgent(
        ledger_host = "localhost",
        ledger_port = "9000",
        admin_host = "localhost",
        admin_port = "8080",
        inbound_port = "8000",
        name = "test.agent")

loop = asyncio.get_event_loop()

loop.run_until_complete(agent.register_did())

agent.register_did()

