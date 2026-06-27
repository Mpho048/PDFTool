import pandas as pd 
from play_pdf import PDFTool

#PDF file name
pdf_name = "business_data_tables.pdf"

#Read the PDF file
pdf = PDFTool(pdf_name)

#Extract the 2 page table
tables = pdf.extract_multi_table(start_page = 1,end_page = 2)
print("All of the table data:")
for table in tables:
    print(table)
    print()
    
    
#Make the table into a dataframe
df = pd.DataFrame(tables[1:],columns = tables[0]) 
print("\nDataFrame:")
print(df)

#Clean the DataFrame
df["Growth %"] = pd.to_numeric(df["Growth %"])

df["ID"] = pd.to_numeric(df["ID"])


def clean_numeric(df, columns):

    for col in columns:
        df[col] = (
            df[col]
            .str.replace(",", "", regex=False)
        )

        df[col] = pd.to_numeric(df[col])

    return df
    
df = clean_numeric(df,["Revenue ($)","Expenses ($)","Profit ($)"])    

print("DataFrame info:")
df.info()