from sshtunnel import SSHTunnelForwarder
import psycopg2
from psycopg2.extras import RealDictCursor

# Your SQL query
QUERY = """
SELECT 'Contacts' AS Name, COUNT(*) AS Count, TO_CHAR(MAX(create_date), 'DD Mon YYYY') AS "Last Created Date" FROM res_partner WHERE create_uid IS NOT NULL AND create_uid NOT IN (SELECT id FROM res_users WHERE login IN ('admin', '__system__'))
UNION ALL
SELECT 'Sales Orders', COUNT(*), TO_CHAR(MAX(create_date), 'DD Mon YYYY') FROM sale_order WHERE create_uid IS NOT NULL AND create_uid NOT IN (SELECT id FROM res_users WHERE login IN ('admin', '__system__'))
UNION ALL
SELECT 'Purchase Orders', COUNT(*), TO_CHAR(MAX(create_date), 'DD Mon YYYY') FROM purchase_order WHERE create_uid IS NOT NULL AND create_uid NOT IN (SELECT id FROM res_users WHERE login IN ('admin', '__system__'))
UNION ALL
SELECT 'Products', COUNT(*), TO_CHAR(MAX(create_date), 'DD Mon YYYY') FROM product_template WHERE create_uid IS NOT NULL AND create_uid NOT IN (SELECT id FROM res_users WHERE login IN ('admin', '__system__'))
UNION ALL
SELECT 'Manufacture Orders', COUNT(*), TO_CHAR(MAX(create_date), 'DD Mon YYYY') FROM mrp_production WHERE create_uid IS NOT NULL AND create_uid NOT IN (SELECT id FROM res_users WHERE login IN ('admin', '__system__'))
UNION ALL
SELECT 'Bill of Materials', COUNT(*), TO_CHAR(MAX(create_date), 'DD Mon YYYY') FROM mrp_bom WHERE create_uid IS NOT NULL AND create_uid NOT IN (SELECT id FROM res_users WHERE login IN ('admin', '__system__'))
UNION ALL
SELECT 'Customer Invoices', COUNT(*), TO_CHAR(MAX(create_date), 'DD Mon YYYY') FROM account_move WHERE move_type = 'out_invoice' AND create_uid IS NOT NULL AND create_uid NOT IN (SELECT id FROM res_users WHERE login IN ('admin', '__system__'))
UNION ALL
SELECT 'Vendor Bills', COUNT(*), TO_CHAR(MAX(create_date), 'DD Mon YYYY') FROM account_move WHERE move_type = 'in_invoice' AND create_uid IS NOT NULL AND create_uid NOT IN (SELECT id FROM res_users WHERE login IN ('admin', '__system__'))
UNION ALL
SELECT 'Payments', COUNT(*), TO_CHAR(MAX(create_date), 'DD Mon YYYY') FROM account_payment WHERE create_uid IS NOT NULL AND create_uid NOT IN (SELECT id FROM res_users WHERE login IN ('admin', '__system__'))
UNION ALL
SELECT 'Journal Entries', COUNT(*), TO_CHAR(MAX(create_date), 'DD Mon YYYY') FROM account_move WHERE move_type = 'entry' AND create_uid IS NOT NULL AND create_uid NOT IN (SELECT id FROM res_users WHERE login IN ('admin', '__system__'))
UNION ALL
SELECT 'Journals', COUNT(*), TO_CHAR(MAX(create_date), 'DD Mon YYYY') FROM account_journal WHERE create_uid IS NOT NULL AND create_uid NOT IN (SELECT id FROM res_users WHERE login IN ('admin', '__system__'))
UNION ALL
SELECT 'Chart of Accounts', COUNT(*), TO_CHAR(MAX(create_date), 'DD Mon YYYY') FROM account_account WHERE create_uid IS NOT NULL AND create_uid NOT IN (SELECT id FROM res_users WHERE login IN ('admin', '__system__'))
;
"""

# Server and DB config
SERVER = {
    "ssh_host": "34.56.206.36",
    "ssh_port": 22,
    "ssh_user": "root",
    "ssh_key_path": "/home/thuya/.ssh/id_rsa",  # Update if your key is elsewhere
    "db_user": "odoo17",
    "db_password": "odoo17",
    "databases": ["genomic"]
}

def fetch_data():
    results = {}

    with SSHTunnelForwarder(
        (SERVER["ssh_host"], SERVER["ssh_port"]),
        ssh_username=SERVER["ssh_user"],
        ssh_pkey=SERVER["ssh_key_path"],
        remote_bind_address=('127.0.0.1', 5432),
        local_bind_address=('127.0.0.1', 5433)  # local port you will connect to
    ) as tunnel:
        for db in SERVER["databases"]:
            try:
                conn = psycopg2.connect(
                    host="127.0.0.1",
                    port=5433,
                    user=SERVER["db_user"],
                    password=SERVER["db_password"],
                    dbname=db
                )
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(QUERY)
                    results[db] = cur.fetchall()
                conn.close()
            except Exception as e:
                results[db] = f"Error: {e}"
    return results

def main():
    print(f"Connecting to {SERVER['ssh_host']} via SSH...")
    data = fetch_data()
    for db, result in data.items():
        print(f"\n-- Database: {db} --")
        if isinstance(result, str):
            print(result)
        else:
            for row in result:
                print(row)

if __name__ == "__main__":
    main()
