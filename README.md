# Smart Airport Baggage HMI Prototype

A standalone Python/Flask web dashboard prototype for Group 08.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## Important
This is a prototype only. It is **not connected to OpenPLC Runtime**.
The action endpoints are mock actions designed to demonstrate the HMI and dashboard workflow.

## Intended later architecture

Browser HMI -> Node.js / API layer -> OpenPLC Runtime
                       |
                       +-> CoppeliaSim
                       |
                       +-> Node-RED / data stream

The mock action routes can later be replaced by real PLC/API calls.
# smart-airport-baggage
