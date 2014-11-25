'''
Car Class: General Car grouping for type of car

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    15/08/2010 Ver 1 Populate class name correctly on amend (if left blank) 
'''

import MOPS_Element

class cCarClasses(MOPS_Element.cElement):
    """details about car classes.  car classes define major groupings of cars.  car classes are
    used by warehouses and car types; and are copied down to cars themselves
    """
    extract_code = 'select * from carclass'
    extract_header = 'id|code|description'



    def adclas(self, message):
        """add a new car class and name to the system
        """
        if self.show_access(message, 'ADCLAS class;class name', 'S') != 0:
            return

        #car class code-----------------------------------------------------------------------------
        carclass, rc = self.extract_field(message, 0, 'CAR CLASS')
        if rc > 0:
            return

        if len(carclass) > self.classize:
            print('* CAR CLASS CODE ENTERED IS GREATER THAN THE ALLOWED SIZE')
            return
        
        if len(carclass) ==0:
            print('* NO CAR CLASS CODE ENTERED: A BLANK CODE IS NOT ALLOWED')
            return
        
        #check it does not already exist on the database
        data = (carclass,)
        sql = 'select id from carclass where carclass = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* CAR CLASS CODE ALREADY EXISTS')
            return

        #car class name-----------------------------------------------------------------------------
        class_name, rc = self.extract_field(message, 1, 'CAR CLASS NAME')
        
        if rc > 0:
            return

        #carry out the update-----------------------------------------------------------------------
        data = (carclass, class_name)
        sql = 'insert into carclass values (null, ?, ?)'
        if self.db_update(sql, data) != 0:
            return
        print('NEW CAR CLASS ADDED SUCCESSFULLY')
        print(carclass + class_name)
        return



    def chclas(self, message):
        """change the name on a car class
        """
        if self.show_access(message, 'CHCLAS class;class name', 'S') != 0:
            return

        #car class code-----------------------------------------------------------------------------
        carclass, rc = self.extract_field(message, 0, 'CAR CLASS')
        if rc > 0:
            return

        #read the database and populate the fields
        data = (carclass,)
        sql = 'select name from carclass where carclass = ?'
        count, ds_classes = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* CAR CLASS CODE DOES NOT EXIST')
            return
        
        for row in ds_classes:
            class_name = row[0]

        #car class name-----------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, 'CAR CLASS NAME')
        if rc > 0:
            return
        if rc == 0:                                                          # Ver 1
            class_name = value

        #carry out the update-----------------------------------------------------------------------
        data = (class_name, carclass)
        sql = 'update carclass set name = ? where carclass = ?'
        if self.db_update(sql, data) != 0:
            return
        print('CAR CLASS NAME CHANGED SUCCESSFULLY')
        print(carclass + class_name)
        return

    

    def dxclas(self, message):
        """Deletes a car class entry from the list.  Validates that there are no
        car types entries with that value prior to deletion
        """
        if self.show_access(message, 'DXCLAS class', 'S') != 0:
            return

        #car class code-----------------------------------------------------------------------------
        carclass, rc = self.extract_field(message, 0, 'CAR CLASS')
        if rc > 0:
            return
        data = (carclass,)
        
        #validate the change - check there is a record to delete
        sql = 'select id from carclass where carclass = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* CAR CLASS CODE DOES NOT EXIST')
            return
        
        #make sure that there is not a car type linked to the car class-----------------------------
        sql = 'select id from cartype where carclass = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* CAR TYPES ARE ATTACHED TO THIS CLASS - CANNOT DELETE')
            return

        #make sure that there is not a warehouse linked to the car class----------------------------
        sql = 'select id from warehouse where threshold_class = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* WAREHOUSES ARE ATTACHED TO THIS CLASS - CANNOT DELETE')
            return

        #process the change-------------------------------------------------------------------------
        if self.db_update('delete from carclass where carclass = ?', data) == 0:
            print('CAR CLASS ' + carclass + ' SUCCESSFULLY DELETED')
        return



    def liclas(self, message):
        """list classes to the screen sortable by code or name
        """
        if self.show_access(message, 'LICLAS (sort[0/1])', 'R') != 0:
            return        

        #status
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = ''

        # build the column titles
        titles = self.x_field('CLASS=====', self.classize) + ' ' +\
                 self.x_field('NAME==========================', 30)
       
        #get the extract data
        if sort_order == '1':
            sql = 'select carclass, name from carclass order by carclass'
        else:
            sql = 'select carclass, name from carclass order by name'

        count, ds_classes = self.db_read(sql, '')
        if count < 0:
            return

        #report the extracted data
        line_count = 0
        for row in ds_classes:
            if line_count == 0:
                print(titles)
            print(self.x_field(row[0], self.classize) + " " +
                   self.x_field(row[1], 30))
            line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break
        print(' ** END OF DATA: ' + str(count) + ' RECORDS DISPLAYED **')         
        return



    def prclas(self, message, Params):
        """report classes to a file sortable by name or code
        """
        if self.show_access(message, 'PRCLAS (sort[0/1])', 'R') != 0:
            return        

        #status
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = ''

        # build the column titles
        titles = self.x_field('CLASS=====', self.classize) + ' ' +\
                 self.x_field('NAME==========================', 30)
       
        #get the extract data
        if sort_order == '1':
            sql = 'select carclass, name from carclass order by carclass'
        else:
            sql = 'select carclass, name from carclass order by name'

        count, ds_classes = self.db_read(sql, '')
        if count < 0:
            return

        #report the extracted data
        self.temp = {}

        for row in ds_classes:
            print_line = self.x_field(row[0], self.classize) + ' '  +\
                   self.x_field(row[1], 30)
            if sort_order == '1':
                self.temp[row[1]] = print_line
            else:
                self.temp[row[0]] = print_line

        #extracted data sent to printer
        self.print_report (titles = titles,
                           report_id = 'PRCLAS',
                           report_name = 'LIST OF CAR CLASSES',
                           Params = Params)
        return
