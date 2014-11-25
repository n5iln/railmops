'''
Areas Class: Defines a territory or coverage

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.
'''

import MOPS_Element

class cAreas(MOPS_Element.cElement):
    """details about areas.  areas belong to railroads and are geographical in nature.  stations are
    linked to areas.
    """
    extract_code = 'select * from area'
    extract_header = 'id|code|name|railroad\n'



    def adarea(self, message):
        """adds an area code and name to the system.  the area must belong to a railroad
        """
        if self.show_access(message, 'ADAREA area;area name;^railroad^', 'S') != 0:
            return

        #area code----------------------------------------------------------------------------------
        area, rc = self.extract_field(message, 0, 'AREA CODE')
        if rc > 0:
            return
        
        if len(area) > self.areasize:
            print('* AREA CODE ENTERED IS GREATER THAN THE ALLOWED SIZE')
            return
        
        if len(area) == 0:
            print('* NO AREA CODE ENTERED: A BLANK CODE IS NOT ALLOWED')
            return

        #check it does not already exist------------------------------------------------------------
        data = (area,)
        sql = 'select id from area where area = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* AREA CODE ALREADY EXISTS')
            return

        #area name----------------------------------------------------------------------------------
        area_name, rc = self.extract_field(message, 1, 'AREA NAME')
        if rc > 0:
            return

        #railroad-----------------------------------------------------------------------------------
        railroad, rc = self.extract_field(message, 2, 'RAILROAD CODE')
        if rc > 0:
            return
        
        data = (railroad, )
        sql = 'select name from railroad where railroad = ?'
        count, ds_railroads = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            print('* RAILROAD CODE DOES NOT EXIST (' + railroad + ')')
            return
        else:
            for row in ds_railroads:
                railroad_name = row[0]
        
        #carry out the update and report the change-------------------------------------------------
        data = (area, area_name, railroad)
        sql = 'insert into area values (null, ?, ?, ?)'
        if self.db_update(sql, data) != 0:
            return

        print('NEW AREA ADDED SUCCESSFULLY')
        print(area + area_name + '(' + railroad + railroad_name + ')')
        return



    def charea(self, message):
        """amend the name of an area or change the railroad to which it belongs
        """
        if self.show_access(message, 'CHAREA area;(area name);(^railroad^)', 'S') != 0:
            return

        #area code----------------------------------------------------------------------------------
        area, rc = self.extract_field(message, 0, 'AREA CODE')
        if rc > 0:
            return

        #read the database--------------------------------------------------------------------------
        data = (area,)
        sql = 'select name, railroad from area where area = ?'
        count, ds_areas = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* AREA CODE DOES NOT EXIST')
            return

        for row in ds_areas:
            area_name = row[0]
            railroad  = row[1]

        #area name----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            area_name = value

        #railroad-----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            railroad = value

        data = (railroad, )
        sql = 'select name from railroad where railroad = ?'
        count, ds_railroads = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            print('* RAILROAD CODE DOES NOT EXIST (' + railroad + ')')
            return
        else:
            for row in ds_railroads:
                railroad_name = row[0]
        
        #carry out the update and report the change-------------------------------------------------
        data = (area_name, railroad, area)
        sql = 'update area set name = ?, railroad = ? where area = ?'
        if self.db_update(sql, data) != 0:
            return

        print('AREA DETAILS CHANGED SUCCESSFULLY')
        print(area + area_name + '(' + railroad + railroad_name + ')')
        return

        

    def dxarea (self, message):
        """deletes an area entry from the list.  validates that there are no stations attached to
        the area
        """
        if self.show_access(message, 'DXAREA area', 'S') != 0:
            return

        #area code----------------------------------------------------------------------------------
        area, rc = self.extract_field(message, 0, 'AREA CODE')
        if rc > 0:
            return
        data = (area,)

        #validate the change------------------------------------------------------------------------
        sql = 'select id from area where area = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* AREA CODE DOES NOT EXIST')
            return

        #make sure that there is not a station linked to the area-----------------------------------
        sql = 'select id from station where area = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* STATIONS ARE ATTACHED TO THIS AREA - CANNOT DELETE')
            return

        #process the change-------------------------------------------------------------------------
        if self.db_update('delete from area where area = ?', data) == 0:
            print('AREA ' + area + ' SUCCESSFULLY DELETED')
        return



    def liarea(self, message):
        """list basic area details to the screen, can be filtered by railroad.  can be sorted by
        area code, area name or railroad/area.
        """
        if self.show_access(message, 'LIAREA (sort[0/1/2]);(^railroad^)', 'R') != 0:
            return        

        #work out the various parameters------------------------------------------------------------
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            filter_railroad = value
        else:
            filter_railroad = ''

        # build the column titles-------------------------------------------------------------------
        area_name_size = 78 - self.areasize - self.railsize - 30 - 3
        titles = self.x_field('AREA====', self.areasize)                                  + ' ' + \
                 self.x_field('AREA NAME==============================', area_name_size)  + ' ' + \
                 self.x_field('RAIL====', self.railsize)                                  + ' ' + \
                 self.x_field('RAILROAD NAME==========================', 30)

        # get the extract data----------------------------------------------------------------------
        if sort_order == '1':
            sql = 'select area.area, area.name, railroad.railroad, railroad.name '  +\
                  'from area, railroad where area.railroad = railroad.railroad ' +\
                  'order by area.area'
        elif sort_order == '2':
            sql = 'select area.area, area.name, railroad.railroad, railroad.name '  +\
                  'from area, railroad where area.railroad = railroad.railroad ' +\
                  'order by area.name'
        else:
            sql = 'select area.area, area.name, railroad.railroad, railroad.name '  +\
                  'from area, railroad where area.railroad = railroad.railroad ' +\
                  'order by railroad.railroad, area.area'

        count, ds_areas = self.db_read(sql, '')
        if count < 0:
            return

        #report the extracted data------------------------------------------------------------------
        line_count = 0
        counter = 0
        for row in ds_areas:
            rail = row[2]
            if filter_railroad == '' or filter_railroad == rail:
                if line_count == 0:
                    print(titles)
                counter = counter + 1
                print(self.x_field(row[0], self.areasize) + " " +
                        self.x_field(row[1], area_name_size) + " " +
                        self.x_field(row[2], self.railsize) + " " +
                        self.x_field(row[3], 30))
                line_count = line_count + 1
                if line_count > 20:
                    line_count = 0
                    reply = raw_input('+')
                    if reply == 'x':
                        break
        print(' ** END OF DATA: ' + str(counter) + ' RECORDS DISPLAYED **')         
        return



    def prarea(self, message, Params):
        """print basic area details, can be filtered by railroad.  can be sorted by area code, area
        name or railroad/area.
        """
        if self.show_access(message, 'PRAREA (sort[0/1/2]);(^railroad^)', 'R') != 0:
            return

        #work out the various parameters------------------------------------------------------------
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            filter_railroad = value
        else:
            filter_railroad = ''

        # build the column titles-------------------------------------------------------------------
        area_name_size = 80 - self.areasize - self.railsize - 30 - 3
        titles = self.x_field('AREA====', self.areasize)                                  + ' ' + \
                 self.x_field('AREA NAME==============================', area_name_size)  + ' ' + \
                 self.x_field('RAIL====', self.railsize)                                  + ' ' + \
                 self.x_field('RAILROAD NAME==========================', 30)

        # get the extract data----------------------------------------------------------------------
        if sort_order == '1':
            sql = 'select area.area, area.name, railroad.railroad, railroad.name '  +\
                  'from area, railroad where area.railroad = railroad.railroad ' +\
                  'order by area.area'
            report_desc = 'AREAS SORTED BY AREA CODE'
        elif sort_order == '2':
            sql = 'select area.area, area.name, railroad.railroad, railroad.name '  +\
                  'from area, railroad where area.railroad = railroad.railroad ' +\
                  'order by area.name'
            report_desc = 'AREAS SORTED BY AREA NAME'
        else:
            sql = 'select area.area, area.name, railroad.railroad, railroad.name '  +\
                  'from area, railroad where area.railroad = railroad.railroad ' +\
                  'order by railroad.railroad, area.area'
            report_desc = 'AREAS SORTED BY RAILROAD, AREA'

        count, ds_areas = self.db_read(sql, '')
        if count < 0:
            return

        #build the extracted data-------------------------------------------------------------------
        self.temp = {}

        for row in ds_areas:
            rail = row[2]
            if filter_railroad == '' or filter_railroad == rail:
                print_line = self.x_field(row[0], self.areasize)  + ' '  +\
                             self.x_field(row[1], area_name_size) + ' '  +\
                             self.x_field(row[2], self.railsize)  + ' '  +\
                             self.x_field(row[3], 30)
            if sort_order == '1':
                self.temp[row[0]] = print_line
            elif sort_order == '2':
                self.temp[row[1]] = print_line
            else:
                self.temp[row[2] + row[0]] = print_line                

        #--------------------------------------------------------------------------------------------
        #report the extracted data
        self.print_report (titles      = titles,
                           report_id   = 'PRAREA',
                           report_name = report_desc,
                           Params      = Params)
        return
