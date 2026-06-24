import serial
import time
import os

SERIAL_OUT = "COM11"
BAUD_RATE = 115200
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PATH = os.path.join(BASE_DIR, "data", "simulated_results_2.txt")


def main():
    print(f"Deschid portul {SERIAL_OUT}...")
    ser = serial.Serial(SERIAL_OUT, BAUD_RATE)
    time.sleep(1)

    if not os.path.exists(FILE_PATH):
        print(f"Fisierul nu exista: {FILE_PATH}")
        ser.close()
        return

    print(f"Trimit mesajele din {FILE_PATH}...")
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            full = line + "\n"
            print(">>> TRIMIT:", full.strip())
            ser.write(full.encode())
            time.sleep(0.2)

    ser.close()
    print("Gata.")


if __name__ == "__main__":
    main()
