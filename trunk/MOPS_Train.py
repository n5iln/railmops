'''
Train Class


Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    Rev 1 Added new routines Z040_trimop, Z041_trimop_shutdown and Z042_trimops_update.
          Changes to update routines to reference these modules
          Fixed failure on terminating unscheduled trains (sql change)
          Corrected sql data input to read correct variable in XCARXT (remove car)
          Removed import of unused module re.  Removed unused variables.
          Print consist only printed full list; check added PRCONS
          Changed validation on time on REPORT (minutes)
          Unused variables removed
          Corrected bad reporting of trains running in reverse direction
          Added Next station & time to TRAINS enquiry
          Added Haulage power to LICONS enquiry
          Only expected trains displayed for LINEUP
          EST removed from LINEUP enquiry; not used
          Strip added to commodity when checking for empty/loaded in LINEUP
          Amended count on block to reflect use of word additional
          Amended TTRAIN to correctly terminate trains running in 'opposite' direction
          Amended REPORT to remove publication of loco details
          Amended TTRAIN to handle termination of Unscheduled trains
          Corrected sql getting schedule id in TTRAIN
          Prevented termination of a train that has already been terminated
          Added Ready trains to TRAINS enquiry
          TRAINS amended to show a flag if the train terminates
          Direction added as field and filer on LINEUP enquiry
          Distinguishes between passenger, loaded and empty cars on lineup
          Removed FROM station from LINEUP as direction was already given
          Added Passenger Car reporting to LICONS
          TRAINS enquiry changed to sort by next action time
'''

import MOPS_Element

