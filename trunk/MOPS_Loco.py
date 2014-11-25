'''
Loco Class
A locomotive provides power to a train.  Type include multiple and dummy units.

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    15/08/2010 Ver 1  Unused variables removed
'''

import MOPS_Element

class cLoco(MOPS_Element.cElement):
    """working details of locomotives.  locomotives are allocated to a locomotive type, and will also
    belong to a railroad and to a home station.  locomotives will be at a station (and optionally at
    a place).  when a locomotive moves on a train, the originating station will be held until the
    train journey is complete.  A loco would be Powered (capable of pulling weight) or Unpowered.
    Fuel and Maintenance details are also held.
    """
    extract_code = 'select * from locomotive'
    extract_header = 'id|code|fuel|weight|time to maint|time in maint|is powered|type|railroad|home station|station|place|train\n'



    def adloco(self, message):
        """Add a loco running number, notes, and give the loco a type.  Also indicate owning
        railroad and home station.  set the fuel and time to maintenance to maximum for the type.
        set the time in maintenance to zero and is powered indicator to P.  Other details
        should be set to blank
        """
        if self.show_access(message, 'ADLOCO loco;^loco type^;^railroad^;^home station^', 'S') != 0:
            return
        errors = 0

        #code---------------------------------------------------------------------------------------
        loco, rc = self.extract_field(message, 0, 'LOCOMOTIVE RUNNING NUMBER')
        if rc > 0:
            return

        if len(loco) > self.locosize:
            print('* LOCOMOTIVE CODE ENTERED IS GREATER THAN THE ALLOWED SIZE')
            return
        
        if len(loco) ==0:
            print('* NO LOCOMOTIVE CODE ENTERED: A BLANK CODE IS NOT ALLOWED')
            return
        
        if loco.strip() == '':
            errors = errors + 1
            print('* BLANK LOCOMOTIVE CODE NOT ALLOWED')

        #check it does not already exist on the database
        data = (loco,)
        sql = 'select id from locomotive where loco = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* LOCOMOTIVE CODE ALREADY EXISTS')
            return

        #Loco Type----------------------------------------------------------------------------------
        loco_type, rc = self.extract_field(message, 1, 'LOCOMOTIVE TYPE')
        if rc > 0:
            return

        loct = (loco_type,)
        sql = 'select fuel_capacity, maint_interval, works_time, name ' +\
              'from locotype where locotype = ?'
        count, ds_types = self.db_read(sql, loct)
        if count < 0:
            return

        if count ==0:
            errors = errors + 1
            print('* LOCOMOTIVE TYPE DOES NOT EXIST')
        else:
            for row in ds_types:
                fuel_capacity = row[0]
                maint_interval = row[1]
                loco_type_name = row[3]
            
        #Railroad-----------------------------------------------------------------------------------
        rail, rc = self.extract_field(message, 2, 'RAILROAD')
        if rc > 0:
            return

        rr = (rail,)
        sql = 'select name from railroad where railroad = ?'
        count, ds_railroads = self.db_read(sql, rr)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* RAILROAD CODE DOES NOT EXIST')
        else:
            for row in ds_railroads:
                railroad_name = row[0]

        #HomeStation--------------------------------------------------------------------------------
        home_stax, rc = self.extract_field(message, 3, 'HOME STATION')
        if rc > 0:
            return

        stax = (home_stax,)
        sql = 'select long_name from station where station = ?'
        count, ds_station = self.db_read(sql, stax)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* HOME STATION CODE DOES NOT EXIST')
        else:
            for row in ds_station:
                home_station_name = row[0]

        #build and store the new record-------------------------------------------------------------
        if errors != 0:
            return

        blank = ''
        zero = 0
        powered = 'P'
        weight = 0
        data = (loco, loco_type, fuel_capacity, weight, maint_interval, zero, powered, rail, home_stax, home_stax, blank, blank)
        sql = 'insert into locomotive values (null, ?,?,?,?,?,?,?,?,?,?,?,?)'
        if self.db_update(sql, data) != 0:
            return

        #report the change to the screen
        print('NEW LOCOMOTIVE ADDED SUCCESSFULLY')   
        print(loco, '(' + loco_type + ' ' + loco_type_name + ')')
        print(rail, railroad_name, ' HOME STATION:' + home_stax, home_station_name)
        print('FUEL LOAD:' + str(fuel_capacity), 'MAINT DUE:' + str(maint_interval) + 'DAYS')
        return 



    def chloco(self, message):
        """Change the notes, loco type, owning railroad or home station for the given locomotive
        """
        if self.show_access(message,'CHLOCO loco;(^loco type^);(^railroad^);(^home station^)', 'S') != 0:
            return
        errors = 0

        #code---------------------------------------------------------------------------------------
        loco, rc = self.extract_field(message, 0, 'LOCOMOTIVE RUNNING NUMBER')
        if rc > 0:
            return

        data = (loco,)
        sql = 'select loco, locotype, railroad, home_station from locomotive where loco = ? '    
        count, ds_loco = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* LOCOMOTIVE CODE DOES NOT EXIST')
            return

        for row in ds_loco:
            loco_type = row[1]
            rail = row[2]
            home_stax = row[3]

        #Type---------------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            loco_type = value
        
        loct = (loco_type,)
        sql = 'select name from locotype where locotype = ?'
        count, dummy = self.db_read(sql, loct)
        if count < 0:
            return

        if count ==0:
            errors = errors + 1
            print('* LOCOMOTIVE TYPE DOES NOT EXIST')

        #Railroad-----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            rail = value

        rr = (rail,)
        sql = 'select name from railroad where railroad = ?'
        count, dummy = self.db_read(sql, rr)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* RAILROAD CODE DOES NOT EXIST')

        #HomeStation--------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 3, '')
        if rc == 0:
            home_stax = value

        stax = (home_stax,)
        sql = 'select long_name from station where station = ?'
        count, dummy = self.db_read(sql, stax)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* HOME STATION CODE DOES NOT EXIST')

        #build and store the new record-------------------------------------------------------------
        if errors != 0:
            return

        data = (loco_type, rail, home_stax, loco)
        sql = 'update locomotive set locotype = ?, railroad = ?, home_station = ? where loco = ?'
        if self.db_update(sql, data) != 0:
            return
        print('LOCOMOTIVE DETAILS CHANGED SUCCESSFULLY')
        self.shloco(loco)
        return 



    def fuelxx(self, message):
        """change the fuel on a loco, up to the maximum allowed for the type.  Does not have
        to be at a refuellling point; this is a correcting facility
        """
        if self.show_access(message, 'FUELXX loco;fuel', 'S') != 0:
            return

        #code---------------------------------------------------------------------------------------
        loco, rc = self.extract_field(message, 0, 'LOCOMOTIVE RUNNING NUMBER')
        if rc > 0:
            return

        #read the database and populate the fields
        data = (loco,)
        sql =   'select locomotive.loco, locomotive.fuel, locotype.fuel_capacity, ' +\
                'locotype.power_type ' +\
                'from locomotive, locotype where locomotive.loco = ? ' +\
                'and locomotive.locotype = locotype.locotype'
        count, ds_loco = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            print('* LOCOMOTIVE NOT FOUND, OR NOT LINKED TO VALID LOCOMOTIVE TYPE')
            return
        else:
            for row in ds_loco:
                fuel_capacity = row[2]
                power_type = row[3]

        if power_type == 'E':
            print('* ELECTRIC LOCOMOTIVES DO NOT REQUIRE FUELLING')
            return

        #fuel---------------------------------------------------------------------------------------
        fuel, rc = self.extract_field(message, 1, 'FUEL AMOUNT')
        if rc > 0:
            return

        try:
            if int(fuel) > 99999 or int(fuel) < 0:
                print('* FUEL STATE MUST BE IN THE RANGE 0 to 99999')
                return
        except:
            print('* FUEL STATE MUST BE A WHOLE NUMBER')
            return
                
        if int(fuel) > int(fuel_capacity):
            print('* FUEL CAPACITY OF LOCOMOTIVE TYPE IS ' + fuel_capacity + ' {REQUESTED ' + fuel + ')')
            return

        #build and store the new record-------------------------------------------------------------
        data = (fuel, loco)
        sql = 'update locomotive set fuel = ? where loco = ?'
        if self.db_update(sql, data) != 0:
            return

        print('LOCOMOTIVE FUEL LOAD CHANGED SUCCESSFULLY')
        self.shloco(loco)
        return



    def maintl(self, message):
        """change the maintenance details on a loco.  This is a correcting facility, loco
        does not have to be at a maintenance point.  Only one of the items (to  maint or in maint)
        should be set; the other should be left blank or be zero
        """
        if self.show_access(message, 'MAINTL loco;(time to maint);(works time)', 'S') != 0:
            return
        errors = 0
        maint_interval = 0
        works_time = 0

        #code---------------------------------------------------------------------------------------
        loco, rc = self.extract_field(message, 0, 'LOCOMOTIVE RUNNING NUMBER')
        if rc > 0:
            return

        #read the database and populate the fields
        data = (loco,)
        sql =   'select locomotive.loco, locomotive.time_to_maint, locomotive.time_in_maint, ' +\
                'locotype.maint_interval, locotype.works_time ' +\
                'from locomotive, locotype where locomotive.loco = ? '    +\
                'and locomotive.locotype = locotype.locotype'
        count, data = self.db_read(sql, data)
        if count < 0:
            return

        for row in data:
            time_to_maint = row[1]
            time_in_maint = row[2]
            maint_interval = row[3]
            works_time = row[4]

        #TimeToMaint--------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            time_to_maint = value
        else:
            time_to_maint = 0

        try:
            if int(time_to_maint) > 99999 or int(time_to_maint) < 0:
                errors = errors + 1
                print('* TIME TO MAINTENANCE MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* TIME TO MAINTENANCE MUST BE A WHOLE NUMBER')

        if int(time_to_maint) > int(maint_interval):
            errors = errors + 1
            print('* MAINTENANCE INTERVAL OF LOCOMOTIVE TYPE IS ' + str(maint_interval))

        #TimeInMaint--------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            time_in_maint = value
        else:
            time_in_maint = 0

        if int(time_to_maint) != 0 and int(time_in_maint) != 0:
            print('* EITHER TIME TO MAINTENANCE OR WORKS TIME MUST BE ZERO')
            return

        try:
            if int(time_in_maint) > 99999 or int(time_in_maint) < 0:
                errors = errors + 1
                print('* TIME IN MAINTENANCE MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* TIME IN MAINTENANCE MUST BE A WHOLE NUMBER')

        if int(time_in_maint) > works_time:
            errors = errors + 1
            print('* MAINTENANCE OUTAGE OF LOCOMOTIVE TYPE IS ' + str(works_time))

        #build and store the new record-------------------------------------------------------------
        if errors != 0:
            return

        data = (time_to_maint, time_in_maint, loco)
        sql = 'update locomotive set time_to_maint = ?, time_in_maint = ? where loco = ?'
        if self.db_update(sql, data) != 0:
            return
        print('LOCOMOTIVE MAINTENANCE DETAILS CHANGED SUCCESSFULLY')
        self.shloco(loco)
        return



    def powerx(self, message):
        """change the power state on a loco; toggle between having power or simply
        being weight on a train
        """
        if self.show_access(message, 'POWERX loco;power state [P/U]', 'N') != 0:
            return

        #code---------------------------------------------------------------------------------------
        loco, rc = self.extract_field(message, 0, 'LOCOMOTIVE RUNNING NUMBER')
        if rc > 0:
            return

        #read the database and populate the fields--------------------------------------------------
        data = (loco,)
        sql = 'select locomotive.loco, locomotive.is_powered, locotype.weight, ' +\
              'locomotive.time_in_maint from locomotive, locotype where locomotive.loco = ? ' +\
              'and locomotive.locotype = locotype.locotype'    
        count, ds_locos = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* LOCOMOTIVE NOT FOUND')
        else:
            for row in ds_locos:
                loco_weight = row[2]
                works_time = row[3]

        #IsPowered----------------------------------------------------------------------------------
        is_powered, rc = self.extract_field(message, 1, 'POWER STATE')
        if rc > 0:
            return

        if not (is_powered == 'P' or is_powered == 'U'):
            print('* POWER STATE MUST BE P-POWERED U-UNPOWERED')
            return

        if is_powered == 'P':
            loco_weight = 0

        if works_time != 0:
            is_powered = 'X'
            
        #--------------------------------------------------------------------------------------------
        #build and store the new record
        data = (is_powered, loco_weight, loco)
        sql = 'update locomotive set is_powered = ?, weight = ? where loco = ?'
        if self.db_update(sql, data) != 0:
            return
        print('LOCOMOTIVE POWER STATUS CHANGED SUCCESSFULLY')
        self.shloco(loco)
        return



    def locoat(self, message):
        """locate the loco at a new station.  This is a correction facility; normally
        a station is acquired by moving a train
        """
        if self.show_access(message, 'LOCOAT loco;^station^', 'N') != 0:
            return
        place = 0

        #code---------------------------------------------------------------------------------------
        loco, rc = self.extract_field(message, 0, 'LOCOMOTIVE RUNNING NUMBER')
        if rc > 0:
            return

        #read the database and populate the fields
        data = (loco,)
        sql =   'select loco, station, time_in_maint, fuel from locomotive where locomotive.loco = ? '    
        count, ds_loco = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            print('* LOCOMTIVE NOT FOUND')
            return

        for row in ds_loco:
            current_stax = row[1]
            time_in_maint = row[2]
            fuel = row[3]

        # station-----------------------------------------------------------------------------------
        station, rc = self.extract_field(message, 1, 'STATION')
        if rc > 0:
            return

        if time_in_maint > 0:
            print('* LOCOMOTIVE IN MAINTENANCE, CANNOT BE MOVED')
            return

        stax = (station,)
        sql = 'select id from station where station = ?'
        count, dummy = self.db_read(sql, stax)
        if count < 0:
            return

        if count == 0:
            print('* STATION CODE DOES NOT EXIST')
            return

        if current_stax != station:
            current_stax = station
            fuel = int(float(fuel) * 0.75)

        #build and store the new record-------------------------------------------------------------
        data = (current_stax, place, fuel, loco)
        sql = 'update locomotive set station = ?, place_id = ?, fuel = ? where loco = ?'
        if self.db_update(sql, data) != 0:
            return
        print('LOCOMOTIVE FUEL LOAD CHANGED SUCCESSFULLY')
        self.shloco(loco)
        return


    
    def locosp(self, message):
        """locate the loco at a place.  this is used by controlers to spot a
        locomotive at a defined place, where certain activities (maintenance, refuelling)
        can then happen automatically
        """
        if self.show_access(message, 'LOCOSP loco;^place^', 'N') != 0:
            return

        #code---------------------------------------------------------------------------------------
        loco, rc = self.extract_field(message, 0, 'LOCOMOTIVE RUNNING NUMBER')
        if rc > 0:
            return

        #read the database and populate the fields
        data = (loco,)
        sql =   'select locomotive.loco, locomotive.station, locomotive.time_in_maint, ' +\
                'locomotive.fuel, locomotive.locotype, locotype.fuel_capacity ' +\
                'from locomotive, locotype where locomotive.loco = ? ' +\
                'and locomotive.locotype = locotype.locotype'
        count, data = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* NO LOCOMOTIVE FOUND WITH THAT RUNNING NUMBER')
            return

        for row in data:
            current_stax = row[1]
            time_in_maint = row[2]
            loco_type = row[4]
            fuel_capacity = row[5]

        if time_in_maint > 0:
            print('* LOCO IN MAINTENANCE, CANNOT BE MOVED')
            return

        #Place--------------------------------------------------------------------------------------
        place, rc = self.extract_field(message, 1, 'PLACE')
        if rc > 0:
            return

        data = (current_stax, place)
        sql = 'select id, place_type from place where station = ? and code = ?'
        count, ds_places = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            print('* STATION/PLACE DOES NOT EXIST')
            return
        else:
            for row in ds_places:
                current_place_id = row[0]
                place_type = row[1]

        data = (loco_type,)
        sql = 'select works_time, power_type from locotype where locotype = ?'
        count, ds_types = self.db_read(sql, data)
        if not (count > 0):
            print('* ERROR ON DATABASE OR LOCO TYPE NOT FOUND')
            return

        for row in ds_types:
            time_in_maint = row[0]
            power_type = row[1]

        #build and store the new record.  power type for refuelling, place type for maintenance
        #if at a fuel spot, then the fuel is set to max but the powered states is set to F for
        #fuelling; this flag will be set to powered at the top of the hour
        if place_type == power_type:
            data = (current_place_id + fuel_capacity + 'F' + loco)
            sql = 'update locomotive set place_id = ?, fuel = ?, is_powered = ? where loco = ?'
        elif place_type == 'L':
            data = (current_place_id + time_in_maint + 'X' + loco)
            sql = 'update locomotive set place_id = ?, time_in_maint = ?, ' +\
                  'time_to_maint = 0, is_powered = ? where loco = ?'
        else:
            data = (current_place_id + loco)
            sql = 'update locomotive set place_id = ? where loco = ?'

        if self.db_update(sql, data) != 0:
            return

        #--------------------------------------------------------------------------------------------
        #report the change to the screen
        print('LOCOMOTIVE SPOTTED SUCCESSFULLY')
        self.shloco(loco)
        return


    
    def dxloco(self, message):
        """deletes a locomotive from the list.  checks that it is not on a train
        """
        if self.show_access(message, 'DXLOCO loco', 'S') != 0:
            return

        #code---------------------------------------------------------------------------------------
        loco, rc = self.extract_field(message, 0, 'LOCOMOTIVE RUNNING NUMBER')
        if rc > 0:
            return
        data = (loco,)

        #validate the change - check there is a record to delete
        sql = 'select id, train from locomotive where loco = ?'
        count, ds_locos = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* LOCOMOTIVE DOES NOT EXIST')
            return
        else:
            for row in ds_locos:
                if row[1] != '':
                    print('* LOCOMOTIVE IS ATTACHED TO A TRAIN AND CANNOT BE DELETED')
                    return

        sql = 'select car from car where is_attached_set = ?'
        count, ds_cars = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* LOCO IS A SET FOR THE FOLLOWING CARS AND CANNOT BE DELETED')
            for row in ds_cars:
                print(row[0])
                


        #--------------------------------------------------------------------------------------------
        #process the change
        if self.db_update('delete from locomotive where loco = ?', data) == 0:
            print('LOCOMOTIVE', loco, 'SUCCESSFULLY DELETED')
        return



    def shloco(self, message):
        """this is a routine to report summary details to the screen after an update
        not for general use, although it is available to end users if they know about it
        """
        if self.show_access(message, 'SHLOCO loco', 'R') != 0:
            return

        #code---------------------------------------------------------------------------------------
        loco, rc = self.extract_field(message, 0, 'LOCOMOTIVE RUNNING NUMBER')
        if rc > 0:
            return

        data = (loco,)
        sql =   'select locomotive.loco, '      +\
                'locomotive.fuel, '             +\
                'locomotive.time_to_maint, '    +\
                'locomotive.time_in_maint, '    +\
                'locomotive.is_powered, '       +\
                'locomotive.locotype, '         +\
                'locomotive.railroad, '         +\
                'locomotive.home_station, '     +\
                'locomotive.station, '          +\
                'locomotive.place_id, '         +\
                'locomotive.train, '            +\
                'locotype.name '                +\
                'from locomotive, locotype '    +\
                'where locomotive.loco = ? '    +\
                'and locomotive.locotype = locotype.locotype'
        count, ds_loco = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* LOCOMOTIVE CODE DOES NOT EXIST')
            return

        for row in ds_loco:
            fuel             = row[1]
            time_to_maint    = row[2]
            time_in_maint    = row[3]
            is_powered       = row[4]
            loco_type        = row[5]
            rail             = row[6]
            home_stax        = row[7]
            current_stax     = row[8]
            current_place_id = row[9]
            loco_type_name   = row[11]

        #--------------------------------------------------------------------------------------------
        #report the data to the screen
        if is_powered == 'U':
            power_state = ' * WARNING: LOCO IS UNPOWERED *'
        elif is_powered == 'X':
            power_state = '* LOCOMOTIVE IN MAINTENANCE *'
        elif is_powered == 'F':
            power_state = '* LOCOMOTIVE BEING REFUELLED *'
        else:
            power_state = ''

        data = (rail,)
        sql = 'select name from railroad where railroad = ?'
        count, ds_rail = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            railroad_name = 'NOT FOUND'
        else:
            for row in ds_rail:
                railroad_name = row[0]
                
        data = (current_stax,)
        sql = 'select long_name from station where station = ?'
        count, ds_stations = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            current_station_name = 'NOT FOUND'
        else:
            for row in ds_stations:
                current_station_name = row[0]
                
        data = (current_place_id,)
        sql = 'select code, name from place where id = ?'
        count, ds_places = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            current_plax = ''
            current_place_name = ''
        else:
            for row in ds_places:
                current_plax = row[0]
                current_place_name = row[1]

        data = (home_stax,)
        sql = 'select long_name from station where station = ?'
        count, ds_stations = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            home_station_name = 'NOT FOUND'
        else:
            for row in ds_stations:
                home_station_name = row[0]

        print(loco, '(' + loco_type, loco_type_name + ')')
        print(rail, railroad_name, ' HOME STATION:' + home_stax, home_station_name)
        print('AT:' + current_stax, current_plax, current_station_name, current_place_name, )
        print('FUEL LOAD:' + str(fuel), ' MAINT DUE:' + str(time_to_maint) + 'DAYS', 'IN WORKS:' + str(time_in_maint) + 'HRS', power_state)
        return 



    def liloco(self, message):
        """Show static details about locomotives ie type, notes, railroad, home station.
        Available filtered by type, owning railroad or home station.  Can be sorted by
        type/code, railroad code or simply in running number order
        """
        if self.show_access(message, 'LILOCO (sort[0/1/2/3]);(^loco type^);(^railroad^);(^station^)', 'R') != 0:
            return

        # report requirements
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            filter_type = value
        else:
            filter_type = '*'

        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            filter_rail = value
        else:
            filter_rail = '*'

        value, rc = self.extract_field(message, 3, '')
        if rc == 0:
            filter_stax = value
        else:
            filter_stax = '*'
       
        # build the column titles
        titles = self.x_field('LOCO======', self.locosize) + ' ' +\
                 self.x_field('TYPE======', self.loctsize) + ' ' +\
                 self.x_field('ENGINE', 8) + ' ' +\
                 self.x_field('RR========', self.railsize) + ' ' +\
                 self.x_field('HOME STN==', self.staxsize)

        #get the extract data
        if sort_order == '1':
            sql = 'select locomotive.loco, locomotive.locotype,  ' +\
                  'locomotive.railroad, locomotive.home_station, locotype.power_type ' +\
                  'from locomotive, locotype where locomotive.locotype = locotype.locotype ' +\
                  'order by locomotive.locotype, locomotive.code'
        elif sort_order == '2':
            sql = 'select locomotive.loco, locomotive.locotype,  ' +\
                  'locomotive.railroad, locomotive.home_station, locotype.power_type ' +\
                  'from locomotive, locotype where locomotive.locotype = locotype.locotype ' +\
                  'order by locomotive.railroad, locomotive.code'
        else:
            sql = 'select locomotive.loco, locomotive.locotype,  ' +\
                  'locomotive.railroad, locomotive.home_station, locotype.power_type ' +\
                  'from locomotive, locotype where locomotive.locotype = locotype.locotype ' +\
                  'order by locomotive.loco'
            
        count, ds_locos = self.db_read(sql, '')
        if count < 0:
            return

        #process the data
        line_count = 0
        counter = 0
        for row in ds_locos:
            loct = row[1]
            rail = row[2]
            stax = row[3]
            if loct == filter_type or filter_type == '*':
                if rail == filter_rail or filter_rail == '*':
                    if stax == filter_stax or filter_stax == '*':
                        if row[4] == 'D':
                            power_desc = 'DIESEL  '
                        if row[4] == 'E':
                            power_desc = 'ELECTRIC'
                        if row[4] == 'S':
                            power_desc = 'STEAM   '
                        if row[4] == 'O':
                            power_desc = 'OTHER   '
                        if line_count == 0:
                            print(titles)               
                        print(self.x_field(row[0], self.locosize) + " " +
                               self.x_field(row[1], self.loctsize) + " " +
                               power_desc + " " +
                               self.x_field(row[2], self.railsize) + " " +
                               self.x_field(row[3], self.staxsize))
                        counter = counter + 1
            line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break
        print(' ** END OF DATA:' + str(counter) + ' RECORDS DISPLAYED **')         
        return


    def prloco(self, message, Params):
        """Report static details about locomotives ie type, notes, railroad, home station.
        Available filtered by type, owning railroad or home station.  Can be sorted by
        type/code, railroad code or simply in running number order
        """
        if self.show_access(message, 'PRLOCO (sort[0/1/2/3]);(^loco type^);(^railroad^);(^station^)', 'R') != 0:
            return
        # report requirements
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            filter_type = value
        else:
            filter_type = '*'

        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            filter_rail = value
        else:
            filter_rail = '*'

        value, rc = self.extract_field(message, 3, '')
        if rc == 0:
            filter_stax = value
        else:
            filter_stax = '*'
       
        # build the column titles
        titles = self.x_field('LOCO======', self.locosize) + ' ' +\
                 self.x_field('TYPE======', self.loctsize) + ' ' +\
                 self.x_field('ENGINE', 8) + ' ' +\
                 self.x_field('RR========', self.railsize) + ' ' +\
                 self.x_field('HOME STN==', self.staxsize)

        #get the extract data
        if sort_order == '1':
            sql = 'select locomotive.loco, locomotive.locotype,  ' +\
                  'locomotive.railroad, locomotive.home_station, locotype.power_type ' +\
                  'from locomotive, locotype where locomotive.locotype = locotype.locotype ' +\
                  'order by locomotive.locotype, locomotive.code'
            report_desc = 'LOCOMOTIVES SORTED BY TYPE, LOCO NUMBER'
        elif sort_order == '2':
            sql = 'select locomotive.loco, locomotive.locotype,  ' +\
                  'locomotive.railroad, locomotive.home_station, locotype.power_type ' +\
                  'from locomotive, locotype where locomotive.locotype = locotype.locotype ' +\
                  'order by locomotive.railroad, locomotive.code'
            report_desc = 'LOCOMOTIVES SORTED BY RAILROAD, LOCO NUMBER'
        else:
            sql = 'select locomotive.loco, locomotive.locotype,  ' +\
                  'locomotive.railroad, locomotive.home_station, locotype.power_type ' +\
                  'from locomotive, locotype where locomotive.locotype = locotype.locotype ' +\
                  'order by locomotive.loco'
            report_desc = 'LOCOMOTIVES SORTED BY LOCO NUMBER'

        count, ds_locos = self.db_read(sql, '')
        if count < 0:
            return

        #process the data
        self.temp = {}
        
        for row in ds_locos:
            loct = row[1]
            rail = row[2]
            stax = row[3]
            if loct == filter_type or filter_type == '*':
                if rail == filter_rail or filter_rail == '*':
                    if stax == filter_stax or filter_stax == '*':
                        if row[4] == 'D':
                            power_desc = 'DIESEL  '
                        if row[4] == 'E':
                            power_desc = 'ELECTRIC'
                        if row[4] == 'S':
                            power_desc = 'STEAM   '
                        if row[4] == 'O':
                            power_desc = 'OTHER   '
                        print_line = self.x_field(row[0], self.locosize) + ' '   +\
                               self.x_field(row[1], self.loctsize) + ' '   +\
                               power_desc + ' '   +\
                               self.x_field(row[2], self.railsize) + ' '   +\
                               self.x_field(row[3], self.staxsize)
                        if sort_order == '1':
                            self.temp[row[1] + row[0]] = print_line
                        elif sort_order == '2':
                            self.temp[row[2] + row[0]] = print_line
                        else:
                            self.temp[row[0]] = print_line

        #report the extracted data
        self.print_report (titles = titles,
                           report_id = 'PRLOCO',
                           report_name = report_desc,
                           Params = Params)
        return




    def lsloco(self, message):
        """Show changeable details about locomotives ie fuel, maintenance, current location.
        Available filtered by type, owning railroad or home station.  Can be sorted by
        type/code, railroad code or simply in running number order
        """
        if self.show_access(message, 'LSLOCO (sort[0/1/2]);(^type^);(^railroad^);(^station^)', 'R') != 0:
            return

        # report requirements
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            filter_type = value
        else:
            filter_type = '*'

        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            filter_rail = value
        else:
            filter_rail = '*'

        value, rc = self.extract_field(message, 3, '')
        if rc == 0:
            filter_stax = value
        else:
            filter_stax = '*'
       
        
        # build the column titles
        place_size = 78 - self.locosize - self.loctsize - self.staxsize - 28 - 8
        if place_size > 30:
            place_size = 30
        titles = self.x_field('LOCO======', self.locosize) + ' ' +\
                 self.x_field('TYPE======', self.loctsize) + ' ' +\
                 self.x_field('FUEL=',5) + ' ' +\
                 self.x_field('MAINT',5) + ' ' +\
                 self.x_field('RPAIR',5) + ' ' +\
                 self.x_field('PWR',3) + ' ' +\
                 self.x_field('STATION===', self.staxsize) + ' ' +\
                 self.x_field('PLACE=========================', place_size) + ' ' +\
                 self.x_field('TRAIN=====', 10)

        #get the extract data
        if sort_order == '1':
            sql = 'select loco, locotype, fuel, railroad, ' +\
                  'time_to_maint, time_in_maint, is_powered, ' +\
                  'station, train, place_id ' +\
                  'from locomotive order by locomotive.locotype, locomotive.loco'
        elif sort_order == '2':
            sql = 'select loco, locotype, fuel, railroad, ' +\
                  'time_to_maint, time_in_maint, is_powered, ' +\
                  'station, train, place_id ' +\
                  'from locomotive order by locomotive.railroad, locomotive.loco'
        else:
            sql = 'select loco, locotype, fuel, railroad, ' +\
                  'time_to_maint, time_in_maint, is_powered, ' +\
                  'station, train, place_id ' +\
                  'from locomotive order by locomotive.loco'
            
        count, ds_locos = self.db_read(sql, '')
        if count < 0:
            return

        # build the extracted data
        line_count = 0
        counter = 0
        for row in ds_locos:
            place = ' ' 
            loct = row[1]
            rail = row[3]
            stax = row[7]
            if loct == filter_type or filter_type == '*':
                if rail == filter_rail or filter_rail == '*':
                    if stax == filter_stax or filter_stax == '*':
                        if line_count == 0:
                            print(titles)
                        if row[9] != 0:
                            data = (row[9],)
                            sql = 'select code, name from place where id = ?'
                            count, ds_places = self.db_read(sql, data)
                            for placerow in ds_places:
                                place = str(placerow[0]) + ' ' + placerow[1]
                        print(self.x_field(row[0], self.locosize) + " " +
                               self.x_field(row[1], self.loctsize) + " " +
                               self.x_field(row[2], 5, 'R') + " " +
                               self.x_field(row[4], 5, 'R') + " " +
                               self.x_field(row[5], 5, 'R') + " " +
                               self.x_field(row[6], 3, 'R') + " " +
                               self.x_field(row[7], self.staxsize) + " " +
                               self.x_field(place, place_size) + " " +
                               self.x_field(row[8], 10))
                        counter = counter + 1
                        line_count = line_count + 1
                        if line_count > 20:
                            line_count = 0
                            reply = raw_input('+')
                            if reply == 'x':
                                break
        print(' ** END OF DATA:' + str(counter) + ' RECORDS DISPLAYED **')         
        return
        


    def psloco(self, message, Params):
        """Print changeable details about locomotives ie fuel, maintenance, current location.
        Available filtered by type, owning railroad or home station.  Can be sorted by
        type/code, railroad code or simply in running number order
        """
        if self.show_access(message, 'PSLOCO (sort);(^type^);(^railroad^);(^station^)', 'R') != 0:
            return
        dummy = ' ' 

        # report requirements
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            filter_type = value
        else:
            filter_type = '*'

        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            filter_rail = value
        else:
            filter_rail = '*'

        value, rc = self.extract_field(message, 3, '')
        if rc == 0:
            filter_stax = value
        else:
            filter_stax = '*'
        
        # build the column titles
        place_size = 79 - self.locosize - self.loctsize - self.staxsize - 28 - 8
        if place_size > 30:
            place_size = 30
        titles = self.x_field('LOCO======', self.locosize) + ' ' +\
                 self.x_field('TYPE======', self.loctsize) + ' ' +\
                 self.x_field('FUEL=',5) + ' ' +\
                 self.x_field('MAINT',5) + ' ' +\
                 self.x_field('RPAIR',5) + ' ' +\
                 self.x_field('PWR',3) + ' ' +\
                 self.x_field('STATION===', self.staxsize) + ' ' +\
                 self.x_field('PLACE=========================', place_size) + ' ' +\
                 self.x_field('TRAIN=====', 10)

        #get the extract data
        if sort_order == '1':
            sql = 'select loco, locotype, fuel, railroad, ' +\
                  'time_to_maint, time_in_maint, is_powered, ' +\
                  'station, train, place_id ' +\
                  'from locomotive order by locomotive.locotype, locomotive.loco'
            report_desc = 'LOCO STATUS SORTED BY TYPE, LOCO NUMBER'
        elif sort_order == '2':
            sql = 'select loco, locotype, fuel, railroad, ' +\
                  'time_to_maint, time_in_maint, is_powered, ' +\
                  'station, train, place_id ' +\
                  'from locomotive order by locomotive.railroad, locomotive.loco'
            report_desc = 'LOCO STATUS SORTED BY RAILROAD, LOCO NUMBER'
        else:
            sql = 'select loco, locotype, fuel, railroad, ' +\
                  'time_to_maint, time_in_maint, is_powered, ' +\
                  'station, train, place_id ' +\
                  'from locomotive order by locomotive.loco'
            report_desc = 'LOCO STATUS SORTED BY LOCO NUMBER'
            
        count, ds_locos = self.db_read(sql, '')
        if count < 0:
            return

        # build the extracted data
        self.temp = {}
        
        for row in ds_locos:
            place = ''
            loct = row[1]
            rail = row[3]
            stax = row[7]
            if loct == filter_type or filter_type == '*':
                if rail == filter_rail or filter_rail == '*':
                    if stax == filter_stax or filter_stax == '*':
                        if row[9] != 0:
                            data = (row[9],)
                            sql = 'select code, name from place where id = ?'
                            count, ds_places = self.db_read(sql, data)
                            for placerow in ds_places:
                                place = str(placerow[0]) + ' ' + placerow[1]
                        print_line = self.x_field(row[0], self.locosize) + ' '   +\
                               self.x_field(row[1], self.loctsize) + ' '   +\
                               self.x_field(row[2], 5, 'R') + ' '   +\
                               self.x_field(row[4], 5, 'R') + ' '   +\
                               self.x_field(row[5], 5, 'R') + ' '   +\
                               self.x_field(row[6], 3, 'R') + ' '   +\
                               self.x_field(row[7], self.staxsize) + ' '   +\
                               self.x_field(place, place_size) + ' '   +\
                               self.x_field(row[8], 10)
                        if sort_order == '1':
                            self.temp[row[1] + row[0]] = print_line
                        elif sort_order == '2':
                            self.temp[row[3] + row[0]] = print_line
                        else:
                            self.temp[row[0]] = print_line

        #report the extracted data
        self.print_report (titles = titles,
                           report_id = 'PSLOCO',
                           report_name = report_desc,
                           Params = Params)
        return
        

        
    def Z002_maintain_loco_countdown(self, Flash, Params):
        """read all locos not in maintenance.  Each day reduce the
        time_to_maintenance by 1.  A loco is NOT in maintenance if time_in_maint = 0
        """
        message = ''
        time_to_maint = 90

        sql = 'update locomotive set time_to_maint = time_to_maint - 1 where time_in_maint = 0'
        if self.db_update(sql, '') != 0:
            return

        #for each loco getting near maintenance, report
        sql = 'select loco, time_to_maint, time_in_maint from locomotive ' +\
              'where time_in_maint = 0 and time_to_maint < 6'
        count, ds_locos = self.db_read(sql, '')
        if count < 0:
            return

        for row in ds_locos:
            loco = row[0]
            time_to_maint = row[1]
        
            #time to maintenance less than 5, so report
            if int(time_to_maint) < 6:
                if int(time_to_maint) == 5:
                    message = loco + '  HAS 5 DAYS TO MAINTENANCE'
                if int(time_to_maint) == 4:
                    message = loco + '  HAS 4 DAYS TO MAINTENANCE'
                if int(time_to_maint) == 3:
                    message = loco + '  HAS 3 DAYS TO MAINTENANCE'
                if int(time_to_maint) == 2:
                    message = loco + '  HAS 2 DAYS TO MAINTENANCE'
                if int(time_to_maint) == 1:
                    message = loco + '  HAS 1 DAYS TO MAINTENANCE'
                if int(time_to_maint) == 0:
                    message = loco + '  *** DUE MAINTENANCE ***'
                if int(time_to_maint) < 0:
                    message = loco + '  *** OVERDUE MAINTENANCE ***'
                    time_to_maint = '    0'
                message = 'LOCOMOTIVE ' + message
                Flash.Z003_generate_flash_message(message, Params)
                print(Params.get_date() + ' ' + Params.get_time() + 'Z002:' + message)
        return


    def Z014_set_loco_fuel_usage(self, Params):
        """count down fuel for non-electric locomotives if the loco is on a train
        """
        data = ('',)
        sql = 'select locomotive.id, locomotive.fuel, locomotive.loco, locotype.power_type ' +\
              'from locomotive, locotype where train <> ? and ' +\
              'locotype.locotype = locomotive.locotype'
        count, ds_locos = self.db_read(sql, data)
        if count < 1:
            return

        for row in ds_locos:
            power_type = row[3]
            if power_type != 'E':
                fuel = row[1] - 1
                if fuel < -2:
                    fuel = -1
                loco_id = row[0]
                data = (fuel, loco_id)
                sql = 'update locomotive set fuel = ? where id = ?'
                self.db_update(sql, data)
                if row[1] < 5:
                    print(Params.get_date() + ' ' + Params.get_time() +
                           'Z014: FUEL FOR' + str(row[2]) + 'REDUCED TO' + str(row[1]))
        return


    def Z023_works_locos(self, Flash, Params):
        sql = 'update locomotive set time_in_maint = time_in_maint - 1 where time_in_maint > 0'
        if self.db_update(sql, '') != 0:
            return

        sql = 'select locomotive.id, locomotive.loco, locotype.maint_interval '     +\
              'from locomotive, locotype '                                          +\
              'where locomotive.time_in_maint = 0 '                                 +\
              'and locomotive.time_to_maint = 0 and locomotive.locotype = locotype.locotype'
        count, data = self.db_read(sql, '')
        if count < 1:
            return

        for row in data:
            data = (row[2], 'P', row[0])
            loco = row[1]
            sql = 'update locomotive set time_to_maint = ?, is_powered = ? where id = ?'
            self.db_update(sql, data)
            message = 'LOCOMOTIVE ' + loco + ' MAINTENANCE COMPLETE; READY FOR TRAFFIC'
            Flash.Z003_generate_flash_message(message, Params)
            print(Params.get_date() + ' ' + Params.get_time() +
                   'Z023: LOCOMOTIVE' + loco + 'RETURNING TO TRAFFIC')
        return


    def Z022_refuel_loco(self, Params):
        """refuelling complete, set the status to fuelled by switching the locomotive
        to powered
        """
        data = ('F',)
        sql = 'select loco from locomotive where is_powered = ?'
        count, ds_fuel = self.db_read(sql, data)
        if count < 0:
            return

        for row in ds_fuel:
            loco = row[0]
            print(Params.get_date() + ' ' + Params.get_time() +
                   'Z022: REFUELLING' + loco + 'COMPLETED')
            
        data = ('P','F')
        sql = 'update locomotive set is_powered = ? where is_powered = ?'
        if self.db_update(sql, data) != 0:
            return
        return
