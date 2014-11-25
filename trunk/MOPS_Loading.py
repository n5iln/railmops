'''
Loading Class
Loading and unloading facilities

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    Ver 1   Unused variables removed
            Changed header on LILOAD to say Types, not Cars
'''

import MOPS_Element

class cLoading(MOPS_Element.cElement):
    """loading codes determine how commodities are loaded into cars, and which places have facilities
    to load and unload comodities.  loading codes have attributes indicating whether the code can be
    used for loading, unloading or both.  loading codes are used at places and by car types and
    commodities
    """
    extract_code = 'select * from loading'
    extract_header = 'id|code|description|loading|unloading\n'



    def adload(self, message):
        """add a new loading code, indicating whether it can be used for loading, unloading or both
        """
        if self.show_access(message,
                            'ADLOAD load;description;loading[Y/N];unloading[Y/N]', 'S') != 0:
            return
        errors = 0

        #Loading code-------------------------------------------------------------------------------
        load, rc = self.extract_field(message, 0, 'LOADING CODE')
        if rc > 0:
            return
        
        if len(load) > self.loadsize:
            print('* LOADING CODE ENTERED IS GREATER THAN THE ALLOWED SIZE')
            return
        
        if len(load) ==0:
            print('* NO LOADING CODE ENTERED: A BLANK CODE IS NOT ALLOWED')
            return

        #check it does not already exist on the database
        data = (load,)
        sql = 'select id from loading where loading = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* LOADING CODE ALREADY EXISTS')
            return

        #description--------------------------------------------------------------------------------
        description, rc = self.extract_field(message, 1, 'LOADING DESCRIPTION')
        if rc > 0:
            return

        #used for loading---------------------------------------------------------------------------
        loading, rc = self.extract_field(message, 2, 'USED FOR LOADING')
        if rc > 0:
            return

        if not (loading == 'Y' or loading == 'N'):
            errors = errors + 1
            print('* LOADING CODE MUST BE SET TO Y OR N')

        #used for unloading-------------------------------------------------------------------------
        unloading, rc = self.extract_field(message, 3, 'USED FOR UNLOADING')
        if rc > 0:
            return

        if not (unloading == 'Y' or unloading == 'N'):
            errors = errors + 1
            print('* UNLOADING CODE MUST BE SET TO Y OR N')

        #carry out the update-----------------------------------------------------------------------
        if errors != 0:
            return
        
        data = (load, description, loading, unloading)
        sql = 'insert into loading values (null, ?, ?, ?, ?)'
        if self.db_update(sql, data) != 0:
            return

        #report the change to the screen
        if loading == 'Y':
            load_info = 'YES'
        else:
            load_info = 'NO'
        if unloading == 'Y':
            unload_info = 'YES'
        else:
            unload_info = 'NO'
        print('NEW LOADING CODE ADDED SUCCESSFULLY')
        print(load + ':', description)
        print('LOADING: ' + load_info + ' UNLOADING: ' + unload_info)
        return errors



    def chload(self, message):
        if self.show_access(message, 'CHLOAD load;(description);(loading[Y/N]);(unloading[Y/N])',
                            'S') != 0:
            return
        errors = 0

        #Loading code-------------------------------------------------------------------------------
        load, rc = self.extract_field(message, 0, 'LOADING CODE')
        if rc > 0:
            return

        #read the database file and populate the fields
        data = (load,)
        sql = 'select desc, can_load, can_unload from loading where loading = ?'
        count, ds_load = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* LOADING CODE DOES NOT EXIST')
            return

        for row in ds_load:
            description = row[0]
            loading = row[1]
            unloading = row[2]

        #description--------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            description = value

        #used for loading---------------------------------------------------------------------------
        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            loading = value

        if not (loading == 'Y' or loading == 'N'):
            errors = errors + 1
            print('* LOADING CODE MUST BE SET TO Y OR N')

        #used for unloading-------------------------------------------------------------------------
        value, rc = self.extract_field(message, 3, '')
        if rc == 0:
            unloading = value

        if not (unloading == 'Y' or unloading == 'N'):
            errors = errors + 1
            print('* UNLOADING CODE MUST BE SET TO Y OR N')

        #carry out the update-----------------------------------------------------------------------
        if errors != 0:
            return
        
        data = (description, loading, unloading, load)
        sql = 'update loading set desc = ?, can_load = ?, can_unload = ? where loading = ?'
        if self.db_update(sql, data) != 0:
            return

        #report the change to the screen
        if loading == 'Y':
            load_info = 'YES'
        else:
            load_info = 'NO'
        if unloading == 'Y':
            unload_info = 'YES'
        else:
            unload_info = 'NO'
        print('LOADING CODE CHANGED SUCCESSFULLY')
        print(load + ':', description)
        print('LOADING: ' + load_info + ' UNLOADING: ' + unload_info)
        return errors



    def dxload(self, message):
        """Deletes a loading code entry from the list.  loading codes cannot be used for loading or
        unloading by car types, commodities or places
        """
        if self.show_access(message, 'DXLOAD load', 'S') != 0:
            return

        #Loading code-------------------------------------------------------------------------------
        load, rc = self.extract_field(message, 0, 'LOADING CODE')
        if rc > 0:
            return

        data = (load,)

        #validate the change - check there is a record to delete------------------------------------
        sql = 'select id from loading where loading = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* LOADING CODE DOES NOT EXIST')
            return

        #make sure that there is not a place linked to the loading code as a loading place----------
        sql = 'select id from place where loading = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* PLACES USE THIS CODE FOR LOADING - CANNOT DELETE')
            return

        #make sure that there is not a place linked to the loading code as an unloading place-------
        sql = 'select id from place where unloading = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* PLACES USE THIS CODE FOR UNLOADING - CANNOT DELETE')
            return

        #make sure that there is not a cartype linked to the loading code---------------------------
        sql = 'select id from cartype where loading = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* CAR TYPES USE THIS CODE FOR LOADING - CANNOT DELETE')
            return

        #make sure that there is not a cartype linked to the unloading code-------------------------
        sql = 'select id from cartype where unloading = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* CAR TYPES USE THIS CODE FOR UNLOADING - CANNOT DELETE')
            return

        #make sure that there is not a commodity linked to the loading code-------------------------
        sql = 'select id from commodity where loading = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* COMMODITIES USE THIS CODE FOR LOADING - CANNOT DELETE')
            return

        #process the change-------------------------------------------------------------------------
        if self.db_update('delete from loading where loading = ?', data) == 0:
            print('LOADING ' + load + ' SUCCESSFULLY DELETED')
        return



    def liload(self, message):
        """report basic information about loading codes
        """
        if self.show_access(message, 'LILOAD (sort[0/1])', 'R') != 0:
            return        

        #work out the various parameters------------------------------------------------------------
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        # build the column titles-------------------------------------------------------------------
        desc_size = 80 - self.loadsize - 27 - 6
        if desc_size > 30:
            desc_size = 30
        titles = self.x_field('LOADING=', self.loadsize) + ' ' +\
                 self.x_field('DESCRIPTION===================', 30) + ' ' +\
                 self.x_field('  LOAD', 6) + ' ' +\
                 self.x_field('UNLOAD', 6) + ' ' +\
                 self.x_field('PLACE', 5) + ' ' +\
                 self.x_field('CMDTY', 5) + ' ' +\
                 self.x_field('TYPES', 5)                                        #Rev 1

        # get the extract data----------------------------------------------------------------------
        if sort_order == '1':
            sql = 'select loading, desc, can_load, can_unload from loading order by desc'
        else:
            sql = 'select loading, desc, can_load, can_unload from loading order by loading'
        count, ds_loads = self.db_read(sql, '')
        if count < 0:
            return

        #report the extracted data-----------------------------------------------------------------
        line_count = 0
        for row in ds_loads:
            if line_count == 0:
                print(titles)
            load_code = row[0]
            data = (load_code, load_code)
            sql = 'select id from place where loading = ? or unloading = ?'
            place_count, dummy = self.db_read(sql, data)
            sql = 'select id from cartype where loading = ? or unloading = ?'
            cartype_count, dummy = self.db_read(sql, data)
            data = (load_code,)
            sql = 'select id from commodity where loading = ?'
            comm_count, dummy =  self.db_read(sql, data)
            print(self.x_field(row[0], self.loadsize) + " " +
                    self.x_field(row[1], 30) + " " +
                    self.x_field(row[2], 6, 'R') + " " +
                    self.x_field(row[3], 6, 'R') + " " +
                    self.x_field(place_count, 5, 'R') + " " +
                    self.x_field(comm_count, 5, 'R') + " " +
                    self.x_field(cartype_count, 5, 'R'))                
            line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break
        print(' ** END OF DATA: ' + str(count) + ' RECORDS DISPLAYED **')         
        return



    def prload(self, message, Params):
        """report basic information about loading codes.  sortable by description or code
        """
        if self.show_access(message, 'PRLOAD (sort[0/1])', 'R') != 0:
            return        

        #work out the various parameters------------------------------------------------------------
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        # build the column titles--------------------------------------------------------------------
        titles = self.x_field('LOADING=', self.loadsize) + ' ' +\
                 self.x_field('DESCRIPTION===================', 30) + ' ' +\
                 self.x_field('  LOAD', 6) + ' ' +\
                 self.x_field('UNLOAD', 6)

        # get the extract data-----------------------------------------------------------------------
        if sort_order == '1':
            sql = 'select loading, desc, can_load, can_unload from loading order by desc'
        else:
            sql = 'select loading, desc, can_load, can_unload from loading order by loading'
        count, ds_loads = self.db_read(sql, '')
        if count < 0:
            return

        #report the extracted data-------------------------------------------------------------------
        self.temp = {}
        for row in ds_loads:
            print_line = self.x_field(row[0], self.loadsize) + ' ' +\
                    self.x_field(row[1], 30) + ' ' +\
                    self.x_field(row[2], 6, 'R') + ' ' +\
                    self.x_field(row[3], 6, 'R')                

            if sort_order == '1':
                self.temp[row[1]] = print_line
            else:
                self.temp[row[0]] = print_line

        #report the extracted data-------------------------------------------------------------------
        self.print_report (titles = titles,
                           report_id = 'PRLOAD',
                           report_name = 'LIST OF LOADING TYPE CODES',
                           Params = Params)
        return
      
