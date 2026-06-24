import serial
import time
import os
import csv

# Cu simulatorul: COM10 (jumatatea perechii virtuale com0com)
# Cu placa reala:  schimba la portul COM al Nicla Vision (ex. "COM3", "COM5")
#                  -> il gasesti in Device Manager -> Ports (COM & LPT)
SERIAL_PORT = "COM10"
BAUD_RATE = 115200

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE = os.path.join(BASE_DIR, "data", "log_culturi.csv")
ERROR_LOG_FILE = os.path.join(BASE_DIR, "data", "erori_serial.log")

HEADER = ["timestamp", "stage", "conf_stage",
          "disease", "conf_disease", "recommendation", "fps"]
REQUIRED_FIELDS = ["stage", "conf_stage", "disease", "conf_disease", "recomm"]


def ensure_csv():
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)


def log_error(raw_text, reason):
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {reason} | RAW: {raw_text}\n")


def parse_message(msg):
    parts = msg.split(";")
    data = {}
    for p in parts:
        if "=" in p:
            key, val = p.split("=", 1)
            data[key.strip().lower()] = val.strip()

    missing = [field for field in REQUIRED_FIELDS if not data.get(field)]
    if missing:
        return None, f"campuri lipsa: {missing}"

    return [
        time.strftime("%Y-%m-%d %H:%M:%S"),
        data.get("stage", ""),
        data.get("conf_stage", ""),
        data.get("disease", ""),
        data.get("conf_disease", ""),
        data.get("recomm", ""),
        data.get("fps", ""),
    ], None


def main():
    ensure_csv()
    print(f"Ascult pe portul {SERIAL_PORT}...")
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(1)

    while True:
        line = ser.readline()
        if not line:
            continue

        text = line.decode(errors="ignore").strip()
        if not text:
            continue
        if not text.startswith("RESULT"):
            log_error(text, "linie ignorata (nu incepe cu RESULT)")
            continue

        row, error = parse_message(text)
        if error:
            print("[EROARE PARSARE]", error, "->", text)
            log_error(text, error)
            continue

        print("[RECEIVED]", row)
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)


if __name__ == "__main__":
    main()
