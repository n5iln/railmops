'''
Railroad Class

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    Rev 1 Unused variables removed
          Database error handled in extract_to_file
          Tidied creation of print numbers
    1.02  Replace Linux os.popen print routine with subprocess.Popen
			-- need to work on buffering output to printer
'''

import re
import sqlite3
import platform
#import os      ## deprecated, using subprocess instead
import subprocess

class cElement(object):
    """details about data elements.  used as a base class to handle data access objects.  
    contains some standard routines and generic variables.
    """

    def __init__(self, Params, uid, access, directory):
        """carry out some initiation as this data is common to all modules.  the data loaded
        are from the parameter file which will
        """
        self.areasize = Params.get_field_size('AREASIZE')
        self.cartsize = Params.get_field_size('CARTSIZE')
        self.carxsize = Params.get_field_size('CARXSIZE')
        self.classize = Params.get_field_size('CLASSIZE')
        self.commsize = Params.get_field_size('COMMSIZE')
        self.curosize = Params.get_field_size('CUROSIZE')
        self.loadsize = Params.get_field_size('LOADSIZE')
        self.locosize = Params.get_field_size('LOCOSIZE')
        self.loctsize = Params.get_field_size('LOCTSIZE')
        self.plaxsize = Params.get_field_size('PLAXSIZE')
        self.railsize = Params.get_field_size('RAILSIZE')
        self.routsize = Params.get_field_size('ROUTSIZE')
        self.statsize = Params.get_field_size('STATSIZE')
        self.staxsize = Params.get_field_size('STAXSIZE')
        self.schdsize = Params.get_field_size('SCHDSIZE')
        self.rr         = Params.get_rr_name()
        self.uid        = uid
        self.access     = access
        self.directory  = directory
        self.temp       = {}
        return



    def x_field(self, disp_field, size=5, justify='L'):
        """used to format fields (or column headings) to a fixed size for use on reports and listings
        """
        if isinstance(disp_field, int):
            field_a = str(disp_field)
        else:
            field_a = disp_field
        if justify == 'L':
            field_a = field_a.ljust(size)[:size]
        else:
            field_a = field_a.rjust(size)[:size]
        return field_a



    def show_access(self, message, prompt, access_required):
        """information checked/displayed at the start of a command.
        """
        if message.strip() == '?':
            print(prompt)
            return 11

        #check access required
        if access_required == 'R':
            return 0
        if self.access == access_required:
            return 0
        if self.access == 'S' and access_required == 'N':
            return 0

        if access_required == 'S':
            print('* THIS COMMAND IS FOR USERS WITH SUPERVISOR ACCESS ONLY')
        if access_required == 'N':
            print('* THIS COMMAND IS FOR USERS WITH SUPERVISOR/UPDATE ACCESS ONLY')
        return 22



    def extract_field(self, message, position, field_name):
        """strips data from a message and validates that it is readable
        """
        details = re.split('\;', message)
        try:
            field = details[position].strip()
        except:
            if field_name != '':
                print('* CANNOT DETERMINE ' + field_name + '- CHECK DATA AND DELIMITERS')
            return '', 99
        if field == '' and field_name != '':
            print('*' + field_name + ' MUST BE PROVIDED')    
            return '', 98
        if field == '' and field_name == '':
            return '', 1
        return field, 0
        
        
        
    def db_update(self, sql, data):
        """general sql update routine.  creates a connection to the database, updates the database
        using the sql, and then releases the connection (stays in the database as short as possible).
        returns a non-zero value if the update failed
        """
        try:
            cxn_up = sqlite3.connect(self.directory + 'mops.db')
            c_up = cxn_up.cursor()
            c_up.execute(sql, data)
            cxn_up.commit()               
        except:
            print('* ERROR UPDATING DATA: REPORT DETAILS TO SYSTEM ADMINISTRATOR ***************')
            print('#    sql:' + str(sql))
            print('#   data:' + str(data))
            return 99
        c_up.close()
        cxn_up.close()
        return 0
        


    def db_read(self, sql, data):
        """general sql reader.  creates the connection, gets the dataset of data then drops the
        connection again.  returns a count of records obtained and a dataset.  if there is an error
        with the access then teh count is set to -1
        """
        empty_array = ()
        try:
            cxn = sqlite3.connect(self.directory + 'mops.db')
            c = cxn.cursor()
            try:
                c.execute(sql, data)
                array = c.fetchall()
            except:
                print('* ERROR READING DATA: REPORT DETAILS TO SYSTEM ADMINISTRATOR ***************')
                print('#    sql:' + sql)
                print('#   data:' + data)
                c.close()
                cxn.close()
                return -1, empty_array
        except:
            print('* ERROR ACCESSING DATABASE: REPORT DETAILS TO SYSTEM ADMINISTRATOR ***************')
            print('#    sql:' + sql)
            print('#   data:' + data)
            return -1, empty_array
        c.close()
        cxn.close()

        counter = len(array)
        return counter, array



    def print_report(self, titles, report_id, report_name, Params):
        """Sends a given report to a printer.  The titles, data etc will be provided, this module
        deals with packaging it all together and sending it to the printer
        """
        #initialise all the counters etc used in the routine
        space = ' '
        page_no = 0
        line_no = 0

        # get print reference number and open the file for printing
        print_num = Params.get_inc('PRINTS')                         #Rev 1
        print_num_str = str(print_num)
        print_num_str = print_num_str.rjust(4,'0')
        filename = self.directory + 'MOPS_EXTRACT_' + print_num_str + '.txt'
        file_handle = open (filename, "w")

        # work out the offset for the print line.  this can be got from the titles
        offset = (space * int(( 80 - len(titles) ) / 2))

        suppress_titles = False
        if report_id == 'PRCONS':
            suppress_titles = True
        #process the data. this includes printing page and column headers
        data_sort = list(self.temp.keys())
        data_sort.sort()
        for x in data_sort:
            if line_no == 0:
                page_no = page_no + 1
                if page_no != 1:
                    file_handle.write ('\f')

                top_left = 'MOPS/' + report_id.ljust(10)
                top_right = str(Params.get_date()) + ' ' + str(Params.get_time())[0:5]
                print_width = len(self.rr)
                left_spacing  = space * (int((50-print_width)/2))
                right_spacing = space * (int(49 - len(left_spacing) - print_width))
                file_handle.write(top_left + left_spacing + self.rr + right_spacing + top_right + '\n')

                top_left = self.uid.ljust(10)
                top_right = 'Page:' + str(page_no).rjust(5)
                print_width = len(report_name)
                left_spacing  = space * (int((60-print_width)/2))
                right_spacing = space * (int(59 - len(left_spacing) - print_width))
                file_handle.write(top_left + left_spacing + report_name + right_spacing + top_right + '\n\n')

                if suppress_titles:
                    pass
                else:
                    file_handle.write(offset + titles + '\n\n')

            file_handle.write(offset + self.temp[x] + '\n')
            line_no = line_no + 1
            if line_no > 58:
                line_no = 0
        file_handle.write('\n\n ** END OF DATA: ' + str(len(self.temp)) + ' PRINTED **')
        file_handle.flush
        file_handle.close

        #send the report to the printer
        print( 'SENDING REPORT TO PRINTER: ')
        print(filename)
        if platform.system() == 'Windows':
            try:
                import win32api
            except:
                print('* FAILED TO LOAD WINDOWS EXTENSION')
                return
            try:
                win32api.ShellExecute (0, "print", filename, None, ".", 0)
            except:
                print('* FAILED TO SEND PRINT TO WINDOWS PRINTER')
                return
        else:
            #try:        							## deprecated routine
                #printer = os.popen('lpr', 'w')
                #f = open (filename, 'rb')
                #for line in f:
                    #printer.write (line)
                #f.close
                #printer.close()
            try:										## Rev 1.01
				command = 'lpr {0}'.format(filename)
				subprocess.Popen(command.split(),shell=False)
            except:
                print('* FAILED TO SEND PRINT TO MAC/LINUX PRINTER')
        return



    def dump_to_screen(self):
        """dump the data from the file to the screen with minimum processing.  mostly for debugging purposes.
        """
        counter, data = self.db_read(self.extract_code,'')
        for row in data:
            print(row)
        print(str(counter) + ' RECORDS ON FILE')
        return



    def extract_to_file(self, Params):
        """Dumps the contents of the railroad database file to an extract file with fields in
        delimited format for loading into a spreadsheet
        """
        #initialise used variables
        count = 0
        print_num = Params.get_inc('PRINTS')                         #Rev 1
        print_num_str = str(print_num)
        print_num_str = print_num_str.rjust(4,'0')

        #open the file for printing
        filer = self.directory + 'MOPS_EXTRACT_' + print_num_str + '.txt'
        try:
            filex = open (filer, "w")
        except:
            print('* FAILED TO OPEN FILE FOR PRINTING')
            return
        print('UNFORMATTED REPORT: ' + filer)
        filex.write(self.extract_header)
        counter, data = self.db_read(self.extract_code,'')
        if counter < 0:                                                     #Rev 1
            return
        for row in data:
            output = ''
            for index in range(len(row)):
                output = output + str(row[index]) + '|'
            count  = count + 1
            filex.write(output + '\n')
        filex.write ('END OF DATA: ' + str(count) + ' LINES DISPLAYED')
        filex.flush()
        filex.close
        print('EXTRACT CREATED')
        return
            
