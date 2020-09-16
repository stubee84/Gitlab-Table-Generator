import pandas as pd, csv
from . import config
from io import StringIO

class csv_to_gitlab_table:
    def __init__(self, file = None, string: str = '', query: str = '', url_info: list = [], conn_string: str = '', limit: list = [], strip_char: str = ''):
        self.string = string
        self.file = file
        self.query = query
        self.url_info = url_info
        self.conn_string = conn_string
        self.strip_char = strip_char
        self.input = ""

        if limit != []:
            self.limit = limit

        if self.file != None:
            self.output = self.convert_csv_file()
            self.set_input_data()
        elif self.string != '':
            self.output = self.convert_csv_string()
            self.input = self.string
        elif self.query != '':
            self.output = self.sql_to_gitlab_table()
            self.input = self.query
        elif self.url_info != []:
            self.url = url_info[0]
            self.table_name = url_info[1]
            self.output = self.convert_html_to_string()
    
    def convert_csv_file(self) -> str:
        df = pd.read_csv(filepath_or_buffer=self.file, nrows=self.limit[len(self.limit)-1])
        
        return self.dict_to_string(df=df)
    
    def dict_to_string(self, df: pd.DataFrame) -> str:
        d = df.to_dict()
        #headers/columns
        string = '|' + ''.join([f' {key} |' for key in d.keys()]) +'\n'
        
        #row splitting headers from records
        string += '|' + ' ------ |'*(len(d.keys())) + '\n'

        for i in range(len(df.values)):
            if i >= self.limit[0]:
                records = []
                for key in d.keys():
                    records.append(d[key][i])
                string += '|' + ''.join([f' {record} |' for record in records]) + '\n'

        return string.rstrip('|').strip(' ').rstrip('\n')
    
    def convert_csv_string(self) -> str:
        csv_string = self.string.split('\n')
        headers = csv_string[0].split(',')

        string = '|' + ''.join([f' {header.strip(f" {self.strip_char}")} |' for header in headers]) +'\n'
        string += '|' + ' ------ |'*(len(headers)) + '\n |'

        csv_string.pop(0)

        for i in range(self.limit[len(self.limit)-1]):
            if i >= self.limit[0]:
                rows = csv_string[i].split(',')
                line = []
                for row in rows:
                    line.append(row.strip(f" {self.strip_char}"))
            
                string += ''.join([f' {l} |' for l in line]) + '\n |'
        
        #strip extra | from end of string, strip space, and strip extra newline at end of the string
        return string.rstrip('|').strip(' ').rstrip('\n')
    
    def convert_html_to_string(self) -> str:
        if self.url != '':
            table = self.get_html_table(input=self.url, match=self.table_name)
        
        headers = table.columns.tolist()
        string = '| ' + ' | '.join(headers) + ' |\n'
        string += '|' + ' ------ |'*(len(headers)) + '\n'

        if self.limit[len(self.limit)-1] > len(table):
            self.limit[len(self.limit)-1] = len(table)
        for i in range(self.limit[len(self.limit)-1]):
            string += '|'
            for header in headers:
                string += ' ' + str(table[header][i]) + ' |'
            string += '\n'

        return string
    
    def get_html_table(self, input: str = '', match: str = '') -> pd.DataFrame:
        table = pd.read_html(io=input, match=match)
        df = table[0]

        self.input = df.to_html()
        return df
    
    def sql_to_gitlab_table(self) -> str:
        db = config.database(query=self.query, connection_string=self.conn_string, limit=self.limit)

        df = db.query_database()

        if type(df) == str:
            return {"failure":df}
        
        return self.dict_to_string(df=df)
    
    #sets the input data string to the limit size for entry into the db
    def set_input_data(self) -> str:
        count = 0    
                
        for record in self.file.getvalue().split('\n'):
            if count == 0:
                header = record
                self.input = header + '\n'
            elif count > self.limit[0] and count <= self.limit[len(self.limit)-1]:
                self.input += record + '\n'
            elif count > self.limit[len(self.limit)-1]:
                break
            count += 1
        self.input.rstrip('\n')

if __name__ == "__main__":
    # csv_to_gitlab_table(file=file)
    # csv_to_gitlab_table(string=string, strip_char='\'')
    pass