'''
Cars Class
The freight cars or wagons that move goods and products around the railway.  Cars are unpowered.

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    Rev 1 Corrected sql data input to read correct variable in CARXAT (block move)
          Corrected sql data input to read correct variable in CLEANX (block move)
          Corrected population of filters from input in LONWAY
          Added new routine Z044_trimop_carloads to report car load movements
          Removed unused variables from Z013_select_car_for_loading,MTYORD
          Added current place name on output to CARXSP
          Multiple changes to make dataset return names begin ds_
          Multiple changes to remove unused variable data on sql input statements
          Corrected sql data input to read correct variable in Z005_Waybill, CHCARX
          Added counter check for good return for returned data in LACARS, LMTCAR
          Corrected default time to maintenance in Z011_maintain_car_coundown
          Changed count when moving blocks of cars (as note said additional)
          Added/Corrected processing to reduce amount in storage by amount loaded
          Maintenance details for cars suppressed when spotting
          Rewrote LONWAY to limit to empty cars and to provide improved current location detail
'''

import MOPS_Element

class cCars(MOPS_Element.cElement):
    """details about individual cars.  cars are owned by railroads and are allocated to a home
    station.  cars are allocated to a car type and are also linked to a car class.  cars have a
    current station or train, and may also have a place if spotted.  if a car has been allocated
    to an order then the destination will also be shown.  if a car is added to a train then the
    originating station is added.  cars can be grouped as a block to make them easy to move.  if
    a car has been loaded it is automatically set to dirty.
    """
    extract_code = 'select * from car'
    extract_header = 'id|code|car type|time to maint|time in maint|car class|railroad|' +\
                     'home station|current station|current place|train|block|weight_loaded|' +\
                     'attached to set|clean or dirty|car order\n'


    def adcarx(self, message):
        """adds a new car.  the car is linked to a car type (and also to a car class via its type).
        The car is also owned by a railroad and initially placed at a home station (which also
        identifies its current station).  the time to maintenance for the car is taken from the
        reference file.
        """
        if self.show_access(message, 'ADCARX car;^car type^;^railroad^;^home station^', 'S') != 0:
            return
        errors = 0
        
        #car code-----------------------------------------------------------------------------------
        car, rc = self.extract_field(message, 0, 'CAR RUNNING NUMBER')
        if rc > 0:
            return
        
        if len(car) > self.carxsize:
            print('* CAR RUNNING NUMBER ENTERED IS GREATER THAN THE ALLOWED SIZE')
            return
        
        if len(car) ==0:
            print('* NO CAR RUNNING NUMBER ENTERED: A BLANK CODE IS NOT ALLOWED')
            return        

        #check it does not already exist on the database
        t = (car,)
        sql = 'select id from car where car = ?'
        count, dummy = self.db_read(sql, t)
        if count < 0:
            return
        if count != 0:
            print('* CAR RUNNING NUMBER ALREADY EXISTS')
            return

        #car type-----------------------------------------------------------------------------------
        cartype, rc = self.extract_field(message, 1, 'CAR TYPE')
        if rc > 0:
            return

        t = (cartype,)
        sql = 'select carclass, name from cartype where cartype = ?'
        count, ds_cartypes = self.db_read(sql, t)
        if count < 0:
            return
        if count ==0:
            errors = errors + 1
            print('* CAR TYPE (' + cartype + ') DOES NOT EXIST')
        else:
            for row in ds_cartypes:
                carclass = row[0]
                cartype_name = row[1]
            
        #Railroad-----------------------------------------------------------------------------------
        railroad, rc = self.extract_field(message, 2, 'RAILROAD')
        if rc > 0:
            return
        
        rr = (railroad,)
        sql = 'select name from railroad where railroad = ?'
        count, ds_railroads = self.db_read(sql, rr)
        if count < 0:
            return
        if count == 0:
            errors = errors + 1
            print('* RAILROAD CODE (' + railroad + ') DOES NOT EXIST')
        else:
            for row in ds_railroads:
                railroad_name = row[0]

        #HomeStation--------------------------------------------------------------------------------
        station, rc = self.extract_field(message, 3, 'HOME STATION')
        if rc > 0:
            return
        
        stax = (station,)
        sql = 'select long_name from station where station = ?'
        count, ds_stations = self.db_read(sql, stax)
        if count < 0:
            return
        if count == 0:
            errors = errors + 1
            print('* HOME STATION CODE DOES NOT EXIST')
        else:
            for row in ds_stations:
                station_name = row[0]

        #build and store the new record-------------------------------------------------------------
        if errors != 0:
            return

        sql = 'select value from parameter where name = ?'
        t = ('CARMAINT',)
        count, ds_params = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            print('NO DEFAULT VALUE SET FOR CAR MAINTENANCE, 90 DAY SASSUMED')
            maint_interval = 90
        else:
            for row in ds_params:
                maint_interval = row[0]

        blank = ''
        zero = 0

        t = (car, cartype, maint_interval, zero, carclass, railroad, blank, station,
             station, zero, blank, blank, zero, blank, blank, zero)
        sql = 'insert into car values (null, ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
        if self.db_update(sql, t) != 0:
            return
        
        #report the change to the screen
        print('NEW CAR ADDED SUCCESSFULLY')
        print('RUNNING NUMBER: ' + car, 'TYPE: ' + cartype + cartype_name, 'CLASS: ' + carclass)
        print(railroad + railroad_name + ' HOME STATION: ' + station + station_name)
        print('AT: ' + station + station_name)
        return errors



    def chcarx(self, message):
        """changes basic details about a car.  the car class is copied down based on the
        car type.  the car is also linked to a railroad and to a home station.  other details
        for the car cannot be changed using this mechanism.
        """
        if self.show_access(message, 'CHCARX car;(^car type^);(^railroad^);(^home station^)', 'S') != 0:
            return

        errors = 0
        
        #car code-----------------------------------------------------------------------------------
        car, rc = self.extract_field(message, 0, 'CAR RUNNING NUMBER')
        if rc > 0:
            return
        
        #read the database and populate the fields
        t = (car,)
        sql = 'select car.cartype, car.railroad, car.home_station, car.station ' +\
              'from car where car.car = ? '             
        count, ds_cars = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            print('* CAR RUNNING NUMBER DOES NOT EXIST')
            return

        for row in ds_cars:
            cartype = row[0]
            railroad = row[1]
            home_station = row[2]
            station = row[3]

        #car type-----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            cartype = value

        t = (cartype,)
        sql = 'select carclass, name from cartype where cartype = ?'
        count, ds_cartypes = self.db_read(sql, t)
        if count < 0:
            return
        if count ==0:
            errors = errors + 1
            print('* CAR TYPE (' + cartype + ') DOES NOT EXIST')
        else:
            for row in ds_cartypes:
                carclass = row[0]
                cartype_name = row[1]
            
        #Railroad-----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            railroad = value
        
        rr = (railroad,)
        sql = 'select name from railroad where railroad = ?'
        count, ds_railroads = self.db_read(sql, rr)
        if count < 0:
            return
        if count == 0:
            errors = errors + 1
            print('* RAILROAD CODE (' + railroad + ') DOES NOT EXIST')
        else:
            for row in ds_railroads:
                railroad_name = row[0]

        #HomeStation--------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 3, '')
        if rc == 0:
            home_station = value
        
        stax = (home_station,)
        sql = 'select long_name from station where station = ?'
        count, ds_stations = self.db_read(sql, stax)
        if count < 0:
            return
        if count == 0:
            errors = errors + 1
            print('* HOME STATION CODE DOES NOT EXIST')
        else:
            for row in ds_stations:
                home_station_name = row[0]

        #and get the name of the current station
        stax2 = (station,)
        sql = 'select long_name from station where station = ?'
        count, ds_stations2 = self.db_read(sql, stax2)                                  #Rev 1
        if count < 0:
            return
        if count == 0:
            errors = errors + 1
        else:
            for row in ds_stations2:
                station_name = row[0]

        #build and store the new record-------------------------------------------------------------
        if errors != 0:
            return

        t = (cartype,
             carclass,
             railroad,
             home_station,
             car)
        sql = 'update car set cartype = ?, carclass = ?, railroad = ?, home_station = ? where car = ?'
        if self.db_update(sql, t) != 0:
            return
        
        #report the change to the screen
        print('CAR DETAILS CHANGED SUCCESSFULLY')
        print('RUNNING #: ' + car + 'TYPE: ' + cartype + cartype_name + 'CLASS: ' + carclass)
        print(railroad + railroad_name + ' HOME STATION: ' + home_station + home_station_name)
        print('AT: ' + station + station_name)
        return errors



    def maintc(self, message):
        """change maintenance status for cars.  the time to maintenance and works time
        can be amended up to the values held on the reference file.  only one or the other
        values can be set as both cannot have a value at the same time (ie a car is either
        in traffic and counting down to maintenance, or is in maintenance and counting
        down to going into traffic)
        """
        if self.show_access(message, 'MAINTC car;(time to maint);(works time)', 'S') != 0:
            return

        errors = 0
        maint_interval = 0
        works_time = 0
        
        #car code-----------------------------------------------------------------------------------
        car, rc = self.extract_field(message, 0, 'CAR RUNNING NUMBER')
        if rc > 0:
            return

        #read the database and populate the fields
        t = (car,)
        sql =   'select time_to_maint, time_in_maint from car where car.car = ? '
        count, ds_cars = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* CAR RUNNING NUMBER DOES NOT EXIST')
            return
        else:
            for row in ds_cars:
                time_to_maint = row[0]
                time_in_maint = row[1]

        t = ('CARWORKS',)
        sql = 'select value from parameter where name = ?'
        count, ds_param = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* DEFAULT WORKS TIME FOR CARS DOES NOT EXIST: SET-UP REQUIRED')
            return
        else:
            for row in ds_param:
                works_time = row[0]
        
        t = ('CARMAINT',)
        sql = 'select value from parameter where name = ?'
        count, ds_param = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* DEFAULT MAINTENANCE INTERVAL FOR CARS DOES NOT EXIST: SET-UP REQUIRED')
            return
        else:
            for row in ds_param:
                maint_interval = row[0]

        #time to maint------------------------------------------------------------------------------
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
            return

        if int(time_to_maint) > int(maint_interval):
            errors = errors + 1
            print('* MAINTENANCE INTERVAL OF CAR IS ' + str(maint_interval))

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

        if int(time_in_maint) > int(works_time):
            errors = errors + 1
            print('* MAINTENANCE OUTAGE OF CAR is ' + works_time)
                    
        #build and store the new record-------------------------------------------------------------
        if errors != 0:
            return

        t = (time_to_maint, time_in_maint, car)
        sql = 'update car set time_to_maint = ?, time_in_maint = ? where car = ?'
        if self.db_update(sql, t) != 0:
            return
        
        print('CAR MAINTENANCE DETAILS CHANGED SUCCESSFULLY')
        print(car + ' TO MAINT: ' + str(time_to_maint) + ' IN MAINT: ' + str(time_in_maint))
        return 



    def carxat(self, message):
        """relocate a car at a new station.  this is used for correcting cars that
        are not at the correct location.  cars in maintenance cannot be moved
        """
        if self.show_access(message, 'CARXAT car;^station^', 'N') != 0:
            return

        #car code-----------------------------------------------------------------------------------
        car, rc = self.extract_field(message, 0, 'CAR RUNNING NUMBER')
        if rc > 0:
            return

        t = (car,)
        sql =   'select station, time_in_maint, is_attached_set, block from car where car.car = ? '
        count, ds_cars = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* CAR RUNNING NUMBER DOES NOT EXIST')
            return
        else:
            for row in ds_cars:
                time_in_maint = row[1]
                attached_set = row[2]
                block = row[3]

        if attached_set != '':
            print('* CAR IS ATTACHED TO A SET, CANNOT BE MOVED')
            return

        #HomeStation--------------------------------------------------------------------------------
        station, rc = self.extract_field(message, 1, 'STATION CODE')
        if rc > 0:
            return

        if time_in_maint > 0:
            print('* CAR IN MAINTENANCE, CANNOT BE MOVED')
            return

        stax = (station,)
        sql = 'select long_name from station where station = ?'
        count, ds_stations = self.db_read(sql, stax)
        if count < 0:
            return

        if count == 0:
            print('* STATION CODE DOES NOT EXIST')
            return
        else:
            for row in ds_stations:
                stax_name = row[0]
                    
        #build and store the new record-------------------------------------------------------------
        t = (station, '0', '', car)
        sql = 'update car set station = ?, place_id = ?, train = ? where car = ?'
        if self.db_update(sql, t) != 0:
            return

        #if the car was attached to a block, move the rest of the block as well
        if block != '':
            t = (station, 0, '', block)
            sql = 'update car set station = ?, place_id = ?, train = ? where block = ?'
            if self.db_update(sql, t) != 0:
                return
        
        #report the change to the screen
        print('LOCATION OF CAR AT STATION CHANGED SUCCESSFULLY')
        print(car + ' AT: ' + station + + ' ' + stax_name)
        if block != '':
            data = (block,)                                                             #Rev 1
            sql = 'select car from car where block = ?'
            count, dummy = self.db_read(sql, data)
            if count < 0:
                return
            print(count-1 + 'ADDITIONAL CARS MOVED AS PART OF BLOCK')                   #Rev 1
        return



    def carxsp(self, message):
        """spot a car at a new location.  if the car is spotted at a maintenance location then the
        car will go into maintenance.  if the car is at an industry then it will be loaded (in
        turn, as only one car will load at a time)
        """
        if self.show_access(message, 'CARXSP car;^place^', 'N') != 0:
            return
        
        #car code-----------------------------------------------------------------------------------
        car, rc = self.extract_field(message, 0, 'CAR RUNNING NUMBER')
        if rc > 0:
            return

        t = (car,)
        sql = 'select station, time_to_maint, time_in_maint, ' +\
              'clean_dirty, is_attached_set, block from car where car.car = ? '
        count, ds_cars = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* CAR RUNNING NUMBER DOES NOT EXIST')
            return
        else:
            for row in ds_cars:
                station = row[0]
                time_to_maint = row[1]
                time_in_maint = row[2]
                car_cleaned  = row[3]
                attached_set = row[4]
                block        = row[5]

        if attached_set != '':
            print('* CAR IS ATTACHED TO A SET, CANNOT BE MOVED')
            return
 
        #Place---------------------------------------------------------------------------------------
        place, rc = self.extract_field(message, 1, 'PLACE')
        if rc > 0:
            return

        t = (station, place)
        sql = 'select place.id, place.name, place.place_type, ' +\
              'station.long_name from place, station ' +\
              'where place.station = ? and place.code = ? and station.station = place.station'
        count, ds_places = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* STATION/PLACE DOES NOT EXIST')
            return
        else:
            for row in ds_places:
                current_place_id = row[0]
                current_place_name = row[1]
                place_type = row[2]
                stax_name = row[3]
                    
        #if it is at a maintenance location, put it into maintenance--------------------------------
        if place_type == 'M':
            t = ('CARWORKS',)
            sql = 'select value from parameter where name = ?'
            count, ds_params = self.db_read(sql, t)
            if count < 0:
                return
            for row in ds_params:
                time_in_maint = int(row[0])
            time_to_maint = 0

        #if it is at a car cleaning location, clean the car-----------------------------------------
        if place_type == 'C':
            car_cleaned = 'C'
                
        #build and store the new record-------------------------------------------------------------
        t = (current_place_id, time_in_maint, time_to_maint, car_cleaned, car)
        sql = 'update car set place_id = ?, time_in_maint = ?, time_to_maint = ?, ' +\
              'clean_dirty = ? where car = ?'
        if self.db_update(sql, t) != 0:
            return

        #if the car was attached to a block, move the rest of the block as well
        if block != '':
            t = (current_place_id, time_in_maint, time_to_maint, car_cleaned, block)
            sql = 'update car set place_id = ?, time_in_maint = ?, time_to_maint = ?, ' +\
                  'clean_dirty = ? where block = ?'
            if self.db_update(sql, t) != 0:
                return
        
        #report the change to the screen
        print('CAR SPOTTED SUCCESSFULLY')
        print(car + 'AT: ' + station + stax_name + current_place_name)                        #Rev 1
        if block != '':
            data = (block,)
            sql = 'select car from car where block = ?'
            count, dummy = self.db_read(sql, data)
            if count < 0:
                return
            print( str(count-1) + ' ADDITIONAL CARS SPOTTED AS PART OF BLOCK')                   #Rev 1
        return



    def cleanx(self, message):
        """resets commodity and clean/dirty flag on a car.  this is a maintenance function
        """
        if self.show_access(message, 'CLEANX car', 'S') != 0:
            return

        #car code-----------------------------------------------------------------------------------
        car, rc = self.extract_field(message, 0, 'CAR RUNNING NUMBER')
        if rc > 0:
            return
        t = (car, '')

        #validate the change - check there is a record to change
        sql = 'select id, block from car where car = ? and station != ?'
        count, ds_cars = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            print('* RUNNING NUMBER DOES NOT EXIST OR CAR IS ON A TRAIN')
            return
        else:
            for row in ds_cars:
                block = row[1]
        
        #process the change
        t = ('', '', car)
        if self.db_update('update car set commodity = ?, clean_dirty = ? where car = ?',t) == 0:
            print('CAR ' + car + ' SET TO EMPTY AND CLEAN')

        #if the car was attached to a block, clean the rest of the block as well
        if block != '':
            data = ('', '', block)                                                       #Rev 1
            sql = 'update car set commodity = ?, clean_dirty = ? where block = ?'
            if self.db_update(sql, t) != 0:
                return
            t = (block,)
            sql = 'select car from car where block = ?'
            count, dummy = self.db_read(sql, data)
            if count < 0:
                return
            print(count-1 + 'ADDITIONAL CARS EMPTIED AND CLEANED AS PART OF BLOCK')  #Rev 1
        return


        
    def acarxb(self, message):
        """allocate a car to a block.  blocks allow groups of cars to be moved as a single unit
        by specifying a single car
        """
        if self.show_access(message, 'ACARXB car, block', 'N') != 0:
            return
    
        #car code-----------------------------------------------------------------------------------
        car, rc = self.extract_field(message, 0, 'CAR RUNNING NUMBER')
        if rc > 0:
            return

        t = (car,)
        sql =   'select car.car, car.time_in_maint, car.station, car.train, '    +\
                'car.block, is_attached_set  from car where car.car = ? '   
        count, ds_cars = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* CAR RUNNING NUMBER DOES NOT EXIST')
            return
        else:
            for row in ds_cars:
                time_in_maint = row[1]
                car_station = row[2]
                car_train   = row[3]
                block       = row[4]
                attached_set = row[5]

        if time_in_maint != 0:
            print('* CANNOT BE ASSIGNED TO BLOCK, CAR IN MAINTENANCE')
            return

        if attached_set != '':
            print('* CAR IS ALREADY ATTACHED TO A SET, CANNOT BE ADDED TO A BLOCK')
            return

        if block != '':
            print('* CAR IS ALREADY ATTACHED TO A BLOCK, DETACH FROM OTHER BLOCK FIRST')
            return
            
        if car_train != '':
            print('* CAR CANNOT BE ATTACHED TO A BLOCK WHEN ON A TRAIN')
            return

        #block code---------------------------------------------------------------------------------
        new_block, rc = self.extract_field(message, 1, 'BLOCK REFERENCE')
        if rc > 0:
            return

        t = (new_block,)
        sql =   'select car.block, car.station from car where car.block = ? '   
        count, ds_block = self.db_read(sql, t)
        if count < 0:
            return

        #block doesn't exist, so create it.  if it does exist, then check car is at the right place
        if count == 0:
            t = (new_block, car)
            if self.db_update('update car set block = ? where car = ?', t) == 0:
                print('CAR ' + car + ' ASSIGNED WITH NEW BLOCK REF: ' + new_block)
            return
        else:        
            for row in ds_block:
                block_station = row[1]
            if car_station == block_station:
                t = (new_block, car)
                if self.db_update('update car set block = ? where car = ?', t) == 0:
                    print('CAR ' + car + ' ATTACHED TO EXISTING BLOCK REF: ' + new_block)
                return
        return


    def xcarxb(self, message):
        """deallocate a car from a block.  it doesn't matter where the car is - it will stay at that
        place (or on a train).
        """
        if self.show_access(message, 'XCARXB car', 'N') != 0:
            return

        #car code-----------------------------------------------------------------------------------
        car, rc = self.extract_field(message, 0, 'CAR RUNNING NUMBER')
        if rc > 0:
            return

        t = (car, '')
        sql =   'select car.id from car where car.car = ? and car.block != ?'   
        count, dummy = self.db_read(sql, t)                                            #Rev 1
        if count < 0:
            return

        if count == 0:
            print('* CAR RUNNING NUMBER DOES NOT EXIST OR NOT ATTACHEDD TO BLOCK')
            return

        t = ('', car)
        if self.db_update('update car set block = ? where car = ?', t) == 0:
            print('CAR ' + car + ' REMOVED FROM BLOCK')
        return


    def dxcarx(self, message):
        """deletes a car from the database.  checks that it is not on a train, at a place or allocated
        to an order (ie car is not in use)
        """
        if self.show_access(message, 'DXCARX car', 'S') != 0:
            return
        #car code-----------------------------------------------------------------------------------
        car, rc = self.extract_field(message, 0, 'CAR RUNNING NUMBER')
        if rc > 0:
            return
        t = (car, )

        #validate the change - check there is a record to delete
        sql = 'select car, train, place_id, carorder, is_attached_set from car where car = ?'
        count, ds_cars = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            print('* RUNNING NUMBER DOES NOT EXIST OR CAR IS ON A TRAIN')
            return
        else:
            for row in ds_cars:
                if row[1].strip() != '':
                    print('* CAR IS ON A TRAIN AND CANNOT BE DELETED')
                    return
                if int(row[2]) != 0:
                    print('* CAR IS AT A PLACE AND CANNOT BE DELETED')
                    return
                if int(row[3]) != 0:
                    print('* CAR IS ON AN ORDER AND CANNOT BE DELETED')
                    return
                if row[4] != '':
                    print('* CAR IS ATTACHED TO A SET AND CANNOT BE DELETED')
                    return
                
        #process the change
        if self.db_update('delete from car where car = ?', t) == 0:
            print('CAR ' + car + ' SUCCESSFULLY DELETED')
        return



    def acarxs(self, message):
        """allocates a car to a set.  the loco it is being attached to must be at the same station
        and not on a train.  the loco must be a Multiple Set loco, and the car must be a Multiple
        Set car.  Once the sets are combined the car will be processed with the loco
        """
        if self.show_access(message, 'ACARXS car;^loco^', 'N') != 0:
            return

        #car code-----------------------------------------------------------------------------------
        car, rc = self.extract_field(message, 0, 'CAR RUNNING NUMBER')
        if rc > 0:
            return

        t = (car,)
        sql =   'select car.car, cartype.oper_mode, car.station, car.train, '    +\
                'car.block, car.is_attached_set from car, cartype where car.car = ? and '   +\
                'cartype.cartype = car.cartype'
        count, ds_cars = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* CAR RUNNING NUMBER DOES NOT EXIST')
            return
        else:
            for row in ds_cars:
                car_oper_mode        = row[1]
                car_station          = row[2]
                car_train            = row[3]
                car_block            = row[4]
                attached_set         = row[5]

        if car_train != '':
            print('* CAR IS ON A TRAIN AND CANNOT BE ALLOCATED TO A SET')
            return
        if car_block != '':
            print('* CAR IS ATTACHED TO A BLOCK AND CANNOT BE ALLOCATED TO A SET')
            return
        if car_oper_mode != 'M':
            print('* CAR IS NOT CAPABLE OF FORMING A SET')
            return
        if car_train != '':
            print('* CAR IS ON A TRAIN AND CANNOT BE ALLOCATED TO A SET')
            return
        if attached_set != '':
            print('* CAR IS ALREADY ATTACHED TO ANOTHER SET')
            return

        #loco code
        loco, rc = self.extract_field(message, 1, 'LOCO RUNNING NUMBER')
        if rc > 0:
            return

        t = (loco,)
        sql =   'select locomotive.loco, locotype.oper_mode, locomotive.station, ' +\
                'locomotive.train from locomotive, locotype where locomotive.loco = ? and '   +\
                'locotype.locotype = locomotive.locotype'
        count, dummy = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* LOCOMOTIVE RUNNING NUMBER DOES NOT EXIST')
            return

        for row in ds_cars:
            loco_oper_mode    = row[1]
            loco_station      = row[2]
            loco_train        = row[3]

        if loco_train != '':
            print('* LOCO IS ON A TRAIN AND CANNOT BE ALLOCATED A SET')
            return
        if loco_oper_mode != 'M':
            print('* LOCO IS NOT CAPABLE OF FORMING A SET')
            return
        if loco_station != car_station:
            print('* LOCO AND CAR ARE NOT AT THE SAME STATION')
            return

        #assign the car to the set
        t = ('', 0, loco, car)
        sql = 'update car set station = ?, place_id = ?, is_attached_set = ? where car = ?'
        if self.db_update(sql,t) != 0:
            return
    
        print('CAR ' + car + ' ATTACHED TO LOCO ' + loco + ' AS A SET')
        return



    def xcarxs(self, message):
        """de-allocates a car from a set.  the loco it is being attached to must be at a station
        and not on a train.  the car is given the same station as the loco
        """
        if self.show_access(message, 'XCARXS car', 'N') != 0:
            return

        #car code-----------------------------------------------------------------------------------
        car, rc = self.extract_field(message, 0, 'CAR RUNNING NUMBER')
        if rc > 0:
            return

        t = (car,)
        sql = 'select is_attached_set from car where car = ?'
        count, ds_cars = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            print('* CAR RUNNING NUMBER DOES NOT EXIST')
            return
        for row in ds_cars:
            attached = row[0]

        t = (attached,)
        sql = 'select loco, train, station from locomotive where loco = ?'
        count, ds_locos = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            print('* CAR IS NOT ATTACHED TO A SET')
            return

        for row in ds_locos:
            if row[1] != '':
                print('* CAR IS ON A TRAIN AND CANNOT BE DETACHED')
                return
            station = row[2]
            loco = row[0]
            train = row[1]

        if train.strip() != '':
            print('* CANNOT DETACH CAR IF LOCO IS ON A TRAIN')
            return
        
        #detach the car from the set
        t = (station, 0, '', car)
        sql = 'update car set station = ?, place_id = ?, is_attached_set = ? where car = ?'
        if self.db_update(sql,t) != 0:
            return

        t = (station,)
        sql = 'select long_name from station where station = ?'
        count, ds_stax = self.db_read(sql, t)
        if count < 0:
            return
        for row in ds_stax:
            station_name = row[0]
    
        print('CAR ' + car + ' DETACHED FROM SET ' + loco + ' AT ' + station + station_name)
        return



    def mtyord(self, message):
        """allocates up to 5 cars (or cars on a block) to an order.  check that the cars can be
        allocated (ie not already allocated to an order and not in maintenance) and that they can
        fulfil the order (loading codes agree; is clean if clean/dirty flag set).  set the carorder
        on the car and reduce the carcount on the order by the number of cars attached.
        """
        if self.show_access(message, 'MTYORD order;car;(car);... [up to 5 cars]', 'N') != 0:
            return

        #order code---------------------------------------------------------------------------------
        order, rc = self.extract_field(message, 0, 'CAR EMPTY ORDER NUMBER')
        if rc > 0:
            return

        t = (order, 'E', 'O')
        sql = 'select id, requires, loading, unloading, clean_cars, warehouse, status from waybill ' +\
              'where id = ? and type = ? and status = ?'
        count, ds_orders = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            print('* EMPTY ORDER NUMBER DOES NOT EXIST')
            return
        for row in ds_orders:
            requires = row[1]
            loading  = row[2]
            unloading = row[3]
            cleancar = row[4]
            warehouse = row[5]
            status = row[6]

        #car codes ---------------------------------------------------------------------------------
        car_list = {}
        car_count = 0
        field = 1

        while rc == 0:
            value, rc = self.extract_field(message, field, '')
            if rc == 0:
                car_count = car_count + 1
                car_list[car_count] = value
                field = field + 1

                t = (car_list[car_count], '')
                sql = 'select block, car from car where car = ? and block != ?'
                count, ds_cars = self.db_read(sql, t)
                if count < 0:
                    return

                if count > 0:
                    for row in ds_cars:
                        block = row[0]

                        t1 = (block, car_list[car_count])
                        sql = 'select car, block from car where block = ? and car != ?'
                        count, ds_block = self.db_read(sql, t1)
                        if count < 0:
                            return
                        for row1 in ds_block:
                            car_count = car_count + 1
                            car_list[car_count] = row1[0]
        
            
        #validate the cars--------------------------------------------------------------------------
        for i in car_list:
            if self.check_car_on_order(car_list[i], loading, unloading, cleancar) != 0:
                return

        outstanding = int(requires) - int(car_count)
        if outstanding < 0:
            print('* TOO MANY CARS ASSIGNED TO EMPTY CAR ORDER ' + int(car_count) + int(requires))
            return

        t = (warehouse,)
        sql = 'select warehouse.industry, station.short_name ' +\
              'from warehouse, place, station ' +\
              'where warehouse.id = ? and place.industry = warehouse.industry ' +\
              'and place.station = station.station'
        count, ds_industry = self.db_read(sql, t)
        if count < 0:
            return
        for row in ds_industry:
            industry = row[0]
            station_name = row[1]
        
        print('CARS ATTACHED TO ORDER ' + order + ' FOR ' + industry + station_name)

        for i in car_list:
            t = (car_list[i],)
            sql = 'select car, station, train from car where car = ?'
            count, ds_cars = self.db_read(sql, t)
            if count < 0:
                return
            for row in ds_cars:
                print('CAR:' + row[0] + 'CURRENTLY AT:' + row[1] + row[2])
                t2 = (order, row[0])
                sql = 'update car set carorder = ? where car = ?'
                if self.db_update(sql, t2) != 0:
                    return

        if outstanding == 0:
            status = 'I'
        else:
            status = 'O'
        t = (outstanding, status, order)
        sql = 'update waybill set requires = ?, status = ? where id = ?'
        if self.db_update(sql, t) != 0:
            return

        if status == 'I':
            print('EMPTY CAR ORDER FULFILLED FOR ORDER ' + order)
        else:
            print('EMPTY CAR ORDER: ' + str(order) + ' CARS OUTSTANDING: ' + str(outstanding))
        return



    def check_car_on_order(self, car, loading, unloading, cleancar):
        """routine to check an individual car can be assigned to satisfy an empty order
        """
        rc = 0

        t = (car,)
        sql = 'select car.time_in_maint, car.commodity, ' +\
              'car.clean_dirty, car.carorder, cartype.loading, cartype.unloading, ' +\
              'car.is_attached_set from car, cartype where car.car = ? and car.cartype = cartype.cartype'
        count, ds_cars = self.db_read(sql, t)
        if count < 0:
            return 99
        if count == 0:
            print('* CAR ' + car + ' NOT FOUND')
            return 99
        for row in ds_cars:
            if row[0] != 0:
                print('* CAR ' + car + ' IS IN MAINTENANCE AND CANNOT BE ASSIGNED')
                return 20
            if row[1].strip() != '':
                print('* CAR ' + car + ' IS ALREADY LOADED AND CANNOT BE ASSIGNED ' + row[1])
                return 21
            if row[2].strip() != 'C' and cleancar == 'Y':
                print('*CAR ' + car + ' IS DITRY AND CLEAN CARS ARE REQUIRED')
                return 22
            if row[3] != 0:
                therr = row[3]
                there = str(therr)
                print('* CAR ' + car + ' ALREADY ASSIGNED ON ORDER ' + there)
                return 23
            if row[4] != loading:
                print('* CAR ' + car + ' NOT SUITABLE FOR LOADING (' + loading + ' REQUIRED)')
                return 24
            if row[5] != unloading:
                print('* CAR ' + car + ' NOT SUITABLE FOR UNLOADING (' + unloading + ' REQUIRED)')
                return 25
            if row[6] != '':
                print('* CAR ' + car + ' IS ATTACHED TO A SET ')
                return 26
            
        return rc
                


    def lonway(self, message):
        """provides a list of empty cars en route to a station or place.
        """
        if self.show_access(message, 'LONWAY (^station^);(^industry^)', 'R') != 0:
            return

        #get the parameters for the report        
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            filter_station = value                                                    # Rev 1
        else:
            filter_station = '*'

        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            filter_industry = value                                                   #Rev 1
        else:
            filter_industry = '*'

        # build the column titles
        comm_size = 78 - self.railsize - self.carxsize - self.staxsize - self.plaxsize - 32
        if comm_size < 0:
            comm_size = 1
        titles = self.x_field('RAILROAD==', self.railsize) +  ' ' +\
                 self.x_field('CAR=======', self.carxsize) +  ' ' +\
                 self.x_field('STATION/PLACE============', self.staxsize + self.plaxsize + 12) +  ' ' +\
                 self.x_field('DESTINATN=', 10) +  ' ' +\
                 self.x_field('COMMODITY===================',comm_size) + ' ' +\
                 self.x_field('CURRENT', 10)

        #get the extract data
        data = ('',)
        sql = 'select car.railroad, car.car, place.station, place.code, ' +\
              'warehouse.industry, warehouse.destination, warehouse.commodity, commodity.name, car.train, car.station ' +\
              'from car, waybill, warehouse, place, commodity ' +\
              'where car.carorder != 0 ' +\
              'and car.commodity == ? ' +\
              'and car.carorder = waybill.id ' +\
              'and waybill.warehouse = warehouse.id ' +\
              'and place.industry = warehouse.industry ' +\
              'and warehouse.commodity = commodity.commodity ' +\
              'order by place.station, place.code, car.railroad, car.car'

        count, ds_cars = self.db_read(sql, data)
        if count < 0:
            return

        #process the data
        line_count = 0
        for row in ds_cars:
            if line_count == 0:
                print(titles)
            railroad = row[0]
            car = row[2]
            stax = row[2]
            plax = row[3]
            industry = row[4]
            staxplax = stax + '/' + plax + ' ' + industry
            destination = row[5]
            commodity = row[6]
            commodity_name = row[7]
            train = row[8]
            car_at = row[9]
            current_loc = car_at + train
            current_loc = current_loc.strip()
            if stax == filter_station or filter_station == '*':
                if industry == filter_industry or filter_industry == '*':
                    print(self.x_field(railroad, self.railsize) + " " +
                           self.x_field(car, self.carxsize) + " " +
                           self.x_field(staxplax, self.staxsize + self.plaxsize + 12) + " " +
                           self.x_field(destination, 10) + " " +
                           self.x_field(commodity, self.commsize) + " " +
                           self.x_field(commodity_name, comm_size - self.commsize) + " " +
                           self.x_field(current_loc, 10))
                    line_count = line_count + 1
                    if line_count > 20:
                        line_count = 0
                        reply = raw_input('+')
                        if reply == 'x':
                            break
        print(' ** END OF DATA: ' + str(count) + ' RECORDS DISPLAYED **')         
        return

        

        
    def lacars(self, message):
        """lists activity details about cars.  can be filtered by types, railroad, or station.  this
        list shows cars in traffic (ie not maintenance) and can be filtered by station/class.  also
        indicates clean/dirty and loaded/unloaded
        """
        if self.show_access(message, 'LACARS (^car class^);(^station^)', 'R') != 0:
            return

        #get the parameters for the report        
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            filter_class = value
        else:
            filter_class = '*'

        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            filter_stax = value
        else:
            filter_stax = '*'

        # build the column titles
        place_size = 79 - self.railsize - self.carxsize - self.classize - self.staxsize - self.plaxsize - self.commsize - 39
        titles = self.x_field('RAILROAD==', self.railsize) + ' ' +\
                 self.x_field('CAR=======', self.carxsize) + ' ' +\
                 self.x_field('CLASS=====', self.classize) + ' ' +\
                 self.x_field('STATION======================', self.staxsize + 9) + ' ' +\
                 self.x_field('PLACE=========================', place_size) + ' ' +\
                 self.x_field('COMMODITY=', self.commsize) + ' ' +\
                 self.x_field('DESTINATION', 10) + ' ' +\
                 self.x_field('C', 1) + ' ' +\
                 self.x_field('BLOCK=====', 5) + ' ' +\
                 self.x_field('MAINT', 5)

        #get the extract data
        sql = 'select car.railroad, car.car, car.carclass, car.station, station.short_name, ' +\
              'car.train, car.commodity, car.clean_dirty, car.block, car.place_id, car.carorder, ' +\
              'car.time_to_maint, car.is_attached_set ' +\
              'from car left outer join station on car.station = station.station order by car.railroad, car.car'
        count, ds_cars = self.db_read(sql, '')
        if count < 0:
            return

        #process the data
        line_count = 0
        counter = 0
        for row in ds_cars:
            clas = row[2]
            stax = row[3]
            if stax == '':
                station_detail = 'ON TRAIN'
            else:
                station_detail = stax + ' ' + row[4]
            train = row[5]
            place = row[9]
            car_order = row[10]
            block = row[8]
            time_to_maint = row[11]
            place_name = ''
            destination = ''
            attached_set = row[12]
            if (clas == filter_class) or (filter_class == '*'):
                if (stax == filter_stax) or (filter_stax == '*'):
                    if line_count == 0:
                        print(titles)
                    if place != 0:
                        data = (place,)
                        sql = 'select name, code from place where id = ?'
                        pcount, ds_places = self.db_read(sql, data)
                        if pcount < 0:                                                  #Rev 1
                            return
                        for xrow in ds_places:
                            place_name = xrow[0]
                            place_code = xrow[1]
                        place_name = place_code + ' ' + place_name
                        data = (car_order,)
                        sql = 'select destination from waybill where id = ?'
                        wcount, ds_orders = self.db_read(sql, data)
                        if wcount < 0:                                                  #Rev 1
                            return
                        for wrow in ds_orders:
                            destination = wrow[0]
                    if stax == '':
                        if attached_set == '':
                            place_name = train
                        else:
                            place_name = train + ' (' + attached_set + ')'
                    print(self.x_field(row[0], self.railsize) + " " +
                           self.x_field(row[1], self.carxsize) + " " +
                           self.x_field(row[2], self.classize) + " " +
                           self.x_field(station_detail, self.staxsize + 9) + " " +
                           self.x_field(place_name, place_size) + " " +
                           self.x_field(row[6], self.commsize) + " " +
                           self.x_field(destination, 10) + " " +
                           self.x_field(row[7], 1) + " " +
                           self.x_field(block, 5) + " " +
                           self.x_field(time_to_maint,5, 'R'))
                    line_count = line_count + 1
                    counter = counter + 1
                    if line_count > 20:
                        line_count = 0
                        reply = raw_input('+')
                        if reply == 'x':
                            break
        print(' ** END OF DATA: ' + str(counter) + ' RECORDS DISPLAYED **')         
        return



    def lmtcar(self, message):
        """lists activity details about cars.  can be filtered by types, railroad, or station.  this
        list shows cars in traffic (ie not maintenance) and can be filtered by station/class.  also
        indicates clean/dirty and loaded/unloaded
        """
        if self.show_access(message, 'LMTCAR (^area^);(^station^);(^car class^)', 'R') != 0:
            return

        #get the parameters for the report        
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            filter_area = value
        else:
            filter_area = '*'

        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            filter_stax = value
        else:
            filter_stax = '*'

        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            filter_class = value
        else:
            filter_class = '*'
            
        # build the column titles
        titles = self.x_field('RAILROAD==', self.railsize) + ' ' +\
                 self.x_field('AREA======', self.areasize) + ' ' +\
                 self.x_field('STATION===', self.staxsize) + ' ' +\
                 self.x_field('NAME======', 8)             + ' ' +\
                 self.x_field('PLACE=====', self.plaxsize) + ' ' +\
                 self.x_field('TYPE======', self.cartsize) + ' ' +\
                 self.x_field('CAR=======', self.carxsize) + ' ' +\
                 self.x_field('C', 1) + ' ' +\
                 self.x_field('BLOCK', 8) + ' ' +\
                 self.x_field('LOADING===', self.loadsize) + ' ' +\
                 self.x_field('UNLOAD====', self.loadsize)

        #get the extract data
        data = ('', 0)
        sql = 'select car.railroad, station.area, car.station, car.place_id, car.cartype, ' +\
              'car.car, car.clean_dirty, car.block, cartype.loading, cartype.unloading, car.carclass, station.short_name ' +\
              'from car, station, cartype ' +\
              'where car.station = station.station and cartype.cartype = car.cartype ' +\
              'and car.station != ? and car.carorder = ? order by car.car'
        count, ds_cars = self.db_read(sql, data)
        if count < 0:
            return

        #process the data
        line_count = 0
        counter = 0
        for row in ds_cars:
            railroad = row[0]
            area = row[1]
            station = row[2]
            place = row[3]
            cartype = row[4]
            car = row[5]
            clean = row[6]
            block = row[7]
            loading = row[8]
            unloading = row[9]
            carclass = row[10]
            short_name = row[11]
            if carclass == filter_class or filter_class == '*':
                if station == filter_stax or filter_stax == '*':
                    if area == filter_area or filter_area == '*':
                        if line_count == 0:
                            print(titles)
                        place_id = '          '
                        data = (place,)
                        sql = 'select code from place where id = ?'
                        pcount, ds_places = self.db_read(sql, data)
                        if pcount < 0:                                                    #Rev 1
                            return
                        for prow in ds_places:
                            place_id = prow[0]
                        print(self.x_field(railroad, self.railsize) + " " +
                               self.x_field(area, self.areasize) + " " +
                               self.x_field(station, self.staxsize) + " " +
                               self.x_field(short_name, 8) + " " +
                               self.x_field(place_id, self.plaxsize) + " " +
                               self.x_field(cartype, self.cartsize) + " " +
                               self.x_field(car, self.carxsize) + " " +
                               self.x_field(clean, 1) + " " +
                               self.x_field(block, 8) + " " +
                               self.x_field(loading, self.loadsize) + " " +
                               self.x_field(unloading, self.loadsize))
                        line_count = line_count + 1
                        counter = counter + 1
                        if line_count > 20:
                            line_count = 0
                            reply = raw_input('+')
                            if reply == 'x':
                                break
        print(' ** END OF DATA: ' + str(counter) + ' RECORDS DISPLAYED **')         
        return


    def licars(self, message):
        """list basic details about cars, sortable by various orders and can be filtered by type,
        railroad or station
        """
        if self.show_access(message, 'LICARS (sort[0/1/2/3]);(^car class^);(^railroad^);(^station^)', 'R') != 0:
            return

        #get the parameters for the report        
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            filter_class = value
        else:
            filter_class = '*'

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
        station_size = 74 - self.carxsize - self.cartsize - self.classize - 26 - self.locosize
        if station_size > self.staxsize + 30:
            station_size = self.staxsize + 30
        titles = self.x_field('CAR=======', self.carxsize) +  ' ' +\
                 self.x_field('TYPE======', self.cartsize) +  ' ' +\
                 self.x_field('CLASS=====', self.classize) +  ' ' +\
                 self.x_field('RAILROAD==', self.railsize) +  ' ' +\
                 self.x_field('HOME==================================', station_size) + ' ' +\
                 self.x_field('MAINT', 5, 'R') +  ' ' +\
                 self.x_field('RPAIR', 5, 'R') + ' ' +\
                 self.x_field('BLOCK=====', 10) + ' ' +\
                 self.x_field('SET=======', self.locosize)

        #get the extract data
        if sort_order == '1':
            sql = 'select car.car, car.cartype, car.carclass, car.railroad, '  + \
                  'car.home_station, station.long_name, car.time_to_maint, '  + \
                  'car.time_in_maint, car.block, car.is_attached_set from car, station '  + \
                  'where car.home_station = station.station order by car.railroad, car.car'
        elif sort_order == '2':
            sql = 'select car.car, car.cartype, car.carclass, car.railroad, '  + \
                  'car.home_station, station.long_name, car.time_to_maint, '  + \
                  'car.time_in_maint, car.block, car.is_attached_set from car, station '  + \
                  'where car.home_station = station.station order by car.class, car.car'
        elif sort_order == '3':
            sql = 'select car.car, car.cartype, car.carclass, car.railroad, '  + \
                  'car.home_station, station.long_name, car.time_to_maint, '  + \
                  'car.time_in_maint, car.block, car.is_attached_set from car, station '  + \
                  'where car.home_station = station.station order by car.station, car.car'
        else:
            sql = 'select car.car, car.cartype, car.carclass, car.railroad, '  + \
                  'car.home_station, station.long_name, car.time_to_maint, '  + \
                  'car.time_in_maint, car.block, car.is_attached_set from car, station '  + \
                  'where car.home_station = station.station order by car.car'

        count, ds_cars = self.db_read(sql, '')
        if count < 0:
            return

        #process the data
        line_count = 0
        counted = 0
        for row in ds_cars:
            carc = row[2]
            rail = row[3]
            stax = row[4]
            if ((carc == filter_class) or (filter_class == '*')):
                if ((rail == filter_rail) or (filter_rail == '*')):
                    if ((stax == filter_stax) or (filter_stax == '*')):
                        if line_count == 0:
                            print(titles)
                        print(self.x_field(row[0], self.carxsize) + ' ' +
                               self.x_field(row[1], self.cartsize) + ' ' +
                               self.x_field(row[2], self.classize) + ' ' +
                               self.x_field(row[3], self.railsize) + ' ' +
                               self.x_field(row[4] + '(' + row[5] + ')', station_size) + ' ' +
                               self.x_field(row[6], 5, 'R') + ' ' +
                               self.x_field(row[7], 5, 'R') + ' ' +
                               self.x_field(row[8], 10) + ' ' +
                               self.x_field(row[9], self.locosize))
                        line_count = line_count + 1
                        counted = counted + 1
                        if line_count > 22:
                            line_count = 0
                            reply = raw_input('+')
                            if reply == 'x':
                                break
        print(' ** END OF DATA: ' + str(counted) + ' RECORDS DISPLAYED **')         
        return



    def prcars(self, message, Params):
        """lists activity details about cars.  can be filtered by types, railroad, or station.  this
        list shows cars in traffic (ie not maintenance) and can be filtered by station/class.  also
        indicates clean/dirty and loaded/unloaded
        """
        if self.show_access(message, 'PRCARS (sort[0/1/2/3]);(^car class^);(^railroad^);(^station^)', 'R') != 0:
            return

        #get the parameters for the report        
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            filter_class = value
        else:
            filter_class = '*'

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
        station_size = 74 - self.carxsize - self.cartsize - self.classize - 26 - self.locosize
        if station_size > self.staxsize + 30:
            station_size = self.staxsize + 30
        titles = self.x_field('CAR=======', self.carxsize) +  ' ' +\
                 self.x_field('TYPE======', self.cartsize) +  ' ' +\
                 self.x_field('CLASS=====', self.classize) +  ' ' +\
                 self.x_field('RAILROAD==', self.railsize) +  ' ' +\
                 self.x_field('HOME==================================', station_size) + ' ' +\
                 self.x_field('MAINT', 5, 'R') +  ' ' +\
                 self.x_field('RPAIR', 5, 'R') + ' ' +\
                 self.x_field('BLOCK=====', 10) + ' ' +\
                 self.x_field('SET=======', self.locosize)

        #get the extract data
        if sort_order == '1':
            sql = 'select car.car, car.cartype, car.carclass, car.railroad, '  + \
                  'car.home_station, station.long_name, car.time_to_maint, '  + \
                  'car.time_in_maint, car.block, car.is_attached_set from car, station '  + \
                  'where car.home_station = station.station order by car.railroad, car.car'
        elif sort_order == '2':
            sql = 'select car.car, car.cartype, car.carclass, car.railroad, '  + \
                  'car.home_station, station.long_name, car.time_to_maint, '  + \
                  'car.time_in_maint, car.block, car.is_attached_set from car, station '  + \
                  'where car.home_station = station.station order by car.class, car.car'
        elif sort_order == '3':
            sql = 'select car.car, car.cartype, car.carclass, car.railroad, '  + \
                  'car.home_station, station.long_name, car.time_to_maint, '  + \
                  'car.time_in_maint, car.block, car.is_attached_set from car, station '  + \
                  'where car.home_station = station.station order by car.station, car.car'
        else:
            sql = 'select car.car, car.cartype, car.carclass, car.railroad, '  + \
                  'car.home_station, station.long_name, car.time_to_maint, '  + \
                  'car.time_in_maint, car.block, car.is_attached_set from car, station '  + \
                  'where car.home_station = station.station order by car.car'
        count, ds_cars = self.db_read(sql, '')
        if count < 0:
            return
        self.temp = {}

        #process the data
        counter = 0
        for row in ds_cars:
            carc = row[2]
            rail = row[3]
            stax = row[4]
            if ((carc == filter_class) or (filter_class == '*')):
                if ((rail == filter_rail) or (filter_rail == '*')):
                    if ((stax == filter_stax) or (filter_stax == '*')):
                        print_line =  (self.x_field(row[0], self.carxsize) + ' ' +\
                               self.x_field(row[1], self.cartsize) + ' ' +\
                               self.x_field(row[2], self.classize) + ' ' +\
                               self.x_field(row[3], self.railsize) + ' ' +\
                               self.x_field(row[4] + '(' + row[5] + ')', station_size) + ' ' +\
                               self.x_field(row[6], 5, 'R') + ' ' +\
                               self.x_field(row[7], 5, 'R') + ' ' +\
                               self.x_field(row[8], 10) + ' ' +\
                               self.x_field(row[9], self.locosize))
                        self.temp[counter] = print_line
                        counter = counter + 1

        #report the extracted data
        self.print_report (titles = titles,
                           report_id = 'PRCARS',
                           report_name = 'LIST OF CARS',
                           Params = Params)
        return



    def Z011_maintain_car_countdown(self, Flash, Params):
        """read all cars not in maintenance.  Each day reduce the
        time_to_maintenance by 1.  A car is NOT in maintenance if time_in_maint = 0
        """
        message = ''
        time_to_maint = 90                                                            #Rev 1

        sql = 'update car set time_to_maint = time_to_maint - 1 where time_in_maint = 0'
        if self.db_update(sql, '') != 0:
            return

        #for each car getting near maintenance, report
        sql = 'select car, time_to_maint, time_in_maint from car where time_in_maint = 0 ' +\
              'and time_to_maint < 6'
        count, data = self.db_read(sql, '')
        if count < 0:
            return

        for row in data:
            car = row[0]
            time_to_maint = row[1]
        
            #time to maintenance less than 5, so report
            if int(time_to_maint) < 6:
                if int(time_to_maint) == 5:
                    message = car + '  HAS 5 DAYS TO MAINTENANCE'
                if int(time_to_maint) == 4:
                    message = car + '  HAS 4 DAYS TO MAINTENANCE'
                if int(time_to_maint) == 3:
                    message = car + '  HAS 3 DAYS TO MAINTENANCE'
                if int(time_to_maint) == 2:
                    message = car + '  HAS 2 DAYS TO MAINTENANCE'
                if int(time_to_maint) == 1:
                    message = car + '  HAS 1 DAYS TO MAINTENANCE'
                if int(time_to_maint) == 0:
                    message = car + '  *** DUE MAINTENANCE ***'
                if int(time_to_maint) < 0:
                    message = car + '  *** OVERDUE MAINTENANCE ***'
                    time_to_maint = '    0'
                message = 'CAR ' + message
                Flash.Z003_generate_flash_message(message, Params)
                print(Params.get_date() + ' ' + Params.get_time() + 'Z011:' + message)
        return



    def Z012_works_cars(self, Flash, Params):
        """if a car is in works (time_in_main > 0) then reduce the time in maintenance by 1.
        if it falls to zero, then it can be released back into traffic.  in this case get the
        default value for the time to works from the parameter file
        """
        sql = 'update car set time_in_maint = time_in_maint - 1 where time_in_maint > 0'
        if self.db_update(sql, '') != 0:
            return

        sql = 'select value from parameter where name = ?'
        t = ('CARMAINT',)
        count, ds_params = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            print('NO DEFAULT VALUE SET FOR CAR MAINTENANCE, 90 DAYS ASSUMED')
            maint_interval = 90
        else:
            for row in ds_params:
                maint_interval = row[0]

        t = ()
        sql = 'select car.id, car.car from car where car.time_in_maint = 0 '    +\
              'and car.time_to_maint = 0'
        count, ds_cars = self.db_read(sql, t)
        if count < 1:
            return

        for row in ds_cars:
            t = (maint_interval, row[0])
            carcode = row[1]
            sql = 'update car set time_to_maint = ? where id = ?'
            self.db_update(sql, t)
            message = 'CAR ' + carcode + ' MAINTENANCE COMPLETE; READY FOR TRAFFIC'
            t = (message,)
            Flash.Z003_generate_flash_message(message, Params)
            print(Params.get_date() + ' ' + Params.get_time() + 'Z012: CAR ' + carcode + ' RETURNING TO TRAFFIC')
        return



    def Z013_select_car_for_loading(self, Params):
        """reads all industry places where car id is zero (no car being loaded or unloaded).
        find the oldest incomplete, empty carorder at that place (lookup via place/warehouse/
        carorder).  find a car matching on that carorder.  update the place with the car id to
        show it is being loaded.  remove the carorder id from the car.  check the remaining
        cars for the carorder id - if no cars are now using taht id, set the carorder status
        to C for complete
        """

        #get a list of places not currently loading/unloading which have orders
        t = ('I', 0, '', 'I')
        sql = 'select waybill.id, place.id, place.industry, waybill.commodity, ' +\
              'waybill.type, waybill.origin, waybill.destination ' +\
              'from place, waybill ' +\
              'where place.place_type = ? and (place.car_id = ? or place.car_id = ?) ' +\
              'and (waybill.origin = place.industry or waybill.destination = place.industry) ' +\
              'and waybill.status = ? ' +\
              'order by waybill.timestamp'
        count, ds_orders = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            return

        for row in ds_orders:
            place = row[1]
            industry = row[2]
            commodity = row[3]
            order_type = row[4]
            origin = row[5]
            destination = row[6]

            #get an unloaded car at that place
            load_or_unload = ''
            if order_type == 'E' and (industry == origin):
                t = ('', place)
                load_or_unload = 'loading'
            if order_type == 'W' and (industry == destination):
                t = (commodity, place)
                load_or_unload = 'unloading'

            if load_or_unload != '':
                sql = 'select car.id, car.car from car where commodity = ? and place_id = ? limit 1'
                count_cars, ds_cars = self.db_read(sql, t)
                if count_cars < 0:
                    return
                for row2 in ds_cars:
                    carid = row2[0]
                    carcode = row2[1]

                    #set the place to be loading that car
                    t = (carid, place)
                    sql = 'update place set car_id = ? where id = ?'
                    if self.db_update(sql, t) != 0:
                        return
                    print(Params.get_date() + ' ' + Params.get_time() +
                           'Z013: car ' + carcode + ' set for ' + load_or_unload + ' at ' + industry)
        return



    def Z015_car_loading(self, Flash, Params):
        """read industries and get a list of where cars are being loaded.  read commodity and add
        the amount in loadingrate to the loadedweight.  if the loadedweight is greater than the
        capacity then reduce the loadedweight to capacity.  reduce the amount forloading in the
        warehouse by the amount actually loaded into the car.  if the loadedweight = capacity for
        the car, remove the car from being loaded and create a waybill order (set to outstanding)
        for the car and send a flash message
        """
        loadingrate = 0
        sql =   'select car.car, car.weight_loaded, waybill.commodity, commodity.loading_rate, ' +\
                'commodity.unloading_rate, cartype.capacity, car.id, place.industry, ' +\
                'waybill.origin, waybill.destination, waybill.type, place.id, waybill.id ' +\
                'from car, place, waybill, commodity, cartype ' +\
                'where (place.industry = waybill.origin or place.industry = waybill.destination) ' +\
                'and place.car_id = car.id ' +\
                'and waybill.commodity = commodity.commodity ' +\
                'and car.cartype = cartype.cartype ' +\
                'and car.carorder = waybill.id'
        count, ds_places = self.db_read(sql, '')
        if count < 0:
            return
        for row in ds_places:
            carcode = row[0]
            loaded = row[1]
            commodity = row[2]
            loadingrate = row[3]
            unloadingrate = row[4]
            capacity = row[5]
            carid = row[6]
            industry = row[7]
            origin = row[8]
            destination = row[9]
            place = row[11]
            waybill_id = row[12]

            in_storage = 0                                                     #Rev 1 start
            sql = 'select id, in_storage from warehouse where industry = ?'    #plus changes
            data = (industry,)
            count, ds_warehouse = self.db_read(sql, data)
            if count < 0:
                return
            for warehouse in ds_warehouse:
                warehouse_id = warehouse[0]
                in_storage = warehouse[1]
            
            #check we wont load more than we have on site
            if in_storage < loadingrate:
                loadingrate = in_storage

            if industry == origin:
                loaded = loaded + loadingrate
                if loaded > capacity:
                    loaded = capacity
                    in_storage = in_storage - loaded
                    if in_storage < 0:
                        in_storage = 0
                    sql = 'update warehouse set in_storage = ? where id = ?'
                    data = (in_storage, warehouse_id)
                    self.db_update(sql, data)                                   #Rev 1 end
                    t = (commodity, loaded, carid)
                    sql = 'update car set commodity = ?, weight_loaded = ? where car.id = ?'
                    if self.db_update(sql, t) != 0:
                        return
                    t = (0, place)
                    sql = 'update place set car_id = ? where place.id = ?'
                    self.db_update(sql, t)
                    self.Z044_trimop_carloads(Params, '51', carcode, waybill_id, origin, destination, commodity, loaded)
                    return
            else:
                loaded = loaded - unloadingrate
                if loaded < 0:
                    loaded = 0
                    t = ('', 0, 0, carid)
                    sql = 'update car set commodity = ?, weight_loaded = ?, carorder = ? '  +\
                          'where car.id = ?'
                    if self.db_update(sql, t) != 0:
                        return
                    t = (0, place)
                    sql = 'update place set car_id = ? where place.id = ?'
                    self.db_update(sql, t)
                    self.Z044_trimop_carloads(Params, '52', carcode, waybill_id, origin, destination, commodity, loaded)
                    return

            t = (loaded, carid)
            sql = 'update car set weight_loaded = ? where car.id = ?'
            if self.db_update(sql, t) == 0:
                return

        return



    def Z005_waybill(self, Flash, Params, Order_Type):
        """read in-progress car orders.  for each order, determine if all cars have been loaded
        (commodity eq spaces).  if all cars have been loaded then the waybill is set to
        ready-to-leave
        """
        if Order_Type == 'E':
            waybill_data = ('E', 'I')
        else:
            waybill_data = ('W', 'I')
            
        sql = 'select id, origin, warehouse, commodity from waybill where type = ? and status = ?'
        count, ds_orders = self.db_read(sql, waybill_data)
        
        if count <= 0:
            return

        for row in ds_orders:
            waybill_id = row[0]
            industry = row[1]
            commodity = row[3]

            data = (industry,)
            sql = 'select station, code from place where industry = ?'
            count, ds_places = self.db_read(sql, data)
            if count < 0:
                return
            for places in ds_places:
                stax = places[0]
                plax = places[1]
                place = stax + '/' + plax
            
            if Order_Type == 'E':
                car_data = (waybill_id,)
                sql = 'select car.id from car where carorder = ?'
                new_status = 'I'
                message = 'INDUSTRY ' + industry + place + ' RAISED WAYBILL'
            else:
                car_data = (waybill_id, commodity) 
                sql = 'select car.id from car where carorder = ? and commodity = ?'
                new_status = 'C'
                message = 'INDUSTRY ' + industry + place + ' COMPLETED WAYBILL'
            
            count, dummy = self.db_read(sql, car_data)                                          
            if count == 0:
                timestamp = Params.get_date() + ' ' + Params.get_time()
                
                t = ('W', new_status, timestamp, row[0],)
                sql = 'update waybill set type = ?, status = ?, timestamp = ? where id = ?'
                if self.db_update(sql, t) != 0:
                    return
                
                t = (message, )
                Flash.Z003_generate_flash_message(message, Params)
                print(timestamp + 'Z009: ' + message)
        return



    def Z044_trimop_carloads(self, Params, action, car, waybill, orig, dest, commodity, load):
        """write out a car record update for TriMOPS.  Need to look up the cartype/car class
        from the car, and the origin/dest station from the origin/dest industry.
        the action will indicate whether it's a loading (51) or unloading (52) event
        """
        #see if we want to process the messages
        process_trimops = Params.get_param_value('TRIMOPS', 'NO')
        if process_trimops != 'YES':
            return
        
        #append the updated details to the history file
        filename = self.directory + 'exMOPStrains.txt'
        with open(filename, "a") as f:

            #get data for cars
            data = (car,)
            sql = 'select cartype, carclass from car where car = ?'
            count, ds_cars = self.db_read(sql, data)
            if count < 0:
                return
            for row in ds_cars:
                cartype = row[0]
                carclass = row[1]

            #get data for origin
            data = (orig,)
            sql = 'select station from place where industry = ?' 
            count, ds_places = self.db_read(sql, data)
            if count < 0:
                return
            for row in ds_places:
                orig_stax = row[0]

            #get data for dest
            data = (dest,)
            sql = 'select station from place where industry = ?' 
            count, ds_places = self.db_read(sql, data)
            if count < 0:
                return
            for row in ds_places:
                dest_stax = row[0]

            record_data = self.x_field(car, 10) +\
                          self.x_field(cartype, 10) +\
                          self.x_field(carclass, 10) +\
                          self.x_field(waybill, 5, 'R') +\
                          self.x_field(orig_stax, 10) +\
                          self.x_field(orig, 15) +\
                          self.x_field(dest_stax, 10) +\
                          self.x_field(dest, 15) +\
                          self.x_field(commodity, 10) +\
                          self.x_field(load, 5, 'R')
            f.write(action + Params.get_date() + Params.get_time() + record_data + '\n')
        return
