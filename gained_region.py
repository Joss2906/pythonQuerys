import pandas as pd
from database import Connection as db_conn
import sys
import os


def main():
    database = 'northwind'
    conn = db_conn(database)
    result = gained_region(conn)
    print(result)
    conn.close()

    #export to excel file
    output_path = os.path.join(os.path.dirname(__file__), 'gained_x_region.xlsx')
    result.to_excel(output_path, index=False)


def gained_region(conn):
    qry_orders = "SELECT * FROM orders"
    qry_oDetails = "SELECT * FROM `order details`"
    qry_region = "SELECT * FROM region"
    qry_terr = "SELECT * FROM territories"
    qry_emp_terr = "SELECT * FROM employeeterritories"

    #SUBQUERY
    terr = conn.fetch_dataframe(qry_terr)
    emp_terr = conn.fetch_dataframe(qry_emp_terr)
    region = conn.fetch_dataframe(qry_region)

    join = pd.merge(region, terr, on='RegionID', how='inner')
    join = pd.merge(join, emp_terr, on='TerritoryID', how='inner')
    final_sub = join[['EmployeeID', 'RegionID', 'RegionDescription']].drop_duplicates().sort_values(by=['EmployeeID', 'RegionID'])

    #QUERY
    orders = conn.fetch_dataframe(qry_orders)
    oDetails = conn.fetch_dataframe(qry_oDetails)

    final_join = pd.merge(orders, oDetails, on='OrderID', how='inner')
    final_join = pd.merge(final_join, final_sub, on='EmployeeID', how='inner')

    final_join['Total'] = final_join['UnitPrice'] * final_join['Quantity']
    gained_region = final_join.groupby(['RegionID','RegionDescription'], as_index=False).agg({'Total': 'sum'})
    gained_region = gained_region[['RegionID', 'RegionDescription', 'Total']].sort_values(by='RegionID')

    return gained_region
    