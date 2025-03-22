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
SELECT 'Chart of Accounts', COUNT(*), TO_CHAR(MAX(create_date), 'DD Mon YYYY') FROM account_account WHERE create_uid IS NOT NULL AND create_uid NOT IN (SELECT id FROM res_users WHERE login IN ('admin', '__system__'));