class cTrains(MOPS_Element.cElement):
    """Trains define a locomotive and cars normally running against a schedule (although it is
    possible to run a train without a schedule.  Trains have a code, type (Scheduled, Extra or
    Unscheduled) and optionally the schedule that they are running against.
    """



    def utrain(self, message, Params):
        """Creates an unscheduled train:
                            schedule    train code  locomotive  time offset
            Unscheduled -               required    required
        The departing station is taken from the loco.  An Unscheduled train has, initially,
        no Running entries as the route is not known.
        """
        if self.show_access(message, 'UTRAIN train;^locomotive^', 'N') != 0:
            return

        #train id ------------------------------------------------------------------------------
        train_id, rc = self.extract_field(message, 0, 'TRAIN ID')
        if rc > 1:   
            return

        #check to see if a train is already running against this train id
        data = (train_id,)
        sql = 'select id from train where train = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* THIS TRAIN ID ALREADY USED BY ANOTHER TRAIN')
            return           

        #check to see if a schedule is already running against this train id
        data = (train_id,)
        sql = 'select id from schedule where schedule = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* THIS TRAIN ID ALREADY ON USE ON A SCHEDULE')
            return           

        #loco -----------------------------------------------------------------------
        loco, rc = self.extract_field(message, 1, 'LOCO ID')
        if rc > 1:   
            return

        t = (loco, '')
        sql = 'select locomotive.station, locotype.oper_mode, locomotive.is_powered ' +\
              'from locomotive, locotype ' +\
              'where locomotive.loco = ? and locomotive.locotype = locotype.locotype ' +\
              'and locomotive.station != ?'
        count, ds_loco = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* LOCOMOTIVE CODE DOES NOT EXIST OR IS ALREADY ON A TRAIN')
            return
        else:
            for row in ds_loco:
                at_station = row[0]
                oper_mode = row[1]
                powered = row[2]
                
        if oper_mode == 'S':
            print('* NOT ALLOWED TO CREATE TRAIN WITH SLAVE/DUMMY LOCOMOTIVE')
            return

        if powered != 'P':
            print('* LOCOMOTIVE IS NOT AVAILABLE TO ALLOCATE TO A TRAIN')
            return

        #carry out the update =====================================================
        t = (train_id, 'U', at_station, 'R', '')
        sql = 'insert into train values (null, ?, ?, ?, ?, ?)'
        if self.db_update(sql, t) != 0:
            return
        t = ('', 0, train_id, loco)
        sql = 'update locomotive set station = ?, place_id = ?, train = ? where loco = ?'
        if self.db_update(sql, t) != 0:
            return

        #update extract to triMOPS
        self.Z042_trimops_update (Params, train_id, 0, False)                           # Rev 1

        print('NEW UNSCHEDULED TRAIN:' + train_id + ' LOCO:' + loco + 'CURRENT STATION:' + at_station)        
        return



    def etrain(self, message, Params):
        """Creates an Extra train:
                            schedule    train code  locomotive  
            Extra -         required    required    required    
        The originating station is taken from the schedule.
        The Running table entries are copied from the Timing entries for the schedule for
        Extra trainsm using the same running times as the schedule it is running against.
        """
        if self.show_access(message,'ETRAIN schedule;train;^locomotive^', 'N') != 0:
            return

        #schedule id ------------------------------------------------------------------------------
        schedule, rc = self.extract_field(message, 0, 'SCHEDULE ID')
        if rc > 1:   
            return

        #check to see if the schedule id exists and is in the correct status
        t = (schedule, )
        sql = 'select id, status, orig_station from schedule where schedule = ?'
        count, ds_schedules = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            print('* SCHEDULE ID DOES NOT EXIST')
            return
        else:
            for row in ds_schedules:
                status = row[1]
                station = row[2]

        if not (status == 'R' or status == 'A'):
            print('* CAN ONLY RUN EXTRAS AGAINST ACTIVE OR RUNNING SCHEDULES')
            return

        #train id ------------------------------------------------------------------------------
        train_id, rc = self.extract_field(message, 1, 'TRAIN ID')
        if rc > 1:   
            return

        t = (train_id,)
        #check to see if a train is already running against this train id
        sql = 'select id from train where train = ?'
        count, dummy = self.db_read(sql, t)
        if count < 0:
            return
        if count != 0:
            print('* THIS TRAIN ID ALREADY USED BY ANOTHER TRAIN')
            return

        if schedule == train_id:
            print('* SCHEDULE ID AND TRAIN ID CANNOT BE THE SAME')
            return
        else:
            t = (train_id, )
            sql = 'select id, status from schedule where schedule = ?'
            count, ds_schedules = self.db_read(sql, t)
            if count < 0:
                return
            if count > 0:
                print('* EXTRA ID ALREADY EXISTS AS A SCHEDULE ID')
                return
            

        #loco -----------------------------------------------------------------------
        loco, rc = self.extract_field(message, 2, 'LOCO ID')
        if rc > 1:   
            return

        t = (loco, '')
        sql = 'select locomotive.station, locotype.oper_mode, locomotive.is_powered, ' +\
              'locomotive.id ' +\
              'from locomotive, locotype ' +\
              'where locomotive.loco = ? and locomotive.locotype = locotype.locotype ' +\
              'and locomotive.station != ?'
        count, ds_loco = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* LOCOMOTIVE CODE DOES NOT EXIST OR IS ALREADY ON A TRAIN')
            return
        else:
            for row in ds_loco:
                at_station = row[0]
                oper_mode = row[1]
                powered = row[2]
                loco_id = row[3]
                
        if oper_mode == 'S':
            print('* NOT ALLOWED TO CREATE TRAIN WITH SLAVE/DUMMY LOCOMOTIVE')
            return

        if powered != 'P':
            print('* LOCOMOTIVE IS NOT AVAILABLE TO ALLOCATE TO A TRAIN')
            return
                
        if station != at_station:
            print('* LOCOMOTIVE NOT AT DEPARTURE STATION FOR SCHEDULED TRAIN')
            return

        #carry out the update =====================================================
        t = (train_id, 'E', station, 'R', schedule)
        sql = 'insert into train values (null, ?, ?, ?, ?, ?)'
        if self.db_update(sql, t) != 0:
            return

        t = ('', 0, train_id, loco_id)
        sql = 'update locomotive set station = ?, place_id = ?, train = ? where id = ?'
        if self.db_update(sql, t) != 0:
            return

        t = (schedule,)
        sql = 'select section, depart_station, arrive_station, planned_depart, planned_arrive ' +\
              'from timings where schedule = ? order by section'
        count, ds_schedule = self.db_read(sql, t)
        if count < 0:
            return
        for row in ds_schedule:
            t2 = (train_id, row[0], row[1], row[2], row[3], row[4], '', '')
            sql = 'insert into running values (null, ?, ?, ?, ?, ?, ?, ?, ?)'
            if self.db_update(sql, t2) != 0:
                return

        #update extract to triMOPS
        self.Z042_trimops_update (Params, train_id, schedule, False)                 # Rev 1

        print('EXTRA TRAIN:' + schedule + ' LOCO:' + loco + 'CURRENT STATION:' + at_station)        
        return



    def strain(self, message, Params):
        """Creates a Scheduled train:
                            schedule    train code  locomotive  time offset
            Scheduled -     required    optional    required    
        For Scheduled and Extra trains, the station is taken from teh schedule.
        The Running table entries are copied from the Timing entries for the schedule for
        Scheduled and Extra trains (with the Running estimates offset by the give time entries).
        """
        if self.show_access(message, 'STRAIN schedule;(train);^locomotive^', 'N') != 0:
            return

        #schedule id ------------------------------------------------------------------------------
        schedule, rc = self.extract_field(message, 0, 'SCHEDULE ID')
        if rc > 1:   
            return

        if schedule != '':
            #check to see if the schedule id exists and is in the correct status
            t = (schedule, 'A')
            sql = 'select id, status, orig_station from schedule where schedule = ? and status = ?'
            count, ds_schedules = self.db_read(sql, t)
            if count < 0:
                return
            if count == 0:
                print('* SCHEDULE ID DOES NOT EXIST OR IS NOT IN ACTIVE STATUS')
                return
            else:
                for row in ds_schedules:
                    schedule_id = row[0]
                    station = row[2]

        #train id ------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 1:   
            train_id= value
        else:
            train_id = ''

        if train_id == '':
            train_id = schedule

        #check to see if a train is already running against this train id
        data = (train_id,)
        sql = 'select id from train where train = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* THIS TRAIN ID ALREADY USED BY ANOTHER TRAIN')
            return           

        #loco -----------------------------------------------------------------------
        loco, rc = self.extract_field(message, 2, 'LOCO ID')
        if rc > 1:   
            return

        t = (loco, '')
        sql = 'select locomotive.station, locotype.oper_mode, locomotive.is_powered, ' +\
              'locomotive.id ' +\
              'from locomotive, locotype ' +\
              'where locomotive.loco = ? and locomotive.locotype = locotype.locotype ' +\
              'and locomotive.station != ?'
        count, ds_loco = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* LOCOMOTIVE CODE DOES NOT EXIST OR IS ALREADY ON A TRAIN')
            return
        else:
            for row in ds_loco:
                at_station = row[0]
                oper_mode = row[1]
                powered = row[2]
                loco_id = row[3]
                
        if oper_mode == 'S':
            print('* NOT ALLOWED TO CREATE TRAIN WITH SLAVE/DUMMY LOCOMOTIVE')
            return

        if powered != 'P':
            print('* LOCOMOTIVE IS NOT AVAILABLE TO ALLOCATE TO A TRAIN')
            return
                
        if station != at_station:
            print('* LOCOMOTIVE NOT AT DEPARTURE STATION FOR SCHEDULED TRAIN')
            return

        #carry out the update =====================================================
        t = (train_id, 'S', station, 'R', schedule)
        sql = 'insert into train values (null, ?, ?, ?, ?, ?)'
        if self.db_update(sql, t) != 0:
            return

        t = ('R', schedule_id)
        sql = 'update schedule set status = ? where id = ?'
        if self.db_update(sql, t) != 0:
            return

        t = ('', 0, train_id, loco_id)
        sql = 'update locomotive set station = ?, place_id = ?, train = ? where id = ?'
        if self.db_update(sql, t) != 0:
            return

        t = (schedule,)
        sql = 'select section, depart_station, arrive_station, planned_depart, planned_arrive ' +\
              'from timings where schedule = ? order by section'
        count, ds_schedule = self.db_read(sql, t)
        if count < 0:
            return
        for row in ds_schedule:
            t2 = (train_id, row[0], row[1], row[2], row[3], row[4], '', '')
            sql = 'insert into running values (null, ?, ?, ?, ?, ?, ?, ?, ?)'
            if self.db_update(sql, t2) != 0:
                return

        #update extract to triMOPS
        self.Z042_trimops_update (Params, train_id, schedule, False)              # Rev 1

        print("NEW TRAIN: " + schedule + " LOCO: " + loco + " CURRENT STATION: " + at_station)        
        return



    def ltrain(self, message, Flash, Params):
        """Creates a train starting at a later origin:
                            type  schedule train code  locomotive  
            Scheduled -     S     required optional    required    
            Extra -         E     required required    required    
        """
        if self.show_access(message, 'LTRAIN type[E/S];schedule;(train);^locomotive^'
                            , 'N') != 0:
            return

        #train type---------------------------------------------------------------------------------
        train_type, rc = self.extract_field(message, 0, 'TRAIN TYPE')
        if rc > 1:   
            return

        if not (train_type == 'S' or train_type == 'E'):
            print('* TRAIN TYPE MUST BE (S)CHEDULED OR (E)XTRA')
            return

        #schedule id ------------------------------------------------------------------------------
        schedule, rc = self.extract_field(message, 1, 'SCHEDULE ID')
        if rc > 1:   
            return

        if schedule != '':
            #check to see if the schedule id exists and is in the correct status
            t = (schedule, )
            sql = 'select id, status from schedule where schedule = ?'
            count, ds_schedules = self.db_read(sql, t)
            if count < 0:
                return
            if count == 0:
                print('* SCHEDULE ID DOES NOT EXIST')
                return
            else:
                for row in ds_schedules:
                    schedule_id = row[0]
                    status = row[1]

        if not (status == 'A' or status == 'R'):
            print('* STATUS MUST BE IN ACTIVE OR RUNNING STATUS')
            return

        #train id ------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 2, '')
        if rc == 0:   
            train_id= value
        else:
            train_id = ''

        if train_id == '' and train_type == 'E':
            print('* TRAIN ID REQUIRED FOR EXTRA TRAIN')
            return
        
        if train_id == '':
            train_id = schedule

        #check to see if a train is already running against this train id
        data = (train_id,)
        sql = 'select id from train where train = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* THIS TRAIN ID ALREADY USED BY ANOTHER TRAIN')
            return           
    
        #check to see if an extra train is using another schedule
        if train_type == 'E':
            data = (train_id,)
            sql = 'select id from schedule where schedule = ?'
            count, dummy = self.db_read(sql, data)
            if count < 0:
                return
            if count != 0:
                print('* THIS TRAIN ID ALREADY USED BY A SCHEDULE')
                return           

        #loco -----------------------------------------------------------------------
        loco, rc = self.extract_field(message, 3, 'LOCO ID')
        if rc > 1:   
            return

        t = (loco, '')
        sql = 'select locomotive.station, locotype.oper_mode, locomotive.is_powered, ' +\
              'locomotive.id ' +\
              'from locomotive, locotype ' +\
              'where locomotive.loco = ? and locomotive.locotype = locotype.locotype ' +\
              'and locomotive.station != ?'
        count, ds_loco = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* LOCOMOTIVE CODE DOES NOT EXIST OR IS ALREADY ON A TRAIN')
            return
        else:
            for row in ds_loco:
                station = row[0]
                oper_mode = row[1]
                powered = row[2]
                loco_id = row[3]
                
        if oper_mode == 'S':
            print('* NOT ALLOWED TO CREATE TRAIN WITH SLAVE/DUMMY LOCOMOTIVE')
            return

        if powered != 'P':
            print('* LOCOMOTIVE IS NOT AVAILABLE TO ALLOCATE TO A TRAIN')
            return
                
        data = (schedule, station)
        sql = 'select section, depart_station from timings where schedule = ? ' +\
              'and depart_station = ? order by section'
        count, ds_schedule = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* DEPARTING STATION NOT ON SCHEDULE')
            return
        else:
            for row in ds_schedule:
                start_section = row[0]

        #carry out the update =====================================================
        t = (train_id, train_type, station, 'R', schedule)
        sql = 'insert into train values (null, ?, ?, ?, ?, ?)'
        if self.db_update(sql, t) != 0:
            return

        t = ('R', schedule_id)
        sql = 'update schedule set status = ? where id = ?'
        if self.db_update(sql, t) != 0:
            return

        t = ('', 0, train_id, loco_id)
        sql = 'update locomotive set station = ?, place_id = ?, train = ? where id = ?'
        if self.db_update(sql, t) != 0:
            return

        t = (schedule, start_section)
        sql = 'select section, depart_station, arrive_station, planned_depart, planned_arrive ' +\
              'from timings where schedule = ? and section >= ? order by section'
        count, ds_schedule = self.db_read(sql, t)
        if count < 0:
            return
        for row in ds_schedule:
            t2 = (train_id, row[0], row[1], row[2], row[3], row[4], '', '')
            sql = 'insert into running values (null, ?, ?, ?, ?, ?, ?, ?, ?)'
            if self.db_update(sql, t2) != 0:
                return

        message = ('LATE ORIGIN TRAIN:' + train_id + ' LOCO:' + loco + ' STARTING STATION:' + station)        
        print(message)
        Flash.Z003_generate_flash_message(message, Params)

        #update extract to triMOPS
        self.Z042_trimops_update (Params, train_id, schedule, False)                   # Rev 1

        return


    def lineup(self, message, Params):
        """Shows to the screen trains on their way to a particular station. Provide the following
        detail for each Train: Train Code, PlannedArrive, ArriveEstimate (at that Station),
        StationFrom, StationTo, Class, #Locos, #Cars, #Loaded, #Empty, Weight of Train
        """
        if self.show_access(message, 'LINEUP ^station^;(direction)', 'N') != 0:
            return

        #station-----------------------------------------------------------------------
        station, rc = self.extract_field(message, 0, 'STATION')
        if rc > 1:   
            return

        data = (station,)
        sql = 'select short_name from station where station = ?'
        count, ds_stations = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* STATION DOES NOT EXIST')
            return
        else:
            for row in ds_stations:
                station_name = row[0]

        #direction---------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            direction = value
        else:
            direction = '*'


        print('LINE UP ENQUIRY FOR ' + station + ' ' + station_name)

        # build the column titles
        titles = self.x_field('TRAIN=', 6) + ' ' +\
                 self.x_field('DUE=', 4) + ' ' +\
                 self.x_field('ORIGIN===', self.staxsize) + ' ' +\
                 self.x_field('DEST=====', self.staxsize) + ' ' +\
                 self.x_field('C', 1) + ' ' +\
                 self.x_field('D', 1) + ' ' +\
                 self.x_field('#LOCO', 5) + ' ' +\
                 self.x_field('#PASS', 5) + ' ' +\
                 self.x_field('#LOAD', 5) + ' ' +\
                 self.x_field('#MTY=', 5) + ' ' +\
                 self.x_field('WGHT=', 5) + ' ' +\
                 self.x_field('LNGTH', 5)

        data = (station, '')
        sql = 'select running.train, running.depart_station, running.est_depart, ' +\
              'running.act_depart, running.est_arrive, train.schedule, ' +\
              'schedule.orig_station, schedule.dest_station, schedule.class, ' +\
              'schedule.direction ' +\
              'from running, train, schedule ' +\
              'where running.arrive_station = ? and ' +\
              'running.train = train.train and train.schedule = schedule.schedule ' +\
              'and running.act_arrive = ? order by running.est_arrive'     #Rev 1
        count, ds_timings = self.db_read(sql, data)
        if count < 0:
            return

        line_count = 0
        counter = 0
        for row in ds_timings:
            train_id = row[0]
            depart = row[1]
            est_arrive = row[4]
            orig_station = row[6]
            dest_station = row[7]
            sched_class = row[8]
            schedule_direction = row[9]                                           #Rev 1
            loco_count = 0
            pass_count = 0
            load_count = 0
            empty_count = 0
            weight_count = 0
            length_count = 0
            data = (train_id,)
            sql = 'select locotype.length, locomotive.weight from locomotive, locotype ' +\
                  'where locomotive.train = ? ' +\
                  'and locomotive.locotype = locotype.locotype'
            loco_count, ds_locos = self.db_read(sql, data)
            if loco_count < 0:
                return
            for lrow in ds_locos:
                weight_count = weight_count + lrow[1]
                length_count = length_count + lrow[0]
            pass_count = 0
            sql = 'select cartype.length, cartype.unladen_weight, ' +\
                  'car.weight_loaded, car.commodity, car.carclass ' +\
                  'from car, cartype ' +\
                  'where car.train = ? ' +\
                  'and car.cartype = cartype.cartype'
            car_count, ds_cars = self.db_read(sql, data)
            if car_count < 0:
                return
            for crow in ds_cars:
                weight_count = weight_count + crow[1] + crow[2]
                length_count = length_count + crow[0]
                carclass = crow[4]                                           #Rev 1
                     
                passenger = Params.get_param_value('PASSENGER', 'XXX')       #Rev 1
                if passenger == carclass:                                    #Rev 1
                    pass_count = pass_count + 1                              #Rev 1
                else:
                    if crow[3].strip() == '':                                     #Rev 1
                        empty_count = empty_count + 1
                    else:
                        load_count = load_count + 1

            if line_count == 0:
                print(titles)
            if (direction == '*') or (schedule_direction == direction):           #Rev 1
                print(self.x_field(train_id, 6) + " " +
                       self.x_field(est_arrive, 4) + " " +
                       self.x_field(orig_station, self.staxsize) + " " +
                       self.x_field(dest_station, self.staxsize) + " " +
                       self.x_field(sched_class, 1) + " " +
                       self.x_field(schedule_direction, 1) + " " +
                       self.x_field(loco_count, 5, 'R') + " " +
                       self.x_field(pass_count, 5, 'R') + " " +
                       self.x_field(load_count, 5, 'R') + " " +
                       self.x_field(empty_count, 5, 'R') + " " +
                       self.x_field(weight_count, 5, 'R') + " " +
                       self.x_field(length_count, 5, 'R'))
                counter = counter + 1
                line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break
        print(' ** END OF DATA: ' + str(counter) + ' RECORDS DISPLAYED **')         
        return


    def alocot(self, message):
        """Allocate a locomotive to a train.  The train must already exist, and be reported as
        being at the same place as the locomotive.
        """
        if self.show_access(message, 'ALOCOT ^locomotive^;^train^', 'N') != 0:
            return

        #loco---------------------------------------------------------------------------------------
        loco, rc = self.extract_field(message, 0, 'LOCOMOTIVE')
        if rc > 1:   
            return

        t = (loco,)
        sql = 'select station, is_powered, id from locomotive where loco = ?'
        count, ds_station = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* LOCOMOTIVE CODE DOES NOT EXIST')
            return
        else:
            for row in ds_station:
                loco_at_station = row[0]
                power = row[1]
                loco_id = row[2]

        if not (power == 'U' or power == 'P'):
            print('* LOCOMOTIVE IS NOT ABLE TO BE MOVED (FUELLING/MAINTENANCE)')
            return

        #train reference ---------------------------------------------------------------------------
        train, rc = self.extract_field(message, 1, 'TRAIN REFERENCE')
        if rc > 1:   
            return

        #check that the train exists and get the station
        t = (train,)
        sql = 'select id, station from train where train = ?'
        count, ds_trains = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            print('* TRAIN DOES NOT EXIST')
            return
        else:
            for row in ds_trains:
                station = row[1]

        if station != loco_at_station:
            print('* LOCOMOTIVE NOT AT SAME STATION AS CURRENT STATION OF TRAIN')
            return

        #carry out the update ----------------------------------------------------------------------
        t = ('', 0, train, loco_id)
        sql = 'update locomotive set station = ?, place_id = ?, train = ? ' +\
              'where id = ?'
        if self.db_update(sql, t) != 0:
            return

        print('LOCOMOTIVE '+ loco+ ' ATTACHED TO TRAIN: '+ train)        
        return
        


    def xlocot(self, message):
        """Removes a locomotive from a train.  The train must be at a station.
        """
        if self.show_access(message, 'XLOCOT ^locomotive^', 'N') != 0:
            return

        #loco---------------------------------------------------------------------------------------
        loco, rc = self.extract_field(message, 0, 'LOCOMOTIVE')
        if rc > 1:   
            return

        t = (loco,)
        sql = 'select train, id from locomotive where loco = ?'
        count, ds_loco = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* LOCOMOTIVE CODE DOES NOT EXIST')
            return
        else:
            for row in ds_loco:
                train = row[0]
                loco_id = row[1]

        if train == '':
            print('* LOCOMOTIVE IS NOT ON A TRAIN')
            return

        #check that the train exists and get the station
        t = (train,)
        sql = 'select id, station from train where train = ?'
        count, ds_trains = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            print('* TRAIN DOES NOT EXIST')
            return
        else:
            for row in ds_trains:
                station = row[1]

        if station == '':
            print('* TRAIN IS NOT AT A STATION')
            return

        #carry out the update ----------------------------------------------------------------------
        t = (station, '', loco_id)
        sql = 'update locomotive set station = ?, train = ? where id = ?'
        if self.db_update(sql, t) != 0:
            return

        print('LOCOMOTIVE '+ loco+ ' DETACHED FROM TRAIN: '+ train+ ' AND NOW AT '+ station)        
        return



    def acarxt(self, message):
        """Allocate a car to a train.  The train must already exist, and be reported as
        being at the same place as the car.
        """
        if self.show_access(message, 'ACARXT car;^train^', 'N') != 0:
            return
 
        #car --------------------------------------------------------------------------------------
        car, rc = self.extract_field(message, 0, 'CAR')
        if rc > 1:   
            return

        t = (car,)
        sql = 'select station, time_in_maint, id, block from car where car = ?'
        count, ds_cars = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* CAR CODE DOES NOT EXIST')
            return
        else:
            for row in ds_cars:
                car_at_station = row[0]
                maint = row[1]
                car_id = row[2]
                block = row[3]

        if maint != 0:
            print('* CAR IS IN MAINTENANCE AND CANNOT BE MOVED')
            return
                
        #train reference ---------------------------------------------------------------------------
        train, rc = self.extract_field(message, 1, 'TRAIN REFERENCE')
        if rc > 1:   
            return

        #check that the train exists and get the station
        t = (train,)
        sql = 'select id, station from train where train = ?'
        count, ds_trains = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            print('* TRAIN DOES NOT EXIST')
            return
        else:
            for row in ds_trains:
                station = row[1]
                
        if station != car_at_station:
            print('* CAR NOT AT SAME STATION AS CURRENT STATION OF TRAIN')
            return

        #carry out the update =====================================================
        t = ('', 0, train, car_id)
        sql = 'update car set station = ?, place_id = ?, train = ? where id = ?'
        if self.db_update(sql, t) != 0:
            return

        #if the car was attached to a block, move the rest of the block as well
        if block != '':
            t = ('', 0, train, block)
            sql = 'update car set station = ?, place_id = ?, train = ? where block = ?'
            if self.db_update(sql, t) != 0:
                return

        print('CAR ' + car + ' ATTACHED TO TRAIN: ' + train)        
        if block != '':
            data = (block,)
            sql = 'select car from car where block = ?'
            count, dummy = self.db_read(sql, data)
            if count < 0:
                return
            print(count-1, ' ADDITIONAL CARS ADDED TO TRAIN AS PART OF BLOCK')    #Rev 1
        return


    def xcarxt(self, message):
        """Removes a car from a train.  The train must be at a station.
        """
        if self.show_access(message, 'XCARXT car', 'N') != 0:
            return

        #car---------------------------------------------------------------------------------------
        car, rc = self.extract_field(message, 0, 'CAR')
        if rc > 1:   
            return

        t = (car,)
        sql = 'select train, id, block from car where car = ?'
        count, ds_car = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* CAR NUMBER DOES NOT EXIST')
            return
        else:
            for row in ds_car:
                train = row[0]
                car_id = row[1]
                block = row[2]

        if train == '':
            print('* CAR IS NOT ON A TRAIN')
            return

        #check that the train exists and get the station
        t = (train,)
        sql = 'select id, station from train where train = ?'
        count, ds_trains = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            print('* TRAIN DOES NOT EXIST')
            return
        else:
            for row in ds_trains:
                station = row[1]

        if station == '':
            print('* TRAIN IS NOT AT A STATION')
            return

        #carry out the update ----------------------------------------------------------------------
        t = (station, '', car_id)
        sql = 'update car set station = ?, train = ? where id = ?'
        if self.db_update(sql, t) != 0:
            return

        #if the car was attached to a block, move the rest of the block as well
        if block != '':
            t = (station, '', block)
            sql = 'update car set station = ?, train = ? where block = ?'
            if self.db_update(sql, t) != 0:
                return

        print('CAR '+ car+ ' DETACHED FROM TRAIN: '+ train+ ' AND NOW AT '+ station)        
        if block != '':
            data = (block,)                                                         # Rev 1
            sql = 'select car from car where block = ?'
            count, dummy = self.db_read(sql, data)                       
            if count < 0:
                return
            print(count-1, ' ADDITIONAL CARS DETACHED FROM TRAIN AS PART OF BLOCK')  #Rev 1
        return




    def report(self, message, Params):
        """reports a train arriving or departing a station.  processing depends on whether it is
        an unscheduled train or a scheduled/extra train.  For unscheduled train the timings
        record may need to be created or updated as there will be no information.  other train
        types need only update an existing timings record (which must exist)
        """
        if self.show_access(message, 'REPORT train;update[DEP/ARR/THR];^station^;(time)','N') != 0:
            return
        
        #train id ------------------------------------------------------------------------------
        train, rc = self.extract_field(message, 0, 'TRAIN ID')
        if rc > 0:   
            return

        t = (train,)
        sql = 'select train, type from train where train = ?'
        count, ds_trains = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* TRAIN CODE DOES NOT EXIST')
            return
        else:
            for row in ds_trains:
                train_type = row[1]
                
        #arrival/depart ----------------------------------------------------------------------------
        action, rc = self.extract_field(message, 1, 'ACTION')
        if rc > 0:   
            return

        if not (action == 'ARR' or action == 'DEP' or action == 'THR'):
            print('* INDICATE WHETHER THIS IS AN ARRIVAL (arr), DEPARTURE (dep) OR THROUGH (thr) REPORT')
            return
            
        #station -----------------------------------------------------------------------------------
        station, rc = self.extract_field(message, 2, 'STATION')
        if rc > 0:   
            return

        t = (station,)
        sql = 'select long_name from station where station = ?'
        count, ds_stations = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* TRAIN CODE DOES NOT EXIST')
            return
        else:
            for row in ds_stations:
                station_name = row[0]

        #act_time ----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 3, '')
        if rc == 0:   
            act_time = value
        else:
            act_time = Params.get_time()
            act_time = act_time[0:2] + act_time[3:5]

        if len(act_time) != 4:
            print('* TIME MUST BE IN HHMM FORMAT')
            return

        hours = act_time[0:2]
        mins = act_time[2:4]

        try:
            if int(hours) > 23:
                print('* HOURS MUST BE IN RANGE 00-23')
                return

            if int(mins) > 59:
                print('* MINUTES MUST BE IN RANGE 00-59')
                return
        except:
            print('* TIME MUST BE ENTERED IN HOURS AND MINUTES')
            return
        
        #validate the update will be good ----------------------------------------------------------
        if train_type != 'U':
            if action == "ARR" or action == 'THR':
                data = (train, station, '')
                sql = 'select est_arrive from running ' +\
                      'where train = ? and arrive_station = ? and act_arrive = ?'
                count, ds_timings = self.db_read(sql, data)
                if count < 0:
                    return
                if count == 0:
                    print('NO TIMINGS RECORD TO UPDATE')
                    return
                
            if action == "DEP" or action == 'THR':
                data = (train, station, '')
                sql = 'select est_depart from running ' +\
                      'where train = ? and depart_station = ? and act_depart = ?'
                count, ds_timings = self.db_read(sql, data)
                if count < 0:
                    return
                if count == 0:
                    print('NO TIMINGS RECORD TO UPDATE')
                    return

        # update the database ----------------------------------------------------------------------
        if train_type == 'U':
            last_id = 0
            data = (train, )
            sql = 'select id from running where train = ? order by id'
            rec_count, ds_timings = self.db_read(sql, data)
            if rec_count < 0:
                return
            if rec_count > 0:
                for row in ds_timings:
                    last_id = row[0] 

            #if its an arrive or thru we need to update
            if action == 'ARR' or action == 'THR':
                data = (station, act_time, last_id)
                sql = 'update running set arrive_station = ?, act_arrive = ? where id = ?'
                if self.db_update(sql, data) != 0:
                    return

            #if its a depart or a thru we need to enter a new record
            if action == 'DEP' or action == 'THR':
                last_id = last_id + 1
                data = (train, last_id, station, '', '', '', act_time, '')
                sql = 'insert into running values (null, ?, ?, ?, ?, ?, ?, ?, ?)'
                if self.db_update(sql, data) != 0:
                    return

        else:
            if action == 'ARR' or action == 'THR':
                data = (act_time, train, station)
                sql = 'update running set act_arrive = ? where train = ? and arrive_station = ?'
                if self.db_update(sql, data) != 0:
                    return
                if action == 'ARR':
                    data = (station, train)
                    sql = 'update train set station = ? where train = ?'
                    if self.db_update(sql, data) != 0:
                        return
            if action == 'DEP' or action == 'THR':
                data = (act_time, train, station)
                sql = 'update running set act_depart = ? where train = ? and depart_station = ?'
                if self.db_update(sql, data) != 0:
                    return
                data = ('', train)
                sql = 'update locomotive set station = ? where train = ?'
                if self.db_update(sql, data) != 0:
                    return

        #update extract to triMOPS
        data = (train,)
        sql = 'select schedule from train where train = ?'
        count, ds_schedule = self.db_read(sql, data)
        if count < 0:
            return
        for row in ds_schedule:
            schedule = row[0]
        self.Z042_trimops_update (Params, train, schedule, True)

        if action == 'DEP':
            print(train + ' DEPARTED ' + station + " " + station_name + ' AT ' + act_time)
        if action == 'ARR':
            print(train + ' ARRIVED ' + station + " " + station_name + ' AT ' + act_time)
        if action == 'THR':
            print(train + ' THRU ' + station + " " + station_name + ' AT ' + act_time)
        return
        

    def ttrain(self, message, Flash, Params):
        """terminates a train.  train is set to completed.  rolling stock is set to the
        current station of the train.  schedule is set to C - Complete
        """
        if self.show_access(message, 'TTRAIN train;(confirm[/YES])','N') != 0:
            return
        
        #train id ------------------------------------------------------------------------------
        train, rc = self.extract_field(message, 0, 'TRAIN ID')
        if rc > 0:   
            return

        #terminates early--------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:   
            early = value
            if early != 'YES':
                early = ''
        else:
            early = ''
    
        schedule_dest = ''
        schedule = ''
        data = (train,)
        sql = 'select schedule.dest_station, schedule.id, train.type, schedule.orig_station, schedule.schedule, ' +\
              'train.status from train left outer join schedule on train.schedule = schedule.schedule ' +\
              'where train.train = ?'                                                                   #Rev 1
        count, ds_schedule = self.db_read(sql, data)
        if count < 0:
            return
        for row in ds_schedule:
            schedule_dest = row[0]
            schedule_id = row[1]
            train_type = row[2]
            schedule = row[4]
            train_status = str(row[5])                                                                       #Rev 1
            
        if train_status == 'C':                                                                         #Rev 1
            print('* TRAIN HAS ALREADY BEEN TERMINATED')                                               #Rev 1
            return                                                                                      #Rev 1

        data = (schedule_id,)                                                                           #Rev 1 start
        sql = 'select schedule.direction, route.default_direction from route, schedule ' +\
              'where schedule.route = route.route and schedule.id = ?'                                  #Rev 1
        count, ds_routes = self.db_read(sql, data)
        if count < 0:
            return
        for routes in ds_routes:
            direction = routes[0]
            default_dir = routes[1]                                                                     #Rev 1 end
        
        if train_type == 'S':
            data = ('C', schedule_id)
            sql = 'update schedule set status = ? where id = ?'
            if self.db_update(sql, data) != 0:
                return
            
        if train_type == 'U':                                                                               #Rev 1
            direction = 'x'
            default_dir = 'x'

        data = (train,)
        if direction == default_dir:                                                                        #Rev 1
            sql = 'select arrive_station, act_arrive from running where train = ? order by timings'
        else:                                                                                               #Rev 1
            sql = 'select arrive_station, act_arrive from running where train = ? order by timings desc'    #Rev 1
        count, ds_running = self.db_read(sql, data)
        if count < 0:
            return
        for row in ds_running:
            arr_station = row[0]
            arr_time = row[1]

        if arr_time == '':
            print('* TRAIN NEEDS TO BE REPORTED AT STATION BEFORE TERMINATION')
            return

        if arr_station != schedule_dest:
            if early != 'YES':
                print('* CONFIRM EARLY TERMINATION OF TRAIN')
                return
            else:
                message = ('EARLY TERMINATION OF TRAIN: ' + train + ' AT: ' + arr_station)        
                Flash.Z003_generate_flash_message(message, Params)

        data = ('C', train)
        sql = 'update train set status = ? where train = ?'
        if self.db_update(sql, data) != 0:
            return

        data = (arr_station, '', train)
        sql = 'update locomotive set station = ?, train = ? where train = ?'
        if self.db_update(sql, data) != 0:
            return

        sql = 'update car set station = ?, train = ? where train = ?'
        if self.db_update(sql, data) != 0:
            return
        
        #update extract to triMOPS                                                      # Rev 1
        self.Z042_trimops_update (Params, train, schedule, True)

        print('TRAIN '+ train+ ' TERMINATED AT '+ arr_station)

        return


    def Z040_trimop(self, Params):
        """write out a session start set of records for TriMOPS.  This includes an initialiser
        record which will tell TriMOPS to reset all existing schedule train and running
        records.  This starter module also includes all station detail.
        """
        #see if we want to process the messages
        process_trimops = Params.get_param_value('TRIMOPS', 'NO')
        if process_trimops != 'YES':
            return
        

        #append the updated details to the history file
        filename = self.directory + 'exMOPStrains.txt'
        with open(filename, "a") as f:

            #header record
            f.write('00' + Params.get_date() + Params.get_time() + 'RESET RECORD' + '\n')

            #current list of stations
            sql = 'select station, short_name, long_name, area, stationtype, alias from station'
            count, ds_station = self.db_read(sql, '')
            if count < 0:
                return
            for row in ds_station:
                station = row[0]
                short_name = row[1]
                long_name = row[2]
                area = row[3]
                station_type = row[4]
                alias = row[5]
                record_data = self.x_field(station, 10) +\
                              self.x_field(short_name, 8) +\
                              self.x_field(long_name, 30) +\
                              self.x_field(area, 10) +\
                              self.x_field(station_type, 10) +\
                              self.x_field(alias, 10)
                f.write('10' + Params.get_date() + Params.get_time() + record_data + '\n')

            #current list of schedules
            data = 'I'
            sql = 'select schedule, route, name, class, status, run_days, ' +\
                  'orig_station, dest_station, direction from schedule ' +\
                  'where status != ?'
            count, ds_schedules = self.db_read(sql, data)
            if count < 0:
                return
            for row in ds_schedules:
                schedule =  row[0]
                route =     row[1]
                name =      row[2]
                sch_class = row[3]
                status =    row[4]
                run_days =  row[5]
                orig =      row[6]
                dest =      row[7]
                direction = row[8]
                record_data = self.x_field(schedule, 5) +\
                              self.x_field(route, 10) +\
                              self.x_field(name, 30) +\
                              self.x_field(sch_class, 1) +\
                              self.x_field(status, 1) +\
                              self.x_field(run_days, 8) +\
                              self.x_field(orig, 10) +\
                              self.x_field(dest, 10) +\
                              self.x_field(direction, 1)
                f.write('20' + Params.get_date() + Params.get_time() + record_data + '\n')

            #current list of schedules
            sql = 'select train, type, station, status, schedule from train'
            count, ds_trains = self.db_read(sql, '')
            if count < 0:
                return
            for row in ds_trains:
                train = row[0]
                traintype = row[1]
                station = row[2]
                status = row[3]
                schedule = row[4]
                record_data = self.x_field(train, 5) +\
                              self.x_field(traintype, 1) +\
                              self.x_field(station, 10) +\
                              self.x_field(status, 1) +\
                              self.x_field(schedule, 5)
                f.write('30' + Params.get_date() + Params.get_time() + record_data + '\n')

            #current state of running
            sql = 'select train, depart_station, arrive_station, ' +\
                  'est_depart, est_arrive, act_depart, act_arrive from running'
            count, ds_runnings = self.db_read(sql, '')
            if count < 0:
                return
            for row in ds_runnings:
                train = row[0]
                departs = row[1]
                arrives = row[2]
                est_depart = row[3]
                est_arrive = row[4]
                act_depart = row[5]
                act_arrive = row[6]
                record_data = self.x_field(train, 5) +\
                              self.x_field(departs, 10) +\
                              self.x_field(arrives, 10) +\
                              self.x_field(est_depart, 4) +\
                              self.x_field(est_arrive, 4) +\
                              self.x_field(act_depart, 4) +\
                              self.x_field(act_arrive, 4)
                f.write('40' + Params.get_date() + Params.get_time() + record_data + '\n')
        return


    def Z041_trimop_shutdown(self, Params):
        """send an end-of session message
        """
        #see if we want to process the messages
        process_trimops = Params.get_param_value('TRIMOPS', 'NO')
        if process_trimops != 'YES':
            return
        
        #append the updated details to the history file
        filename = self.directory + 'exMOPStrains.txt'
        with open(filename, "a") as f:

            #header record
            f.write('99' + Params.get_date() + Params.get_time() + 'MOPS SHUTDOWN' + '\n')

        return


    def Z042_trimops_update(self, Params, train, schedule, update_schedule):
        """ creates an update record for triMOPS
        """
        #see if we want to process the messages
        process_trimops = Params.get_param_value('TRIMOPS', 'NO')
        if process_trimops != 'YES':
            return
        
        #append the updated details to the history file
        filename = self.directory + 'exMOPStrains.txt'
        with open(filename, "a") as f:

            #schedule being updated
            data = (schedule, )
            sql = 'select schedule, route, name, class, status, run_days, ' +\
                  'orig_station, dest_station, direction from schedule ' +\
                  'where schedule = ?'
            count, ds_schedules = self.db_read(sql, data)
            if count > 0:
                for row in ds_schedules:
                    schedule =  row[0]
                    route =     row[1]
                    name =      row[2]
                    sch_class = row[3]
                    status =    row[4]
                    run_days =  row[5]
                    orig =      row[6]
                    dest =      row[7]
                    direction = row[8]
                    record_data = self.x_field(schedule, 5) +\
                                  self.x_field(route, 10) +\
                                  self.x_field(name, 30) +\
                                  self.x_field(sch_class, 1) +\
                                  self.x_field(status, 1) +\
                                  self.x_field(run_days, 8) +\
                                  self.x_field(orig, 10) +\
                                  self.x_field(dest, 10) +\
                                  self.x_field(direction, 1)
                    f.write('21' + Params.get_date() + Params.get_time() + record_data + '\n')

            #train being updated
            data = (train, )
            sql = 'select train, type, station, status, schedule from train where train = ?'
            count, ds_trains = self.db_read(sql, data)
            if count > 0:
                for row in ds_trains:
                    train = row[0]
                    traintype = row[1]
                    station = row[2]
                    status = row[3]
                    schedule = row[4]
                    data = ('P', train)
                    sql =   'select cartype.oper_mode from cartype, car where car.cartype = cartype.cartype ' +\
                            'and cartype.oper_mode = ? and car.train = ?'
                    pass_cars, dummy = self.db_read(sql, data)
                    if pass_cars < 0:
                        return
                    record_data = self.x_field(train, 5) +\
                                  self.x_field(traintype, 1) +\
                                  self.x_field(station, 10) +\
                                  self.x_field(status, 1) +\
                                  self.x_field(schedule, 5) +\
                                  self.x_field(pass_cars, 5, 'R')
                    f.write('31' + Params.get_date() + Params.get_time() + record_data + '\n')

            #running info being updated
            if update_schedule:
                data = (train, )
                sql = 'select train, depart_station, arrive_station, ' +\
                      'est_depart, est_arrive, act_depart, act_arrive from running where train = ?'
                count, ds_runnings = self.db_read(sql, data)
                if count > 0:
                    for row in ds_runnings:
                        train = row[0]
                        departs = row[1]
                        arrives = row[2]
                        est_depart = row[3]
                        est_arrive = row[4]
                        act_depart = row[5]
                        act_arrive = row[6]
                        record_data = self.x_field(train, 5) +\
                                      self.x_field(departs, 10) +\
                                      self.x_field(arrives, 10) +\
                                      self.x_field(est_depart, 4) +\
                                      self.x_field(est_arrive, 4) +\
                                      self.x_field(act_depart, 4) +\
                                      self.x_field(act_arrive, 4)
                        f.write('41' + Params.get_date() + Params.get_time() + record_data + '\n')
        return
        

    def trains(self, message):
        """reports a train arriving or departing a station.  processing depends on whether it is
        an unscheduled train or a scheduled/extra train.   other train
        types need only update an existing timings record (which must exist)
        """
        if self.show_access(message, 'TRAINS (^route^);(direction[N/S/E/W/U/D])','R') != 0:
            return

        #work out the various parameters------------------------------------------------------------
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            filter_route = value
        else:
            filter_route = '*'

        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            filter_dir = value
        else:
            filter_dir = '*'

        # build the column titles
        titles = self.x_field('TRAIN=', 6) + ' ' +\
                 self.x_field('C', 1) + ' ' +\
                 self.x_field('TYPE', 4) + ' ' +\
                 self.x_field('ROUTE', self.routsize) + ' ' +\
                 self.x_field('SCHEDULE', self.schdsize) + ' ' +\
                 self.x_field('D', 1) + ' ' +\
                 self.x_field('ORIGINATING', self.staxsize) + ' ' +\
                 self.x_field('DESTINATION', self.staxsize) + ' ' +\
                 self.x_field('   ', 3) + ' ' +\
                 self.x_field('LAST STATION', self.staxsize) + ' ' +\
                 self.x_field('DUE.', 4) + ' ' +\
                 self.x_field('ACT.', 4) + ' ' +\
                 self.x_field('NEXT STATION', self.staxsize) + ' ' +\
                 self.x_field('EXP.', 4)                                           

        default_dir = 'x'
        data = ('C',)
        sql = 'select train.train, train.type, train.station, train.schedule, ' +\
              'schedule.class, schedule.route, schedule.orig_station,' +\
              'schedule.dest_station, schedule.direction ' +\
              'from train left outer join schedule on train.schedule = schedule.schedule ' +\
              'where train.status != ? order by schedule.orig_station'                                      #Rev 1
        count, ds_trains = self.db_read(sql, data)
        if count < 0:
            return

        counter = 0
        extract = {}
        for row in ds_trains:
            train = row[0]
            train_type = row[1]
            schedule = row[3]
            train_class = row[4]
            train_route = row[5]
            orig = row[6]
            dest = row[7]
            direction = row[8]

            if train_class == None:
                train_class = ''
            if train_route == None:
                train_route = ''
            if orig == None:
                orig = ''
            if dest == None:
                dest = ''
            if direction == None:
                direction = ''
            else:                                                          #Rev 1 start
                sql = 'select route.default_direction from route, schedule ' +\
                      'where schedule.route = route.route ' +\
                      'and schedule.schedule = ?'
                data = (schedule,)
                count, ds_route = self.db_read(sql, data)
                if count < 0:
                    return
                for route in ds_route:
                    default_dir = route[0]                                   #Rev 1 end
            
            if ((filter_route == train_route) or (filter_route == '*')):
                if ((filter_dir == direction) or (filter_dir == '*')):

                    counter = counter + 1
                    if train_type == 'S':
                        p_train_type = 'SCHD'
                    elif train_type == 'E':
                        p_train_type = 'XTRA'
                    else:
                        p_train_type = 'UNSC'
                    
                    sql = 'select '
                    last_report = '   '
                    last_station = '         '
                    last_est = '    '
                    last_act = '    '
                    thru_train = ' '
                    data = (train,)
                    
                    if (direction == default_dir) or (default_dir == 'x'):
                        sql = 'select depart_station, arrive_station, est_depart, est_arrive, ' +\
                              'act_depart, act_arrive from running where train = ? order by timings'
                    else:                                                   #Rev 1 else clause added
                        sql = 'select depart_station, arrive_station, est_depart, est_arrive, ' +\
                              'act_depart, act_arrive from running where train = ? order by timings DESC'
                    t_count, ds_run = self.db_read(sql, data)
                    if t_count < 0:
                        return
                    
                    next_item = 'Departure'
                    next_station = ''
                    next_est = '    '
                    terminates = ''
                    thru_train = ' '
                    
                    for t_row in ds_run:
                        terminates = ' '                                                                    #Rev 1
                        dep_station = t_row[0]
                        arr_station = t_row[1]
                        est_depart  = t_row[2]
                        est_arrive  = t_row[3]
                        act_depart  = t_row[4]
                        act_arrive  = t_row[5]
                        
                        if next_item == 'Departure':
                            next_station = 'DEP:'
                            next_est = est_depart
                            next_item = ''
                        
                        if next_item == 'Arrival':
                            if next_est != est_depart:
                                thru_train = '+'
                            next_item = ''

                        if act_depart != '':
                            last_report = 'DEP'
                            last_station = dep_station
                            last_est = est_depart
                            last_act = act_depart
                            next_station = arr_station
                            next_est = est_arrive
                            next_item = 'Arrival'
                        
                        if act_arrive != '':
                            last_report = 'ARR'
                            last_station = arr_station
                            last_est = est_arrive
                            last_act = act_arrive
                            next_item = 'Departure'
                        
                    if next_item == 'Departure':                                     #Rev  1
                        next_station = ' '                                          #Rev 1
                        next_est = '    '                                              #Rev 1

                    next_est = next_est + terminates + thru_train           #Rev 1
                    
                    extract[next_est + direction + train] = self.x_field(train, 6) + ' ' +\
                           self.x_field(train_class,1) + ' ' +\
                           self.x_field(p_train_type,4) + ' ' +\
                           self.x_field(train_route, self.routsize) + ' ' +\
                           self.x_field(schedule, self.schdsize) + ' ' +\
                           self.x_field(direction, 1) + ' ' +\
                           self.x_field(orig, self.staxsize) + ' ' +\
                           self.x_field(dest, self.staxsize) + ' ' +\
                           self.x_field(last_report, 3) + ' ' +\
                           self.x_field(last_station, self.staxsize) + ' ' +\
                           self.x_field(last_est, 4) + ' ' +\
                           self.x_field(last_act, 4) + ' ' +\
                           self.x_field(next_station, self.staxsize) + ' ' +\
                           self.x_field(next_est, 6)

        data_sort = list(extract.keys())
        data_sort.sort()
        line_count = 0
        for x in data_sort:
            if line_count == 0:
                print(titles)
            print(extract[x])
            line_count = line_count + 1
            if line_count > 22:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break
        print(' ** END OF DATA **')         
        return



    def licons(self, message, Params):
        """lists a consist for a train: first current train details, then a summary of
        train information.  If a Full list is required then show details of individual cars
        """
        if self.show_access(message, 'LICONS train;(report[F])','R') != 0:
            return

        #work out the various parameters
        train_id, rc = self.extract_field(message, 0, 'TRAIN ID')
        if rc > 1:   
            return

        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            full_consist = value
        else:
            full_consist = '*'

        # build the column titles
        col_of_lenc = self.railsize + self.carxsize + self.staxsize + self.classize + self.commsize + 24
        titles = self.x_field('----------', self.railsize) + ' ' +\
                 self.x_field('CAR=======', self.carxsize) + ' ' +\
                 self.x_field('DESTINATION', self.staxsize) + ' ' +\
                 self.x_field('========', 8) + ' ' +\
                 self.x_field('CUSTOMER', 10) + ' ' +\
                 self.x_field('BLOCK ', 6) + ' ' +\
                 self.x_field('CLASS=====', self.classize) + ' ' +\
                 self.x_field('COMMODITY=', self.commsize) + ' ' +\
                 self.x_field('-----', 5) + ' ' +\
                 self.x_field('-----', 5) 

        #get the train information
        sql = 'select train.train, train.type, train.station, train.schedule, ' +\
              'schedule.class, schedule.route, schedule.orig_station,' +\
              'schedule.dest_station, schedule.direction ' +\
              'from train ' +\
              'left outer join schedule on train.schedule = schedule.schedule ' +\
              'where train.train = ?'

        data = (train_id,)
        count, ds_trains = self.db_read(sql, data)
        if count < 0:
            return

        #return the train information and print a summary
        counter = 0
        line_count = 0
        for row in ds_trains:
            train = row[0]
            train_type = row[1]
            station = row[2]
            schedule = row[3]
            train_class = row[4]
            train_route = row[5]
            orig = row[6]
            dest = row[7]
            direction = row[8]
            if schedule == None:
                schedule = 'N/A'
            if train_class == None:
                train_class = 'N/A'
            if train_route == None:
                train_route = 'N/A'
            if orig == None:
                orig = 'N/A'
            if dest == None:
                dest = 'N/A'
            if direction == None:
                direction = 'N/A'

            counter = counter + 1
            if train_type == 'S':
                p_train_type = 'SCHD'
            elif train_type == 'E':
                p_train_type = 'XTRA'
            else:
                p_train_type = 'USCD'

            #go to the schedule and get the last reporting points
            last_report = '   '
            last_est = '    '
            last_act = '    '
            data = (train,)
            sql = 'select depart_station, arrive_station, est_depart, est_arrive, ' +\
                  'act_depart, act_arrive from running where train = ? order by timings'
            t_count, ds_run = self.db_read(sql, data)
            if t_count < 0:
                return
            for t_row in ds_run:
                act_depart = t_row[4]
                act_arrive = t_row[5]
                if act_depart != '':
                    last_report = 'DEP'
                    last_est = t_row[2]
                    last_act = t_row[4]
                if act_arrive != '':
                    last_report = 'ARR'
                    last_est = t_row[3]
                    last_act = t_row[5]

            short_orig = 'N/A'
            data = (orig,)
            sql = 'select short_name from station where station = ?'
            s_count, ds_stax = self.db_read(sql, data)
            if s_count < 0:
                return
            for s_row in ds_stax:
                short_orig = s_row[0]

            short_dest = 'N/A'
            data = (dest,)
            sql = 'select short_name from station where station = ?'
            s_count, ds_stax = self.db_read(sql, data)
            if s_count < 0:
                return
            for s_row in ds_stax:
                short_dest = s_row[0]

            short_station = 'N/A'
            data = (station,)
            sql = 'select short_name from station where station = ?'
            s_count, ds_stax = self.db_read(sql, data)
            if s_count < 0:
                return
            for s_row in ds_stax:
                short_station = s_row[0]

            print(' TRAIN:' + train + ' CLASS:' + train_class + ' TYPE:' + p_train_type +
                   ' ROUTE:' + train_route + ' SCHEDULE:' + schedule +
                   ' DIRECTION:' + direction)
            print('ORIG:' + orig + short_orig + ' DEST:' + dest + short_dest)

            #get a summary of the train information
            weight_count = 0
            length_count = 0
            load_count = 0
            empty_count = 0
            loco_hauls = 0                                                      #Rev 1
            data = (train_id,)
            sql = 'select locotype.length, locomotive.weight, locotype.haulage from locomotive, locotype ' +\
                  'where locomotive.train = ? ' +\
                  'and locomotive.locotype = locotype.locotype'                 #Rev 1
            loco_count, ds_locos = self.db_read(sql, data)
            if loco_count < 0:
                return
            for lrow in ds_locos:
                weight_count = weight_count + lrow[1]
                length_count = length_count + lrow[0]
                loco_hauls = loco_hauls + lrow[2]                               #Rev 1
            sql = 'select cartype.length, cartype.unladen_weight, ' +\
                  'car.weight_loaded, car.commodity, car.carclass ' +\
                  'from car, cartype ' +\
                  'where car.train = ? ' +\
                  'and car.cartype = cartype.cartype'
            car_count, ds_cars = self.db_read(sql, data)
            if car_count < 0:
                return
            pass_count = 0
            for crow in ds_cars:
                car_class = crow[4]
                car_commodity = crow[3]
                weight_count = weight_count + crow[1] + crow[2]
                length_count = length_count + crow[0]
                if car_commodity.strip() == '':                                  #Rev 1
                    passenger = Params.get_param_value('PASSENGER', 'XXX')       #Rev 1
                    if passenger == car_class:                                   #Rev 1
                        pass_count = pass_count + 1                              #Rev 1
                    else:                                                        #Rev 1
                        empty_count = empty_count + 1
                else:
                    load_count = load_count + 1
                

            print(last_report + ' AT: ' + station + short_station + ' DUE: ' + last_est + ' ACT: ' + last_act)
            print(' LOCOS: ' + str(loco_count) + ' PASS: ' + str(pass_count) + ' LOAD: ' + str(load_count) + ' MTY: ' + str(empty_count) +
                   ' LEN: ' + str(length_count) + ' HAUL: ' + str(loco_hauls) + 'WGHT:' + str(weight_count))  #Rev 1 

            if full_consist != 'F':
                return

            # build the column titles
            col_of_lenl = self.railsize + self.locosize + self.staxsize + 28
            coldiff = col_of_lenc - col_of_lenl
            if coldiff > 0:
                addin = col_of_lenc - col_of_lenl - 1
            print(self.x_field('RAILROAD==', self.railsize) + ' ' +\
                     self.x_field('LOCO======', self.locosize) + ' ' +\
                     self.x_field('POWER=', 6) + ' ' +\
                     self.x_field('TYPE==', 6) + ' ' +\
                     self.x_field('HAULS', 5, 'R') + ' ' +\
                     self.x_field('MODE==', 6) + ' ' +\
                     self.x_field('FUEL==', 5) + ' ' +\
                     self.x_field('HOME======', self.staxsize) + ' ' +\
                     self.x_field('         ', addin),
                     self.x_field('LNGTH', 5) + ' ' +\
                     self.x_field('WGHT=', 5) )

            #detail wanted, so get the loco details
            data = (train_id,)
            sql = 'select locomotive.railroad, locomotive.loco, ' +\
                  'locomotive.is_powered, locotype.power_type, locotype.haulage, ' +\
                  'locotype.oper_mode, locotype.length, locomotive.weight, locomotive.fuel, ' +\
                  'locomotive.home_station ' +\
                  'from locomotive, locotype '  +\
                  'where locomotive.train = ? ' +\
                  'and locomotive.locotype = locotype.locotype'
            loco_count, ds_locos = self.db_read(sql, data)
            if loco_count < 0:
                return
            for lrow in ds_locos:
                if lrow[2] == 'P':
                    powerstate = '      '
                else:
                    powerstate = 'UNPWRD'
                if lrow[3] == 'D':
                    plant = 'DIESEL'
                elif lrow[3] == 'E':
                    plant = 'ELCTRC'
                elif lrow[3] == 'S':
                    plant = 'STEAM '
                else:
                    plant = '      '
                if lrow[5] == 'I':
                    mode = '      '
                elif lrow[5] == 'D':
                    mode = 'SLAVE '
                elif lrow[5] == 'M':
                    mode = 'M.UNIT'
                else:
                    mode = 'OTHER '
                print(self.x_field(lrow[0], self.railsize) + " " +
                      self.x_field(lrow[1], self.locosize) + " " +
                      self.x_field(powerstate, 6) + " " +
                      self.x_field(plant, 6) + " " +
                      self.x_field(lrow[4], 5, 'R') + " " +
                      self.x_field(mode,6) + " " +
                      self.x_field(lrow[8], 5, 'R') + " " +
                      self.x_field(lrow[9], self.staxsize) + " " +
                      self.x_field('         ', addin) + " " +
                      self.x_field(lrow[6], 5, 'R') + " " +
                      self.x_field(lrow[7], 5, 'R'))

            #get the car details
            data = (train_id,)
            sql = 'select car.railroad, car.car,  place.station, ' +\
                  'station.short_name, waybill.destination, ' +\
                  'car.block, car.carclass, car.commodity, ' +\
                  'cartype.length, cartype.unladen_weight, ' +\
                  'car.weight_loaded ' +\
                  'from car, cartype ' +\
                  'left outer join waybill on car.carorder = waybill.id ' +\
                  'left outer join place on waybill.destination = place.industry  ' +\
                  'left outer join station on place.station = station.station ' +\
                  'where car.train = ? ' +\
                  'and car.cartype = cartype.cartype ' +\
                  'order by place.industry, car.block, car.railroad, car.car'
            car_count, ds_cars = self.db_read(sql, data)
            if car_count < 0:
                return

            line_count = 0
            for crow in ds_cars:
                railroad = crow[0]
                car = crow[1]
                if line_count == 0:
                    print(titles)
                station = crow[2]
                if station == None:
                    station = ''
                stax_name = crow[3]
                if stax_name == None:
                    stax_name = ''
                waybill_dest = crow[4]
                if waybill_dest == None:
                    waybill_dest = ''
                car_block = crow[5]
                car_class = crow[6]
                car_commodity = crow[7]
                car_length = crow[8]
                weight = crow[9] + crow[10]
                print(self.x_field(railroad, self.railsize) + " " +
                         self.x_field(car, self.carxsize) + " " +
                         self.x_field(station, self.staxsize) + " " +
                         self.x_field(stax_name, 8) + " " +
                         self.x_field(waybill_dest, 10) + " " +
                         self.x_field(car_block, 6) + " " +
                         self.x_field(car_class, self.classize) + " " +
                         self.x_field(car_commodity, self.commsize) + " " +
                         self.x_field(car_length, 5, 'R') + " " +
                         self.x_field(weight, 5, 'R'))
                line_count = line_count + 1

                if line_count > 20:
                    line_count = 0
                    reply = raw_input('+')
                    if reply == 'x':
                        break
        print(' ** END OF DATA **')         
        
        return



    def prcons(self, message, Params):
        if self.show_access(message, 'LICONS train;(report[F])','R') != 0:
            return

        #work out the various parameters
        train_id, rc = self.extract_field(message, 0, 'TRAIN ID')
        if rc > 1:   
            return

        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            full_consist = value
        else:
            full_consist = '*'

        # build the column titles
        col_of_lenc = self.railsize + self.carxsize + self.staxsize + self.classize + self.commsize + 24
        titles = self.x_field('RAILROAD==', self.railsize) + ' ' +\
                 self.x_field('CAR=======', self.carxsize) + ' ' +\
                 self.x_field('DESTINATION', self.staxsize) + ' ' +\
                 self.x_field('========', 8) + ' ' +\
                 self.x_field('CUSTOMER', 10) + ' ' +\
                 self.x_field('BLOCK ', 6) + ' ' +\
                 self.x_field('CLASS=====', self.classize) + ' ' +\
                 self.x_field('COMMODITY=', self.commsize) + ' ' +\
                 self.x_field('LNGTH', 5) + ' ' +\
                 self.x_field('WGHT=', 5) 

        #print attributes
        self.temp = {}
        row_no = 0

        #get the train information
        sql = 'select train.train, train.type, train.station, train.schedule, ' +\
              'schedule.class, schedule.route, schedule.orig_station,' +\
              'schedule.dest_station, schedule.direction ' +\
              'from train ' +\
              'left outer join schedule on train.schedule = schedule.schedule ' +\
              'where train.train = ?'

        data = (train_id,)
        count, ds_trains = self.db_read(sql, data)
        if count < 0:
            return

        #return the train information and print a summary
        counter = 0
        for row in ds_trains:
            train = row[0]
            train_type = row[1]
            station = row[2]
            schedule = row[3]
            train_class = row[4]
            train_route = row[5]
            orig = row[6]
            dest = row[7]
            direction = row[8]
            if schedule == None:
                schedule = 'N/A'
            if train_class == None:
                train_class = 'N/A'
            if train_route == None:
                train_route = 'N/A'
            if orig == None:
                orig = 'N/A'
            if dest == None:
                dest = 'N/A'
            if direction == None:
                direction = 'N/A'

            counter = counter + 1
            if train_type == 'S':
                p_train_type = 'SCHD'
            elif train_type == 'E':
                p_train_type = 'XTRA'
            else:
                p_train_type = 'USCD'

            #go to the schedule and get the last reporting points
            last_report = '   '
            last_est = '    '
            last_act = '    '
            data = (train,)
            sql = 'select depart_station, arrive_station, est_depart, est_arrive, ' +\
                  'act_depart, act_arrive from running where train = ? order by timings'
            t_count, ds_run = self.db_read(sql, data)
            if t_count < 0:
                return
            for t_row in ds_run:
                act_depart = t_row[4]
                act_arrive = t_row[5]
                if act_depart != '':
                    last_report = 'DEP'
                    last_est = t_row[2]
                    last_act = t_row[4]
                if act_arrive != '':
                    last_report = 'ARR'
                    last_est = t_row[3]
                    last_act = t_row[5]

            short_orig = 'N/A'
            data = (orig,)
            sql = 'select short_name from station where station = ?'
            s_count, ds_stax = self.db_read(sql, data)
            if s_count < 0:
                return
            for s_row in ds_stax:
                short_orig = s_row[0]

            short_dest = 'N/A'
            data = (dest,)
            sql = 'select short_name from station where station = ?'
            s_count, ds_stax = self.db_read(sql, data)
            if s_count < 0:
                return
            for s_row in ds_stax:
                short_dest = s_row[0]

            short_station = 'N/A'
            data = (station,)
            sql = 'select short_name from station where station = ?'
            s_count, ds_stax = self.db_read(sql, data)
            if s_count < 0:
                return
            for s_row in ds_stax:
                short_station = s_row[0]

            print_line =  ('TRAIN:' + train + ' ' +
                           'CLASS:' + train_class + ' ' +
                           'TYPE:' + p_train_type + ' ' +
                           'ROUTE:' + train_route + ' ' +
                           'SCHEDULE:' + schedule + ' ' +
                           'DIRECTION:' + direction)
            row_no = row_no + 1
            self.temp[row_no] = print_line
            print_line =  ('ORIG:' + orig+ ' ' +
                           short_orig+ ' ' +
                           'DEST:' + dest+ ' ' +
                           short_dest+ ' ' + 
                           last_report+ ' ' +
                           'AT:' + station + ' ' +
                           short_station)
            row_no = row_no + 1
            self.temp[row_no] = print_line

            #get a summary of the train information
            weight_count = 0
            length_count = 0
            load_count = 0
            empty_count = 0
            data = (train_id,)
            sql = 'select locotype.length, locomotive.weight from locomotive, locotype ' +\
                  'where locomotive.train = ? ' +\
                  'and locomotive.locotype = locotype.locotype'
            loco_count, ds_locos = self.db_read(sql, data)
            if loco_count < 0:
                return
            for lrow in ds_locos:
                weight_count = weight_count + lrow[1]
                length_count = length_count + lrow[0]
            sql = 'select cartype.length, cartype.unladen_weight, ' +\
                  'car.weight_loaded, car.commodity ' +\
                  'from car, cartype ' +\
                  'where car.train = ? ' +\
                  'and car.cartype = cartype.cartype'
            car_count, ds_cars = self.db_read(sql, data)
            if car_count < 0:
                return
            for crow in ds_cars:
                weight_count = weight_count + crow[1] + crow[2]
                length_count = length_count + crow[0]
                if row[3] == '':
                    empty_count = empty_count + 1
                else:
                    load_count = load_count + 1

            print_line =  ('DUE:' + last_est + ' ' +
                           'ACT:' + last_act + ' ' +
                           'LOCOS:' + str(loco_count) + ' ' +
                           'LOAD:' + str(load_count) + ' ' +
                           'MTY:' + str(empty_count) + ' ' +
                           'L:' + str(length_count) + ' ' +
                           'W:' + str(weight_count)) 
            row_no = row_no + 1
            self.temp[row_no] = print_line

            print_line = ' '
            row_no = row_no + 1
            self.temp[row_no] = print_line

            if full_consist != 'F':                                                 #Rev 1
                return

            # build the column titles
            col_of_lenl = self.railsize + self.locosize + self.staxsize + 28
            coldiff = col_of_lenc - col_of_lenl
            if coldiff > 0:
                addin = col_of_lenc - col_of_lenl - 1
            print_line = (self.x_field('RAILROAD==', self.railsize)     + ' '   +\
                     self.x_field('LOCO======', self.locosize)          + ' '  +\
                     self.x_field('POWER=', 6)                          + ' '  +\
                     self.x_field('TYPE==', 6) + ' '  +\
                     self.x_field('HAULS', 5, 'R') + ' '  +\
                     self.x_field('MODE==', 6) + ' '  +\
                     self.x_field('FUEL==', 5) + ' '  +\
                     self.x_field('HOME======', self.staxsize) + ' '  +\
                     self.x_field('         ', addin) + ' '   +\
                     self.x_field('LNGTH', 5) + ' '  +\
                     self.x_field('WGHT=', 5) )
            row_no = row_no + 1
            self.temp[row_no] = print_line

            #detail wanted, so get the loco details
            data = (train_id,)
            sql = 'select locomotive.railroad, locomotive.loco, ' +\
                  'locomotive.is_powered, locotype.power_type, locotype.haulage, ' +\
                  'locotype.oper_mode, locotype.length, locomotive.weight, locomotive.fuel, ' +\
                  'locomotive.home_station ' +\
                  'from locomotive, locotype '  +\
                  'where locomotive.train = ? ' +\
                  'and locomotive.locotype = locotype.locotype'
            loco_count, ds_locos = self.db_read(sql, data)
            if loco_count < 0:
                return
            for lrow in ds_locos:
                if lrow[2] == 'P':
                    powerstate = '      '
                else:
                    powerstate = 'UNPWRD'
                if lrow[3] == 'D':
                    plant = 'DIESEL'
                elif lrow[3] == 'E':
                    plant = 'ELCTRC'
                elif lrow[3] == 'S':
                    plant = 'STEAM '
                else:
                    plant = '      '
                if lrow[5] == 'I':
                    mode = '      '
                elif lrow[5] == 'D':
                    mode = 'SLAVE '
                elif lrow[5] == 'M':
                    mode = 'M.UNIT'
                else:
                    mode = 'OTHER '
                print_line = (self.x_field(lrow[0], self.railsize) + ' ' +
                      self.x_field(lrow[1], self.locosize) + ' ' +
                      self.x_field(powerstate, 6) + ' ' +
                      self.x_field(plant, 6) + ' ' +
                      self.x_field(lrow[4], 5, 'R') + ' ' +
                      self.x_field(mode,6) + ' ' +
                      self.x_field(lrow[8], 5, 'R') + ' ' +
                      self.x_field(lrow[9], self.staxsize) + ' ' +
                      self.x_field('         ', addin) + ' ' +
                      self.x_field(lrow[6], 5, 'R') + ' ' +
                      self.x_field(lrow[7], 5, 'R'))
                row_no = row_no + 1
                self.temp[row_no] = print_line

            print_line = ' '
            row_no = row_no + 1
            self.temp[row_no] = print_line

            print_line = titles
            row_no = row_no + 1
            self.temp[row_no] = print_line
            
            #get the car details
            data = (train_id,)
            sql = 'select car.railroad, car.car,  place.station, ' +\
                  'station.short_name, waybill.destination, ' +\
                  'car.block, car.carclass, car.commodity, ' +\
                  'cartype.length, cartype.unladen_weight, ' +\
                  'car.weight_loaded ' +\
                  'from car, cartype ' +\
                  'left outer join waybill on car.carorder = waybill.id ' +\
                  'left outer join place on waybill.destination = place.industry  ' +\
                  'left outer join station on place.station = station.station ' +\
                  'where car.train = ? ' +\
                  'and car.cartype = cartype.cartype ' +\
                  'order by place.industry, car.block, car.railroad, car.car'
            car_count, ds_cars = self.db_read(sql, data)
            if car_count < 0:
                return

            for crow in ds_cars:
                weight = crow[9] + crow[10]
                print_line =  (self.x_field(crow[0], self.railsize) + ' ' +
                         self.x_field(crow[1], self.carxsize) + ' ' +
                         self.x_field(crow[2], self.staxsize) + ' ' +
                         self.x_field(crow[3], 8) + ' ' +
                         self.x_field(crow[4], 10) + ' ' +
                         self.x_field(crow[5], 6) + ' ' +
                         self.x_field(crow[6], self.classize) + ' ' +
                         self.x_field(crow[7], self.commsize) + ' ' +
                         self.x_field(crow[8], 5, 'R') + ' ' +
                         self.x_field(weight, 5, 'R'))
                row_no = row_no + 1
                self.temp[row_no] = print_line

        #report the extracted data
        self.print_report (titles = titles,
                           report_id = 'PRCONS',
                           report_name = 'CONSIST FOR TRAIN ' + train_id,
                           Params = Params)      
        
        return


