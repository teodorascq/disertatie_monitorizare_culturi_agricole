
import subprocess
import time
import os
import signal
import sys

BASE_DIR = r"C:/Users/stama/Desktop/MASTER/DISERTATIE/monitorizare"
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")


def run_orchestrator(run_simulator=True):
    processes = []
    try:
        print("=== PORNESC RECEIVER (fundal) ===")
        receiver_proc = subprocess.Popen(
            [sys.executable, "receiver.py"], cwd=SCRIPTS_DIR)
        processes.append(receiver_proc)
        time.sleep(2)

        print("=== PORNESC DASHBOARD (fundal) ===")
        dashboard_proc = subprocess.Popen(
            [sys.executable, "dashboard_interactiv.py"], cwd=SCRIPTS_DIR)
        processes.append(dashboard_proc)
        time.sleep(2)

        if run_simulator:
            print("=== PORNESC SIMULATOR (trimite date) ===")
            subprocess.run(
                [sys.executable, "simulator_sender.py"], cwd=SCRIPTS_DIR)
            print("=== SIMULATOR TERMINAT — dashboard si receiver raman active ===")

        print("Apasa Ctrl+C pentru a opri tot.")
        while True:
            time.sleep(1)
            if dashboard_proc.poll() is not None:
                print("Dashboard-ul s-a inchis.")
                break

    except KeyboardInterrupt:
        print("\n=== OPRESC TOATE PROCESELE ===")
    finally:
        for proc in processes:
            if proc.poll() is None:
                proc.send_signal(signal.SIGTERM)
        print("=== GATA ===")


if __name__ == "__main__":
    run_simulator = "--no-sim" not in sys.argv
    run_orchestrator(run_simulator=run_simulator)
