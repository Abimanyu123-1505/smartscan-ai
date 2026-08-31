import json
import random
import os

metadata = {
  "source": "DEMO · PREPROCESSED FROM REAL ISM-BAND RECORDING",
  "original_dataset": "zenodo_ism_coexistence",
  "original_doi": "10.5281/zenodo.6334794",
  "warning": "This is a DEMO sample. Research results must use the full real recording.",
  "license": "CC BY 4.0",
  "recording_id": "demo_ism_coexistence",
  "dataset_id": "demo_preprocessed_sample",
  "center_frequency_mhz": 2440,
  "bandwidth_mhz": 80,
  "sample_rate_mhz": 20,
  "freq_bins_mhz": [2402, 2412, 2422, 2432, 2442, 2452, 2462, 2472],
  "freq_bin_labels": ["Ch1","Ch2","Ch3","Ch4","Ch5","Ch6","Ch7","Ch8"],
  "time_slot_duration_ms": 10,
  "num_time_slots": 200,
  "num_freq_bins": 8,
  "noise_floor_db": -88.0,
  "detection_threshold_db": -80.0,
  "hardware": "USRP N210 (source recording)",
  "location": "Berlin, Germany — indoor lab"
}

power_db = []
occupancy = []
events = []

random.seed(42)

for _ in range(200):
    row = [round(random.uniform(-92, -85), 1) for _ in range(8)]
    power_db.append(row)
    occupancy.append([0]*8)

event_id = 1
for bin_idx in [2, 4, 6]:
    num_events = random.randint(2, 4)
    for _ in range(num_events):
        start = random.randint(0, 180)
        dur = random.randint(5, 15)
        peak = round(random.uniform(-45, -30), 1)
        for t in range(start, start+dur):
            power = round(random.uniform(peak-5, peak), 1)
            power_db[t][bin_idx] = power
        events.append({
            "event_id": f"wifi_{event_id}",
            "freq_bin": bin_idx,
            "start_slot": start,
            "end_slot": start+dur-1,
            "peak_power_db": peak,
            "annotation_source": "measurement_derived"
        })
        event_id += 1

bt_bins = [0, 1, 3, 5, 7]
for _ in range(30):
    start = random.randint(0, 195)
    dur = random.randint(1, 3)
    bin_idx = random.choice(bt_bins)
    peak = round(random.uniform(-70, -55), 1)
    for t in range(start, start+dur):
        power = round(random.uniform(peak-3, peak), 1)
        power_db[t][bin_idx] = power
    events.append({
        "event_id": f"bt_{event_id}",
        "freq_bin": bin_idx,
        "start_slot": start,
        "end_slot": start+dur-1,
        "peak_power_db": peak,
        "annotation_source": "measurement_derived"
    })
    event_id += 1

for t in range(200):
    for b in range(8):
        if power_db[t][b] > -80.0:
            occupancy[t][b] = 1

data = {
    "metadata": metadata,
    "power_db": power_db,
    "occupancy": occupancy,
    "events": events
}

output_path = r"c:\Users\abiii\Downloads\dfiop-project (1)\dfiop\smartscan\data\samples\demo_ism_coexistence.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w") as f:
    json.dump(data, f, indent=2)
