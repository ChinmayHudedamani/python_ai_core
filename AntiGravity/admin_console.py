import os
import sys
import json

# Ensure root and month1_python_core are in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
core_dir = os.path.join(root_dir, "month1_python_core")
if core_dir not in sys.path:
    sys.path.insert(0, core_dir)


def run_admin_console():
    print("==========================================================")
    print("        CENTAUR OS - CLINIC ADMIN & ANALYTICS CONSOLE     ")
    print("==========================================================")
    print("1. View Appointment Ledger (appointments_ledger.csv)")
    print("2. Run Financial ROI Calculator")
    print("3. Run Bot System Stress Test")
    print("4. Inspect Telemetry & Analytics Metrics")
    print("5. Exit Admin Console\n")

    while True:
        try:
            choice = input("Select Admin Option [1-5]: ").strip()
            if choice == "1":
                ledger_path = os.path.join(core_dir, "appointments_ledger.csv")
                if os.path.exists(ledger_path):
                    with open(ledger_path, "r", encoding="utf-8") as f:
                        print("\n--- APPOINTMENT LEDGER ---")
                        print(f.read())
                else:
                    print("\nNo appointments ledger found yet.")

            elif choice == "2":
                print("\n--- CLINIC FINANCIAL ROI CALCULATOR ---")
                print("• Onboarding Fee: ₹36,000")
                print("• Monthly Subscription: ₹6,000 / month")
                print("• Estimated High-Value Conversions: 4-6 leads / month")
                print("• Estimated Monthly Revenue Gain: ₹1,50,000+")

            elif choice == "3":
                print("\n--- RUNNING STRESS TEST ---")
                import subprocess
                subprocess.run([sys.executable, os.path.join(core_dir, "rigorous_bot_stress_test.py")])

            elif choice == "4":
                metrics_path = os.path.join(core_dir, "telemetry_metrics.json")
                if os.path.exists(metrics_path):
                    with open(metrics_path, "r", encoding="utf-8") as f:
                        print("\n--- TELEMETRY METRICS ---")
                        print(json.dumps(json.load(f), indent=2))
                else:
                    print("\nNo telemetry metrics recorded yet.")

            elif choice in ["5", "exit", "quit"]:
                print("Exiting Admin Console.")
                break
            else:
                print("Invalid option. Choose [1-5].")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting Admin Console.")
            break


if __name__ == "__main__":
    run_admin_console()
