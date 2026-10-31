import json
import csv


def export_json(results, output_path):
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

def export_csv(results, output_path):
   with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["hostname", "ip", "site", "validation"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
