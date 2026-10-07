
from flask import Flask, jsonify, render_template, request
from datetime import datetime
import random, time

app = Flask(__name__)

state = {
    "system": "STOPPED",
    "fault": False,
    "fault_reason": "",
    "emergency": False,
    "queue": 0,
    "total": 0,
    "correct": 0,
    "misrouted": 0,
    "unsorted": 0,
    "jams": 0,
    "processing_times": [],
    "gates": {"DEL": 0, "BOM": 0, "DXB": 0},
    "events": []
}

def accuracy():
    judged = state["correct"] + state["misrouted"] + state["unsorted"]
    return round(100 * state["correct"] / judged, 1) if judged else 100.0

def avg_time():
    vals = state["processing_times"]
    return round(sum(vals) / len(vals), 1) if vals else 0.0

def throughput():
    # Demo value: intentionally simple mock calculation.
    return round(state["correct"] / 1.0, 1)

def add_event(message, kind="info"):
    state["events"].insert(0, {
        "time": datetime.now().strftime("%H:%M:%S"),
        "message": message,
        "kind": kind
    })
    state["events"] = state["events"][:12]

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/state")
def api_state():
    return jsonify({
        "system": state["system"],
        "fault": state["fault"],
        "fault_reason": state["fault_reason"],
        "emergency": state["emergency"],
        "queue": state["queue"],
        "total": state["total"],
        "correct": state["correct"],
        "misrouted": state["misrouted"],
        "unsorted": state["unsorted"],
        "jams": state["jams"],
        "accuracy": accuracy(),
        "avg_time": avg_time(),
        "throughput": throughput(),
        "gates": state["gates"],
        "events": state["events"],
    })

@app.post("/api/action/<action>")
def action(action):
    if action == "start":
        if state["fault"]:
            return jsonify(ok=False, message="Reset the active fault first."), 400
        if state["emergency"]:
            return jsonify(ok=False, message="Release E-STOP first."), 400
        state["system"] = "RUNNING"
        add_event("System started.", "success")

    elif action == "stop":
        state["system"] = "STOPPED"
        add_event("System stopped.", "warning")

    elif action == "reset":
        state["fault"] = False
        state["fault_reason"] = ""
        state["emergency"] = False
        state["system"] = "STOPPED"
        add_event("Fault reset. System ready.", "success")

    elif action == "estop":
        state["emergency"] = True
        state["system"] = "STOPPED"
        add_event("Emergency stop activated.", "danger")

    elif action == "misread":
        if state["system"] != "RUNNING":
            return jsonify(ok=False, message="Start the system first."), 400
        state["total"] += 1
        state["misrouted"] += 1
        state["queue"] = max(0, state["queue"] - 1)
        state["fault"] = True
        state["fault_reason"] = "MISROUTE"
        state["system"] = "STOPPED"
        add_event("MISROUTE detected: baggage reached an incorrect gate.", "danger")

    elif action == "jam":
        if state["system"] != "RUNNING":
            return jsonify(ok=False, message="Start the system first."), 400
        state["jams"] += 1
        state["fault"] = True
        state["fault_reason"] = "JAM"
        state["system"] = "STOPPED"
        add_event("JAM detected on conveyor.", "danger")

    elif action.startswith("scan_"):
        if state["system"] != "RUNNING":
            return jsonify(ok=False, message="Start the system first."), 400
        dest = action.split("_", 1)[1].upper()
        if dest not in state["gates"]:
            return jsonify(ok=False, message="Unknown destination."), 400

        state["queue"] += 1
        state["total"] += 1
        state["correct"] += 1
        state["gates"][dest] += 1
        state["queue"] = max(0, state["queue"] - 1)
        processing = round(random.uniform(2.2, 5.2), 1)
        state["processing_times"].append(processing)
        state["processing_times"] = state["processing_times"][-50:]
        add_event(f"Baggage routed successfully to {dest}.", "success")

    else:
        return jsonify(ok=False, message="Unknown action."), 404

    return jsonify(ok=True, message="Action completed.")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
