import yaml
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from sshtunnel import SSHTunnelForwarder
from pathlib import Path
from tabulate import tabulate
import csv
from openpyxl import Workbook

CONFIG_PATH = "config/servers.yaml"
QUERY_PATH = "queries/summary_report.sql"
OUTPUT_PATH = "output/results.json"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)["servers"]

def load_query():
    return Path(QUERY_PATH).read_text()

def run_all_servers():
    servers = load_config()
    query = load_query()
    results = []
    all_raw_data = {}

    for server in servers:
        host = server["ssh_host"]
        host_name = server["host_name"]
        print(f"\n🔐 Connecting to SSH: {host}")
        try:
            with SSHTunnelForwarder(
                (host, server.get("ssh_port", 22)),
                ssh_username=server["ssh_user"],
                ssh_pkey=server["ssh_key_path"],
                remote_bind_address=('127.0.0.1', 5432),
                local_bind_address=('127.0.0.1', 5433)
            ) as tunnel:
                for db in server["databases"]:
                    try:
                        conn = psycopg2.connect(
                            host="127.0.0.1",
                            port=5433,
                            user=server["db_user"],
                            password=server["db_password"],
                            dbname=db
                        )
                        with conn.cursor(cursor_factory=RealDictCursor) as cur:
                            cur.execute(query)
                            rows = cur.fetchall()
                            if rows:
                                print(f"\n📄 Results from: \n Project: {host_name} \n Database: {db}:")
                                print(tabulate(rows, headers="keys", tablefmt="fancy_grid"))
                                for row in rows:
                                    row["_server"] = host
                                    row["_database"] = db
                                    results.append(row)
                            else:
                                print(f"\n📄 {host}/{db}: No results.")
                        conn.close()
                    except Exception as e:
                        print(f"❌ Error for {db} on {host}: {e}")
        except Exception as e:
            print(f"❌ SSH Connection failed to {host}: {e}")

    # Save JSON
    Path("output").mkdir(exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to {OUTPUT_PATH}")

    # # Save CSV
    # if results:
    #     keys = results[0].keys()
    #     with open("output/results.csv", "w", newline="") as f:
    #         writer = csv.DictWriter(f, fieldnames=keys)
    #         writer.writeheader()
    #         writer.writerows(results)
    #     print("📁 CSV saved to output/results.csv")
    # Save Excel with sheets by project + db
    if results:
        print("📁 Writing Excel report to output/results.xlsx")
        wb = Workbook()
        wb.remove(wb.active)  # remove default sheet

        # Group results by project/database
        grouped = {}
        for row in results:
            project = row.get("_project")
            db = row.get("_database")
            sheet_name = f"{project} - {db}"
            if sheet_name not in grouped:
                grouped[sheet_name] = []
            grouped[sheet_name].append(row)

        for sheet_name, rows in grouped.items():
            ws = wb.create_sheet(title=sheet_name[:31])  # Excel max sheet name = 31 chars
            headers = list(rows[0].keys())
            ws.append(headers)
            for r in rows:
                ws.append([r[h] for h in headers])

        wb.save("output/results.xlsx")
        print("📁 Excel saved to output/results.xlsx")
