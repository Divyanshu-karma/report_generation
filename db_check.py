import json
import psycopg2
from psycopg2.extras import RealDictCursor

# Your Azure Database connection string
DATABASE_URL = "..."

try:
    # Connect to the DB
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Enforce UTF8 handling
    cursor.execute("SET client_encoding TO 'UTF8';")
    
    # Execute query
    target_id = '2f35deda275945ef864c1bca9a05564c'
    query = "SELECT * FROM rou_matches WHERE result_id = %s;"
    cursor.execute(query, (target_id,))
    
    rows = cursor.fetchall()
    
    if rows:
        import os, re
        output_dir = "analysed_rou_db"
        os.makedirs(output_dir, exist_ok=True)
        max_num = 0
        for filename in os.listdir(output_dir):
            match = re.match(r"match_output_(\d+)\.json", filename)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
        next_num = max_num + 1
        out_file = os.path.join(output_dir, f"match_output_{next_num}.json")
        
        print(f"Found {len(rows)} match records. Writing data to {out_file}...")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=4, default=str)
        print(f"Success! Open '{out_file}' to review your data comfortably.")
    else:
        print("No matching records found for that ID.")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'conn' in locals():
        cursor.close()
        conn.close()
