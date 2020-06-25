
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
            self.did = resp_data["did"]
        logging.debug(f"Got DID: {did}")

    #returns some JSON from the agent if successful
    async def post_schema(self, schema_body=None):

        if not schema_body :
            schema_body = {
                "attributes": ["name", "date", "age"],
                "schema_version": "1.0",
                "schema_name": "Test Name",
            }

        schema_resp  = await self.aries_post("/schemas", data = schema_body)

        if not schema_resp: 
            print("NONETYPE RESPONSE")
            return None 
        schema_id = schema_resp["schema_id"]
        logging.debug(f"GOT schema_ID: {schema_id}")

        return schema_id

    async def post_creddef(self, schema_id, rev_sup: bool=False):
        cred_def = {
            "schema_id": schema_id,
            "support_revocation": rev_sup,
        }

        resp = await self.aries_post(
            "/credential-definitions",
            cred_def
        )

        cred_id = resp["credential_defintion_id"]
        logging.debug(f"credential defintion id acquired: {cred_id}")
        return cred_id








    async def __exit__(self):
        await self.session.close()

    async def aries_req(self, method, path, data = None) -> aiohttp.ClientResponse:

        fullpath = self.admin_url + path

        logging.debug(f"making {method} request to {fullpath}")

        async with self.session.request(method, self.admin_url + path, json = data) as resp:
            resp_text = await resp.text()
            if not resp_text:
                return None
            try:
                print("json is: ", resp_text)
                return json.loads(resp_text)
            except json.JSONDecodeError as e: 
                logging.debug("error decoding json")
                return resp_text

    async def aries_get(self, path):
        try:
            response = await self.aries_req("GET", path)
            return response
        except Exception as e:
            logging.debug(f"EROR DURING GET REQ TO {path}")
            pass


    async def aries_post(self, path, data = None):

        try:
            response = await self.aries_req("POST", path, data=data)
            return response
        except Exception as e:
            logging.debug(f"ERROR DURING post REQ TO {path}")
            pass


    async def get_current_public_did(self):
        try:
            response = await self.aries_get("/wallet/did/public")
            return response
        except Exception as e:
            pass

    async def set_current_public_did(self, did = None):
        if did:
            self.did = did
        try:
            did_data = {
                "did": self.did,
            }
            result = await self.aries_post("/wallet/did/public",json.dumps(did_data))
            return result
        except Exception as e:
            pass




#testing 
agent = BaseAgent(
        ledger_host = "localhost",
        ledger_port = "9000",
        admin_host = "localhost",
        admin_port = "8080",
        inbound_port = "8000",
        name = "test.agent")

loop = asyncio.get_event_loop()

#loop.run_until_complete(agent.register_did())

status = loop.run_until_complete(agent.aries_get("/status"))
print(f"status is: {status}")


public_did = loop.run_until_complete(agent.aries_get("/wallet/did/public"))
print(f"current public did is: {public_did}")

#did_resp = loop.run_until_complete(agent.set_current_public_did(did="3kmcnCq7GzJ8FUSWxsrihw"))
#print(f"resp is: {did_resp}")

#public_did = loop.run_until_complete(agent.aries_get("/wallet/did/public"))
#print(f"current public did is: {public_did}")

dids = loop.run_until_complete(agent.aries_get("/wallet/did"))
print(f"current dids: {dids}")

#text = loop.run_until_complete(agent.post_schema())
#print(f"Response text: {text}")

temp = "PjisyYVtLEA8fAsy9MT1rv:2:Test Name:1.0"

cred_id = loop.run_until_complete(agent.post_creddef(temp))
print(f"cred_def id is: {cred_id}")

loop.run_until_complete(agent.__exit__())
loop.stop()
loop.close()



