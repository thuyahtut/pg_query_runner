from pathlib import Path
from tabulate import tabulate
from openpyxl import Workbook
import yaml
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from sshtunnel import SSHTunnelForwarder

CONFIG_PATH = "config/servers.yaml"
QUERY_PATH = "queries/summary_report.sql"
OUTPUT_JSON = "output/results.json"
OUTPUT_XLSX = "output/results.xlsx"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)["servers"]

def load_query():
    return Path(QUERY_PATH).read_text()

def run_all_servers():
    servers = load_config()
    query = load_query()
    results = []

    for server in servers:
        host = server["ssh_host"]
        host_name = server["host_name"]
        print(f"\n🔐 Connecting to SSH: {host} ({host_name})")
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
                                print(f"\n📄 Results from Project: {host_name} | Database: {db}")
                                print(tabulate(rows, headers="keys", tablefmt="fancy_grid"))
                                # for row in rows:
                                #     row["_project"] = host_name
                                #     row["_server"] = host
                                #     row["_database"] = db
                                #     results.append(row)
                            else:
                                print(f"\n📄 No results for Project: {host_name} | Database: {db}")
                        conn.close()
                    except Exception as e:
                        print(f"❌ Error for {db} on {host}: {e}")
        except Exception as e:
            print(f"❌ SSH Connection failed to {host}: {e}")

    Path("output").mkdir(exist_ok=True)

    # Save JSON
    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to {OUTPUT_JSON}")

    # Save Excel (one sheet per database)
    if results:
        print("📁 Writing Excel report to output/results.xlsx")
        wb = Workbook()
        wb.remove(wb.active)  # remove default sheet

        # Group rows per sheet name
        grouped = {}
        for row in results:
            project = row.get("_project")
            db = row.get("_database")
            sheet_name = f"{project} - {db}"[:31]  # Excel sheet name max 31 chars
            if sheet_name not in grouped:
                grouped[sheet_name] = []
            grouped[sheet_name].append(row)

        for sheet_name, rows in grouped.items():
            ws = wb.create_sheet(title=sheet_name)
            headers = list(rows[0].keys())
            ws.append(headers)
            for r in rows:
                ws.append([r.get(h, "") for h in headers])

        wb.save(OUTPUT_XLSX)
        print(f"📁 Excel saved to {OUTPUT_XLSX}")
