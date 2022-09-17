# Project Three: BloC2
![bloc2](https://user-images.githubusercontent.com/25112189/188766237-26706310-1e7f-42b5-b6df-fb76c6309b57.jpg)

---

## Background
BloC2 is a malware command and control (C2) implemented via Ethereum smart contract.
The malware operator uses a Streamlit web applciation to issue encrypted commands to the blockchain.  These commands are read by the malware clients, decrypted, and executed.  The results of the commands executed are sent to a destination specified by the malware operator.

---

## Bloc2 Controller
<img width="749" alt="bloc2 controller" src="https://user-images.githubusercontent.com/25112189/190848216-0b4c3a8c-ca92-4e58-9b58-89ec791e352d.png">

---

## Installation

```sh
git clone git@github.com:travispeska/gwu_project_three.git
cd gwu_project_three/
pip install -r requirements.txt
```

---

## Smart Contract Deployment with Remix IDE
1. Open [Remix IDE](https://remix.ethereum.org/)
2. Click "Load From GitHub"
3. Enter "https://raw.githubusercontent.com/travispeska/gwu_project_three/main/contracts/bloc2.sol"
4. Click "Import"
5. Select Compiler Version 0.5.1.7+commit.d19bba13
6. Click "Compile bloc2.sol"
7. Deploy to Blockchain

---

## BloC2 Controller Streamlit Application

```sh
cd gwu_project_three/server/
streamlit run server.py
Open Browser > http://localhost:8501
```

---

## License

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
