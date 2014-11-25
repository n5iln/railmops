'''
Railroad Class

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    15/08/2010 Ver 1 Unused variables removed
'''

import MOPS_Element


class cRailroads(MOPS_Element.cElement):
    """details about railroads.  railroads define geographical stretches of lines and are
    subsequently subdivided into areas.  railroads are also the owners of locos and cars
    """
    extract_code = 'select * from railroad'
    extract_header = 'id|rail|railroad_name\n'



    def adrail(self, message):
        """add a new railroad code and name.  the railroad code cannot already exist
        """
        if self.show_access(message, 'ADRAIL railroad;railroad name', 'S') != 0:
            return

        #railroad code------------------------------------------------------------------------------
        railroad, rc = self.extract_field(message, 0, 'RAILROAD')
        if rc > 0:
            return
        
        if len(railroad) > self.railsize:
            print('* RAILROAD CODE ENTERED IS GREATER THAN THE ALLOWED SIZE')
            return
        
        if len(railroad) ==0:
            print('* NO RAILROAD CODE ENTERED: A BLANK CODE IS NOT ALLOWED')
            return
        
        #check it does not already exist on the database--------------------------------------------
        data = (railroad,)
        sql = 'select id from railroad where railroad = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* RAILROAD CODE ALREADY EXISTS')
            return

        #railroad name------------------------------------------------------------------------------
        railroad_name, rc = self.extract_field(message, 1, 'RAILROAD NAME')
        if rc > 0:
            return

        #carry out the update-----------------------------------------------------------------------
        data = (railroad, railroad_name)
        sql = 'insert into railroad values (null, ?, ?)'
        if self.db_update(sql, data) != 0:
            return

        print('NEW RAILROAD ADDED SUCCESSFULLY')
        print(railroad + railroad_name)
        return 
        


    def chrail(self, message):
        """change railroad name
        """
        if self.show_access(message, 'railroad;railroad name', 'S') != 0:
            return

        #railroad code------------------------------------------------------------------------------
        railroad, rc = self.extract_field(message, 0, 'RAILROAD')
        if rc > 0:
            return
        
        #read the database and populate the fields--------------------------------------------------
        data = (railroad,)
        sql = 'select name from railroad where railroad = ?'
        count, ds_railroads = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* RAILROAD CODE DOES NOT EXIST')
            return

        for row in ds_railroads:
            railroad_name = row[0]

        #railroad name------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            railroad_name = value

        #carry out the update-----------------------------------------------------------------------
        data = (railroad_name, railroad)
        sql = 'update railroad set name = ? where railroad = ?'
        if self.db_update(sql, data) != 0:
            return

        print('RAILROAD NAME CHANGED SUCCESSFULLY')
        print(railroad + railroad_name)
        return 



    def dxrail (self, message):
        """deletes a railroad entry from the database.  validates that there are no areas, locos
        or cars attached to the railroad prior to deletion
        """
        if self.show_access(message, 'DXRAIL railroad', 'S') != 0:
            return

        #railroad code------------------------------------------------------------------------------
        railroad, rc = self.extract_field(message, 0, 'RAILROAD')
        if rc > 0:
            return
        data = (railroad,)
        
        #validate the change - check there is a record to delete------------------------------------
        sql = 'select id from railroad where railroad = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* RAILROAD CODE DOES NOT EXIST')
            return
            
        #make sure that there is not an area linked to the railroad---------------------------------
        sql = 'select id from area where railroad = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* AREAS ARE LINKED TO THIS RAILROAD: DELETE CANCELLED')
            return

        #make sure that there is not a loco linked to the railroad----------------------------------
        sql = 'select id from locomotive where railroad = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* LOCOMOTIVES ARE OWNED BY THIS RAILROAD: DELETE CANCELLED')
            return

        #make sure that there is not a car linked to the railroad-----------------------------------
        sql = 'select id from car where railroad = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* CARS ARE OWNED BY THIS RAILROAD: DELETE CANCELLED')
            return

        #process the change-------------------------------------------------------------------------
        if self.db_update('delete from railroad where railroad = ?', data) != 0:
            return
        print('RAILROAD' + railroad + 'SUCCESSFULLY DELETED')
        return


    
    def lirail(self, message):
        """list railroads plus associated info to the screen.  this information is sortable by
        name or code.  
        """
        if self.show_access(message, 'LIRAIL (sort[0/1])', 'R') != 0:
            return

        #sort code----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 0, 'SORT CODE')
        if rc == 0:
            sortcode = value
        else:
            sortcode = '0'
        
        # build the column titles-------------------------------------------------------------------
        titles = self.x_field('RAIL====', self.railsize) + ' '  + \
                 self.x_field('NAME==========================', 30) 
        
        # get the extract data----------------------------------------------------------------------
        if sortcode == '1':
            sql = 'select railroad, name from railroad order by name'
        else:
            sql = 'select railroad, name from railroad order by railroad'

        count, ds_railroads = self.db_read(sql, '')
        if count < 0:
            return
        
        #report the extracted data------------------------------------------------------------------
        line_count = 0
        for row in ds_railroads:
            if line_count == 0:
                print(titles)
            print(self.x_field(row[0], self.railsize) + " " +
                   self.x_field(row[1], 30))
            line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break
        print(' ** END OF DATA:' + str(count) + ' RECORDS DISPLAYED **')         
        return
    


    def prrail(self, message, Params):
        """print railroad details to a file, sortable by either code or name.  also
        includes a count of areas, locos and cars attached to the railroad.
        """
        if self.show_access(message, 'PRRAIL (sort[0/1])', 'R') != 0:
            return

        #sort code----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 0, 'SORT CODE')
        if rc == 0:
            sortcode = value
        else:
            sortcode = '0'
        #TODO: sort code showing up as being required
        
        # build the column titles-------------------------------------------------------------------
        titles = self.x_field('RAIL====', self.railsize) + ' '       +\
                 self.x_field('NAME==========================', 30) + ' ' +\
                 self.x_field('AREAS=', 6) + ' ' +\
                 self.x_field('LOCOS=', 6) + ' ' +\
                 self.x_field('CARS==', 6)

        # get the extract data----------------------------------------------------------------------
        if sortcode == '1':
            sql = 'select railroad, name from railroad order by name'
            report_desc = 'LIST OF RAILROADS SORTED BY RAILROAD NAME'
        else:
            sql = 'select railroad, name from railroad order by railroad'
            report_desc = 'LIST OF RAILROADS SORTED BY RAILROAD CODE'

        count, ds_railroads = self.db_read(sql, '')
        if count < 0:
            return
        
        #build the extracted data-------------------------------------------------------------------
        self.temp = {}

        for row in ds_railroads:
            data = (row[0],)
            sql = 'select id from area where railroad = ?'
            areas_count, dummy = self.db_read(sql, data)
            sql = 'select id from locomotive where railroad = ?'
            locos_count, dummy = self.db_read(sql, data)
            sql = 'select id from car where railroad = ?'
            cars_count, dummy = self.db_read(sql, data)
            print_line = self.x_field(row[0], self.railsize)  + ' ' +\
                         self.x_field(row[1], 30)             + ' ' +\
                         self.x_field(str(areas_count), 6, 'R') + ' ' +\
                         self.x_field(str(locos_count), 6, 'R') + ' ' +\
                         self.x_field(str(cars_count), 6, 'R')
            if message == '1':
                self.temp[row[1]] = print_line
            else:
                self.temp[row[0]] = print_line

        #report the extracted data -----------------------------------------------------------------
        self.print_report (titles      = titles,
                           report_id   = 'PRRAIL',
                           report_name = report_desc,
                           Params      = Params)
        return
