import sqlite3

conn = sqlite3.connect('db/auction.db')
conn.execute('ALTER TABLE lots ADD COLUMN end_date DATETIME')
conn.commit()
conn.close()
print('Done')