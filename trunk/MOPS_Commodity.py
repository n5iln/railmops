'''
Commodities Class
The product that is created by an industry and moved around in cars

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.
'''

import MOPS_Element

class cCommodities(MOPS_Element.cElement):
    """details about commodities.  commodities describe what goods are moved around the railroad,
    and need loading codes, and associated loading and unloading rates.  also indicates whether
    a commodity requires clean cars.
    """
    extract_code   = 'select * from commodity'
    extract_header = 'id|code|description|loading code|loading rate|unloading rate|clean cars reqd\n'



    def adcomm(self, message):
        """adds a new commodity, including loading/unloading rate, whether it requires clean cars
        and is linked to a loading code
        """
        if self.show_access(message,
                            'ADCOMM commodity;description;^load^;loading rate;' +\
                            'unloading rate;clean car[Y/N]',
                            'S') != 0:
            return

        errors = 0
        
        #Commodity code-----------------------------------------------------------------------------
        comm, rc = self.extract_field(message, 0, 'COMMODITY CODE')
        if rc > 0:
            return

        if len(comm) > self.commsize:
            print('* COMMODITY CODE ENTERED IS GREATER THAN THE ALLOWED SIZE')
            return
        
        if len(comm) ==0:
            print('* NO COMMODITY CODE ENTERED: A BLANK CODE IS NOT ALLOWED')
            return

        #check it does not already exist on the database
        t = (comm,)
        sql = 'select id from commodity where commodity = ?'
        count, dummy = self.db_read(sql, t)
        if count < 0:
            return
        if count != 0:
            print('* COMMODITY CODE ALREADY EXISTS')
            return

        #description--------------------------------------------------------------------------------
        commodity_name, rc = self.extract_field(message, 1, 'COMMODITY DESCRIPTION')
        if rc > 0:
            return

        #loading code-------------------------------------------------------------------------------
        load, rc = self.extract_field(message, 2, 'LOADING CODE')
        if rc > 0:
            return

        t = (load,)
        sql = 'select desc from loading where loading = ?'
        count, ds_loadings = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* LOADING CODE DOES NOT EXIST (' + load + ')')
        else:
            for row in ds_loadings:
                loading_desc = row[0]

        #loading rate-------------------------------------------------------------------------------
        loading_rate, rc = self.extract_field(message, 3, 'RATE USED FOR LOADING')
        if rc > 0:
            return

        try:
            if int(loading_rate) > 99999 or int(loading_rate) < 0:
                errors = errors + 1
                print('* LOADING RATE MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* LOADING RATE MUST BE A WHOLE NUMBER')

        #unloading rate-----------------------------------------------------------------------------
        unloading_rate, rc = self.extract_field(message, 4, 'RATE USED FOR UNLOADING')
        if rc > 0:
            return

        try:
            if int(unloading_rate) > 99999 or int(unloading_rate) < 0:
                errors = errors + 1
                print('* UNLOADING RATE MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* UNLOADING RATE MUST BE A WHOLE NUMBER')

        #clean cars required------------------------------------------------------------------------
        requires_clean_cars, rc = self.extract_field(message, 5, 'CLEAN CAR USAGE')
        if rc > 0:
            return
        
        if not (requires_clean_cars == 'Y' or requires_clean_cars == 'N'):
            errors = errors + 1
            print('* CLEAN CAR INDICATOR MUST BE Y OR N')

        #carry out the update----------------------------------------------------------------------
        if errors != 0:
            return
        
        t = (comm, commodity_name, load, loading_rate, unloading_rate, requires_clean_cars)
        sql = 'insert into commodity values (null, ?, ?, ?, ?, ?, ?)'

        if self.db_update(sql, t) != 0:
            return

        print('NEW COMMODITY ADDED SUCCESSFULLY')
        print(comm + ':' + commodity_name)
        print('LOADING CODE:' + load + loading_desc)
        print('LOADING RATE:' + loading_rate + 'UNLOADING RATE:' + unloading_rate)
        if requires_clean_cars == 'Y':
            print('COMMODITY REQUIRES CLEAN CARS')
        return



    def chcomm(self, message):
        """change details on a commodity, such as the description, loading code, loading and
        unloading rate and whether a clean car is required
        """
        if self.show_access(message,
            'CHCOMM commodity;(description);(^load^);(loading rate);' +\
                            '(unloading rate);(clean car[Y/N]','S') != 0:
            return
        errors = 0
        
        #Commodity code-----------------------------------------------------------------------------
        comm, rc = self.extract_field(message, 0, 'COMMODITY CODE')
        if rc > 0:
            return
        
        #read the database file and populate the fields
        t = (comm,)
        sql = 'select name, loading_rate, unloading_rate, clean_cars, loading ' +\
              'from commodity where commodity = ?'
        count, ds_comm = self.db_read(sql, t)
        if count < 0:
            return

        for row in ds_comm:
            commodity_name = row[0]
            loading_rate = row[1]
            unloading_rate = row[2]
            requires_clean_cars = row[3]
            load = row[4]

        #description--------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            commodity_name = value

        #used for loading---------------------------------------------------------------------------
        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            load = value

        t = (load,)
        sql = 'select desc from loading where loading = ?'
        count, ds_loadings = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* LOADING CODE DOES NOT EXIST (' + value + ')')
        else:
            for row in ds_loadings:
                loading_desc = row[0]

        #loading rate-------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 3, '')
        if rc == 0:
            loading_rate = value

        try:
            if int(loading_rate) > 99999 or int(loading_rate) < 0:
                errors = errors + 1
                print('* LOADING RATE MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* LOADING RATE MUST BE A WHOLE NUMBER')

        #unloading rate-----------------------------------------------------------------------------
        value, rc = self.extract_field(message, 4, '')
        if rc == 0:
            unloading_rate = value

        try:
            if int(unloading_rate) > 99999 or int(unloading_rate) < 0:
                errors = errors + 1
                print('* UNLOADING RATE MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* UNLOADING RATE MUST BE A WHOLE NUMBER')

        #clean cars required------------------------------------------------------------------------
        value, rc = self.extract_field(message, 5, '')
        if rc == 0:
            requires_clean_cars = value

        if not (requires_clean_cars == 'Y' or requires_clean_cars == 'N'):
            errors = errors + 1
            print('* CLEAN CAR INDICATOR MUST BE Y OR N')
            
        #carry out the update-----------------------------------------------------------------------
        if errors != 0:
            return
        
        t = (commodity_name, loading_rate, unloading_rate, requires_clean_cars, load, comm)
        sql = 'update commodity set name = ?, loading_rate = ?, unloading_rate = ?, ' +\
              'clean_cars = ?, loading = ? where commodity = ?'
        if self.db_update(sql, t) != 0:
            return

        print('COMMODITY DETAILS CHANGED SUCCESSFULLY')
        print(comm + ':', commodity_name)
        print('LOADING CODE:' + load, loading_desc)
        print('LOADING RATE:' + str(loading_rate) + 'UNLOADING RATE:' + str(unloading_rate))
        if requires_clean_cars == 'Y':
            print('COMMODITY REQUIRES CLEAN CARS')
        return 



    def dxcomm(self, message):
        """removes a commodity from the list.  checks that it is not being used in a warehouse or
        carried on a car
        """
        if self.show_access(message, 'DXCOMM commodity', 'S') != 0:
            return

        #Commodity code-----------------------------------------------------------------------------
        comm, rc = self.extract_field(message, 0, 'COMMODITY CODE')
        if rc > 0:
            return

        t = (comm,)

        #validate the change - check there is a record to delete------------------------------------
        sql = 'select id from commodity where commodity = ?'
        count, dummy = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            print('* COMMODITY CODE DOES NOT EXIST')
            return

        #make sure that there is not a warehouse linked to the commodity----------------------------
        sql = 'select id from warehouse where commodity = ?'
        count, dummy = self.db_read(sql, t)
        if count < 0:
            return
        if count > 0:
            print('* WAREHOUSES USE THIS COMMODITY - CANNOT DELETE')
            return

        #make sure that there is not a car loaded with the -----------------------------------------
        sql = 'select id from car where commodity = ?'
        count, dummy = self.db_read(sql, t)
        if count < 0:
            return
        if count > 0:
            print('* A CAR IS LOADED WITH THIS COMMODITY - CANNOT DELETE')
            return
        
        #process the change-------------------------------------------------------------------------
        if self.db_update('delete from commodity where commodity = ?', t) == 0:
            print('COMMODITY' + comm + 'SUCCESSFULLY DELETED')
        return



    def licomm(self, message):
        """list commodities to the screen
        """
        if self.show_access(message, 'LICOMM (sort[0/1])', 'R') != 0:
            return        

        #work out the various parameters
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        #build the titles
        titles = self.x_field('COMMODITY', self.commsize) + ' ' +\
                 self.x_field('DESCRIPTION==================', 30) + ' ' +\
                 self.x_field('LOADING===', self.loadsize) + ' ' +\
                 self.x_field('   LOAD', 7) + ' ' +\
                 self.x_field(' UNLOAD', 7) + ' ' +\
                 self.x_field('CLEAN?', 6)

        if sort_order == '1':
            sql = 'select commodity, name, loading, loading_rate, unloading_rate, clean_cars ' +\
                  'from commodity order by name'
        else:            
            sql = 'select commodity, name, loading, loading_rate, unloading_rate, clean_cars ' +\
                  'from commodity order by commodity '

        count, ds_comm = self.db_read(sql, '')
        if count < 0:
            return

        #process the data
        line_count = 0
        for row in ds_comm:
            if line_count == 0:
                print(titles)
            print(self.x_field(row[0], self.commsize) + " " +
                   self.x_field(row[1], 30) + " " +
                   self.x_field(row[2], self.loadsize) + " " +
                   self.x_field(row[3], 7, 'R') + " " +
                   self.x_field(row[4], 7, 'R') + " " +
                   self.x_field(row[5], 6, 'R'))
            line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break
        print(' ** END OF DATA:' + str(count) + ' RECORDS DISPLAYED **')         
        return

        
    def prcomm(self, message, Params):
        if self.show_access(message, 'PRCOMM (sort[0/1])', 'R') != 0:
            return        

        #work out the various parameters
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        #build the titles
        titles = self.x_field('COMMODITY', self.commsize) + ' ' +\
                 self.x_field('DESCRIPTION==================', 30) + ' ' +\
                 self.x_field('LOADING===', self.loadsize) + ' ' +\
                 self.x_field('   LOAD', 7) + ' ' +\
                 self.x_field(' UNLOAD', 7) + ' ' +\
                 self.x_field('CLEAN?', 6)

        #select the data required
        if sort_order == '1':
            sql = 'select commodity, name, loading, loading_rate, unloading_rate, clean_cars ' +\
                  'from commodity order by name'
        else:            
            sql = 'select commodity, name, loading, loading_rate, unloading_rate, clean_cars ' +\
                  'from commodity order by commodity '

        count, ds_comm = self.db_read(sql, '')
        if count < 0:
            return

        #build the extracted data
        self.temp = {}

        for row in ds_comm:
            print_line = self.x_field(row[0], self.commsize) + ' ' +\
                   self.x_field(row[1], 30) + ' ' +\
                   self.x_field(row[2], self.loadsize) + ' ' +\
                   self.x_field(row[3], 7, 'R') + ' ' +\
                   self.x_field(row[4], 7, 'R') + ' ' +\
                   self.x_field(row[5], 6, 'R')
            if sort_order == '1':
                self.temp[row[1]] = print_line
            else:
                self.temp[row[0]] = print_line

        #report the extracted data
        self.print_report (titles = titles,
                           report_id = 'PRCOMM',
                           report_name = 'LIST OF COMMODITIES',
                           Params = Params)
        return
