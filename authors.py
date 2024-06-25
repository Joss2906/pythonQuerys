# import pandas as pd
import pandas as pd
from database import Connection as db_conn
import sys
import os



#     from pandas import pandas as pd
#     from database import Connection as db_conn
    

def main():
    database1 = 'pubs'
    database2 = 'northwind'
    
    conn = db_conn(database1)
    df = gained_per_author(conn)
    print(df)

    conn.close()


def gained_per_author(conn):
    qry_titileauthor = "SELECT * FROM titleauthor"
    qry_titles = "SELECT * FROM titles"
    qry_sales = "SELECT * FROM sales"

    # conn.execute_query(qry_titileauthor)
    titileauthor = conn.fetch_dataframe(qry_titileauthor)
    titles = conn.fetch_dataframe(qry_titles)
    sales = conn.fetch_dataframe(qry_sales)

    #FIRST SUBQUERY -> get all authors and royalties
    join = pd.merge(titileauthor, titles, on='title_id', how='right')
    anon_authors = join.groupby('title_id', as_index=False).agg({'royaltyper': 'sum'})
    
    anon_authors['royaltyper'] = 100 - anon_authors['royaltyper'].fillna(100)
    anon_authors['au_id'] = 'ANON'
    anon_authors['au_ord'] = '1'

    #select columns
    anon_authors = anon_authors[['au_id', 'title_id', 'au_ord', 'royaltyper']]
    #having clause
    result_anon = anon_authors[(anon_authors['royaltyper'] > 0) | (anon_authors['royaltyper'].isna())]
    #union with titleauthor
    all_authors = pd.concat([titileauthor, result_anon], axis=0)
    


    #SECOND SUBQUERY -> get all sales and royalties
    #join with sales
    join_author = pd.merge(all_authors, sales, on='title_id', how='right')
    #join with titles
    join_titles = pd.merge(join_author, titles, on='title_id', how='inner')
    #calculate gained
    join_titles['gained'] = join_titles['qty'] * join_titles['price'] * (join_titles['royaltyper'] / 100)
    gained_x_author = join_titles.groupby(['au_id'], as_index=False).agg({'gained': 'sum'})
    gained_x_author = gained_x_author[['au_id', 'gained']]
    
    #export to excel file
    output_path = os.path.join(os.path.dirname(__file__), 'gained_x_author.xlsx')
    gained_x_author.to_excel(output_path, index=False)



    # print(join)
    # result = gained_x_author

    return gained_x_author


if __name__ == "__authors__":
    main()

