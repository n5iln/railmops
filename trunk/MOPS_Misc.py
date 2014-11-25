'''
Misc: Contains a set of utility commands for MOPS

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    31/07/2010 Ver 1.  Stripped trailing chars from line feed from MOPSLocation
    13/08/2010 Ver 1.  Deprecated routines removed.  Unused variable removed


'''

import time
import os
import re
import platform


def directory_location():
    """directory_location  
    Looks for a file in the home directory which contains a name for the 
    data directory.  There should be one line in this file, which will point 
    to the location of the directory in which all other data files will be 
    found. Various checks - can we open the file; 
                            is it formatted correctly; 
                            does the directory exist (can we list it)?
    Return - Success - data directory location (Failure - *****)
    """ 
    try:
        i = 0
        f = open('MOPSLocation.txt', 'r')
        for line in f:
            mops_location = line.strip()
            i = i + 1
        f.close
        if i != 1:
            fatal_error(2)
            return '*****'
    except IOError:
        fatal_error(1)
        return '*****'
    finally:
        try:
            dummy = os.listdir(mops_location)
            return mops_location
        except:
            fatal_error(3)
            return '*****'



def fatal_error(cause):
    """fatal_error  
    Fatal error process - message and shut down. In the event of a 
    fatal error when starting up, display the appropriate messages, wait, 
    then shut down.
    """
    print('*********************************************************************')
    print('* FATAL ERROR                                                       *')
    print('*  There should be a file in the same directory as this application *')
    print('*  called MOPSLocation.txt. This file should contain a single line  *')
    print('*  pointing to the directory containing the data.                   *')
    print('*                                                                   *')
    print('*  You are seeing this message because:                             *')
    if cause == 1:
        print('*    - the file (MOPSLocation.txt) does not exist or                *')
        print('*    - the file with the directory is not in the correct place; it  *')
        print('*      should be in the same place as this application              *')
    if cause == 2:
        print('*    - the file is not correctly formatted - it should contain a    *')
        print('*      single line, the directory where the MOPS data resides       *')
    if cause == 3:
        print('*    - the MOPS directory does not exist (in which case the empty   *')
        print('*      directory should be created manually prior to running MOPS   *')
    print('*                                                                   *')
    print('*  Please check the above and re-run MOPS                           *')  
    print('*********************************************************************')
    print('')
    print('... this screen will close automatically ...')
    time.sleep(4)

    
    
def centre_print(move_it, width):
    """centre_print
    Centres a heading on a defined length
        Inputs  - string to centre
                - width to centre on
        Returns - justified field
    """
    print('centre_print - depracated routine')
    print_width = len(move_it)
    left_margin = (width-print_width) / 2
    left_margin = left_margin + print_width
    new_it = move_it.rjust(int(left_margin), ' ')
    new_it = new_it.ljust(width)
    return new_it



def print_header(filex, print_name, title, userid, pageno, rrname, titles, datetime):
    """print_header
    provides a print heading utility to make all output consistent
        Inputs  - file object (filename) to print to
                - short code for print name
                - title of print
                - userid of person requesting print
                - page number being printed
                - name of railroad
                - column titles
    """
    print('print_header - depracated routine')
    top_left = 'MOPS / ' + print_name.ljust(8)
    top_right = datetime
    top_mid = centre_print(rrname, 50)
    filex.write(top_left + top_mid + top_right + '\n')

    top_left = userid.ljust(10)
    top_right = 'Page ' + str(pageno).ljust(5)
    top_mid = centre_print(title, 60)
    filex.write(top_left + top_mid + top_right + '\n\n')

    filex.write(titles + '\n\n')
    return



def print_file(filename):
    """print_file
    Prints a given file out to the default printer.  Detect whether we are 
    running Windows or a Unix variant and processes accordingly.  All output
    should be to a file first and to use this utility to print the extract.
    For windows we need the win32api module in the same directory as the code
    """
    print('print_file - depracated routine')
    print( 'SENDING REPORT TO PRINTER: ' + filename)
    if platform.system() == 'Windows':
        try:
            import win32api
        except:
            print('* FAILED TO LOAD WINDOWS EXTENSION')
            return
        try:
            print('TEST - NOT going to execute win32api') 
            win32api.ShellExecute (0, "print", filename, None, ".", 0)
        except:
            print('* FAILED TO SEND PRINT TO WINDOWS PRINTER')
            return
    else:
        try:        
            printer = os.popen('lpr', 'w')
            f = open (filename, 'rb')
            for line in f:
                printer.write (line)
            f.close
            printer.close()
        except:
            print('* FAILED TO SEND PRINT TO MAC/LINUX PRINTER')
    return



def format_data(raw_data='', position=0, size=10, mode='change', original_value=''):
    """takes data from a raw string to validate and format.  string is returned
    as a tuple; first element is the validity of the string (0=valid, 1=invalid)
    and the second element is the returned, formatted vaue (if good).
    If inserting in Change mode, then an empty raw data element will return the
    original value indicated.  Any other value won't use a previous version  
    """
    print('format_data - depracated routine')
    details = re.split('\;', raw_data)
    rc = 0
    value = ''
    nposition=int(position)
    nsize = int(size)

    if mode != 'new':
        try:
            if details[nposition] == '': 
                value = original_value
            else:
                value = details[nposition].ljust(nsize)[:nsize]
        except IndexError:
            value = original_value
        except:
            rc = 99
            value = 'NOT KNOWN'

    if mode == 'new':
        try:
            value = details[nposition].ljust(nsize)[:nsize]
        except:
            rc = 99
            value = 'NOT KNOWN'

    if isinstance(value, int):
        pass
    else:
        value = value.strip()
    return rc, value



def get_file_object(directory, Params):
    """returns a file object for printing
    """
    print('get_file_object - depracated routine')
    print_num = Params.get_inc('PRINTS')
    print_num_str = print_num.rjust(4,'0')
    filer = directory + 'MOPS_EXTRACT_' + print_num_str + '.txt'
    return filer



def print_list(data, titles, filex, report_id, report_name, userid, rr_name, datetime):
    """takes a dictionary list that has been previously built with the sort values in
    the key and te printable lines in the value
    """
    print('print_list - depracated routine')
    page_no = 0
    line_no = 0
    
    data_sort = list(data.keys())
    data_sort.sort()

    for x in data_sort:
        if line_no == 0:
            page_no = page_no + 1
            if page_no != 1:
                filex.write ('\f')
            print_header(filex, report_id, report_name, userid, page_no, rr_name, titles, datetime)
        filex.write(data[x] + '\n')
        line_no = line_no + 1
        if line_no > 55:
            line_no = 0
    filex.write('\n\n ** END OF DATA: ' + str(len(data)) + ' PRINTED **')
    filex.flush
    return
