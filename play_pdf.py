import os
import pandas as pd 
from pypdf import PdfReader,PdfWriter 
import sqlite3 as sql
import pandas as pd 
import pdfplumber as plb


class PDFTool:
    """
    PDF utility class:
    - Extract tables
    - Extract multi-page tables
    - Extract table by area
    - Merge PDFs
    - Insert pages
    - Split PDFs
    """    
    def __init__(self,filepath = None) :
        self.filepath = None
        if filepath:
            self.filepath = self._valid_path(filepath)


    def _valid_path(self,path):
        """Validate path exists and is string.
        Args:
            path:str
        """
                
        if not isinstance(path,str):
            raise TypeError("Path must be a string(text)")
        if  not os.path.exists(path):
                raise FileNotFoundError(f"{path} does not exist")
        return path

    def update_filepath(self,new_path):
        """Input a new file path:
            Args:
                new_path(str)"""
        self.filepath = self._valid_path(new_path)

    def _check_file(self):
        """Ensure working file exists."""
        if self.filepath is None:
            raise ValueError("No PDF filepath selected")
              

# --- pdfplumber TABLE EXTRACTION STRATEGIES ---
    def extract_table(self,page_num = 1):
        """Extracting table from pdf using tabula
        Args:
            page_num:(int / list)"""
        try:
            with plb.open(self.filepath) as f:
                page = f.pages[page_num-1]
                table = page.extract_table()
                return table if table else []
        except Exception as e:
            return f"Error: {e}"                      

                                                          
    def extract_multi_table(self,start_page,end_page):
        """ 
        Extract a table that take up two or more page and returns  a list of list
        Args
        start_page(int):
            starting page of the table
        end_page(int):
            end page of the table
        """
        combine = []
        try:
            with plb.open(self.filepath) as f:
                for p_num in range(start_page-1, end_page):
                    page = f.pages[p_num]
                    table = page.extract_table()
                    if table is None:
                        continue
                    if not combine:
                        combine.extend(table)
                    else:
                        combine.extend(table[1:])
            return  combine                  
        except Exception as e:
            return f"Error {e}" 
                                                                                                             
    def extract_tables(self, page_num=1, table_num=None):
        """
        Extract all tables or one specific table
    
        Args:
            page_num : int
            table_num : int or None
    
        Returns:
            list
        """
    
        self._check_file()
    
        try:
            with plb.open(self.filepath) as f:    
                page = f.pages[page_num-1]    
                tables = page.extract_tables()
    
                if not tables:
                    return []    
                # Return one specific table
                if table_num is not None:
    
                    if table_num < 1:
                        raise ValueError("table_num starts at 1")
    
                    if table_num > len(tables):
                        raise IndexError("Table number out of range")
    
                    return tables[table_num-1]
    
                # Return all tables
                return tables
    
        except Exception as e:
            return f"Error: {e}"                                  
                                                            
    # --- MANIPULATION METHODS (pypdf) ---
    
    def merge_pdf(self,sec_pdf,output_name,pages= None):
        """
        Merge another PDF
        Args:
        output_name:str name of the new pdf       
        sec_pdf:str path/name of the second  pdf 
        pages:
            None -> all pages
            [1,2,4]  -> selected pages      
        """
        self._check_file()
        second_pdf = self._valid_path(sec_pdf)

        if not output_name.endswith("pdf"):
            output_name += ".pdf"

        writer = PdfWriter()
        reader1 = PdfReader(self.filepath)
        reader2 = PdfReader(second_pdf)
        

        for page in reader1.pages:
            writer.add_page(page)
            
        for index, page in enumerate(reader2.pages):

            if pages is not None:

                if index not in pages:
                    continue

            writer.add_page(page)

        with open(output_name,"wb") as f:
            writer.write(f)

        return output_name
                                                    
                        
                
    def insert_pdf(self,sec_pdf,page_num,insert_index,output_name):
        """
        Insert a page into the current pdf
        Args:
        sec_pdf(str):
            name of the second pdf,                         page_num(int):
           page number of the page to Insert,
        insert_index(int):
            new page number,
        output_name(str):
            name of the pdf
        """        
        self._check_file()
        second_pdf = self._valid_path(sec_pdf)
        
        if not output_name.endswith(".pdf"):
            output_name += ".pdf"
            
        reader1 = PdfReader(self.filepath)
        writer = PdfWriter()
        reader2 = PdfReader(second_pdf)
        page_num  -= 1
        insert_index  -= 1

        if page_num >= len(reader2.pages):
            raise IndexError("Page doesn't exist")

        if insert_index > len(reader1.pages):
            raise IndexError("Invalid insert index")                     

        for page in reader1.pages:
            writer.add_page(page)
            
        writer.insert_page(reader2.pages[page_num],(insert_index))
        
        with open(output_name,"wb") as f:
            writer.write(f)

        return output_name                                                                

    def _split_all(self,output):
        reader = PdfReader(self.filepath)
        
        for i,page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            filename = os.path.join(output,f"page_{i+1}.pdf")            
            with open(filename,"wb") as f:
                writer.write(f)                 

                                  
    def split_pdf(self,output_dir = "SplitPdf",pages = "all"):
        self._check_file()
        os.makedirs(output_dir,exist_ok = True)
        
        if isinstance(pages,str) and pages.lower() == "all":
            self._split_all(output = output_dir)
            
        if isinstance(pages,list):
            reader = PdfReader(self.filepath)
            for i in pages:
                page =  i - 1
                writer = PdfWriter()
                writer.add_page(reader.pages[page])
                filename = os.path.join(output_dir,f"page_{i}.pdf")
                
                with open(filename,"wb") as f:
                    writer.write(f)
                    
        if not isinstance(pages,(str,list)):
            return "pages has to be 'all' or a list of integers"          
            
        return f"Split completed in folder: '{output_dir}'"                                                                                     
 
#========SQLITE METHODS========

    #Save to sql(database)
    def df_to_sql(self,df,db_name="data.db",table_name="pdf_table", replace = False):
        """
        save dataframe into a sql database         Args
        df (pd.DataFrame):
            pandas dataframe
        db_name(str):
            name of the database
         table_name(str):
             name of the table to save to the                 database
         replace(bool):
             default  = False
        """
        self._valid_path(db_name)
        conn = sql.connect(db_name)
        
        mode = ("replace" if replace else "append")
        
        df.to_sql(table_name,conn,if_exists = mode,index = False)
        
        conn.close()
        return  "Saved successfully"
           
        
    #Read a table from database(to df)
    def sql_to_df(self,db_name,table_name):
        """"
        Read from sql database and get a table and turn it into dataframe
        Args:
        db_name(str):
            name of database
         table_name(str):
             name of the table in the database
        """
        self._valid_path(db_name)
        conn = sql.connect(db_name)
    
        try:
            query = (
            f"SELECT *"
            f"FROM [{table_name}]"
            )
            df = pd.read_sql(query,conn)
            return df
        finally:
            conn.close()

                                           