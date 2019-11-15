import pandas as pd

db = pd.read_excel('SMART Grade VZW GRR Device List.xlsx', sheet_name='GRR 117')
db.to_json(orient='records', path_or_buf='vzw.json')
