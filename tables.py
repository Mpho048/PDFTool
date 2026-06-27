import pandas as pd 
from play_pdf import PDFTool


#Name of the PDF
pdf_name = "page_5.pdf"


#Read PDF file
pdf = PDFTool(pdf_name)


#Read tables and show each page
tables = pdf.extract_tables()
print("Tables:")
for table in tables:
    print(table)
    print()
 
    
#save the first table and second  table to a sql database     
df_1 = pd.DataFrame(tables[0][1:],columns = tables[0][0])
df_2 = pd.DataFrame(tables[1][1:],columns = tables[1][0])
pdf.df_to_sql(df = df_1,db_name = "example.db",table_name = "table1") 

pdf.df_to_sql(df = df_2 ,db_name = "example.db", table_name = "table2")

#Save third table to a csv file
df_3 = pd.DataFrame(tables[2][1:],columns = tables[2][0])
df_3.to_csv("tables3.csv",index = False)

#Save the fourth table to excel file
if len(tables) > 3:
        df_4 = pd.DataFrame(
        tables[3][1:],
        columns=tables[3][0]
    )


df_4.to_excel("table4.xlsx",index = False )


#Combine all the tables
def merge_tables(tables):
    all_rows = []
    for table in tables:
        for row in table:
            # Check if this specific row is already added
            if row not in all_rows:
                all_rows.append(row)
    return all_rows

# Print the results row by row
print("All table with one column:")
for row in merge_tables(tables):
    print(row)
    print()

   