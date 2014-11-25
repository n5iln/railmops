'''
Timings Class
Arrival and departure times for all Route Sections on a Route on a particular
schedule and shows the time into a section and the time out of a section

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    15/08/2010 Ver 1 Removed unused variables
                     Added handling of bad database return codes
'''

import MOPS_Element

class cTimings(MOPS_Element.cElement):
    """Details about Timings.  Inherits from ListHandler class.
    Timings are contained in fixed-length data records.   
    Id	                10 Automatically generated reference
    Section	        10 link to Section that timing is for
    Schedule	        10 Link to Schedule
    DepartStation	10 Copied from Route Section.
    ArrivalStation	10 Copied from Route Section.
    PlannedDepartTime	12 Planned departure time from station
    PlannedArriveTime	12 Planned arrival time at station
    """

    extract_code = 'select * from timings'
    extract_header = 'id|section|schedule|depart_station|arrive_station|planned_depart|planned_arrive\n'
    
    def adtims(self, message):
        """add timings to a section.  this is a basic addition process;
        other facilities will help copy/duplicate timings.  this process is a special
        process as, having been given a route, it will prompt for subsequent departure
        and arrival times until the route is complete.  the process can be abandoned by
        entering an x at the input prompt
        """

        if self.show_access(message, 'ADTIMS schedule', 'S') != 0:
            return

        #schedule code -----------------------------------------------------------------------------
        schedule, rc = self.extract_field(message, 0, 'SCHEDULE CODE')
        if rc > 0:
            return
        
        #check it exists
        data = (schedule, 'I')
        sql = 'select id, direction, route from schedule where schedule = ? and status = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* SCHEDULE CODE DOES NOT EXIST OR NOT IN INACTIVE STATUS')
            return

        print('SCHEDULE ENTRY MODE: ENTER TIME HHMM OR <X> TO QUIT')

        data = (schedule,)
        sql = 'select id, section, depart_station, arrive_station from timings ' +\
              'where schedule = ? order by id'
        count, ds_timings = self.db_read(sql, data)
        if count < 0:
            return
        last_time = '0000'
        for timing_row in ds_timings:
            #build the input prompt strings
            depart_station = timing_row[2]
            arrive_station = timing_row[3]

            t2 = (depart_station,)
            sql = 'select short_name from station where station = ?'
            count, ds_departs = self.db_read(sql, t2)
            if count < 0:
                return
            for station_row in ds_departs:
                depart_name = station_row[0]
            t2 = (arrive_station,)
            sql = 'select short_name from station where station = ?'
            count, ds_arrives = self.db_read(sql, t2)
            if count < 0:
                return
            for station_row in ds_arrives:
                arrive_name = station_row[0]

            #get the departing time
            re_enter = True
            while re_enter:
                new_time = raw_input('TIME DEPARTING ' + depart_station + ' ' + depart_name + ' >')
                if new_time == 'x':
                    print('EXITING INPUT OF TIMINGS FOR SCHEDULE')
                    return
                if self.validate_time(new_time, last_time) == 0:
                    departure_time = new_time
                    last_time = new_time
                    re_enter = False

            #get the arriving time
            re_enter = True
            while re_enter:
                new_time = raw_input('TIME ARRIVING  ' + arrive_station + ' ' + arrive_name + ' >')
                if new_time == 'x':
                    print('EXITING INPUT OF TIMINGS FOR SCHEDULE')
                    return
                if self.validate_time(new_time, last_time) == 0:
                    arrival_time = new_time
                    last_time = new_time
                    re_enter = False
        
            data = (departure_time, arrival_time, timing_row[0])
            sql = 'update timings set planned_depart = ?, planned_arrive = ? where id = ?'
            if self.db_update(sql, data) != 0:
                return

        print('UPDATE OF SCHEDULE TIMINGS FOR ' + schedule + ' COMPLETED')
        return



    def chtims(self, message):
        """allows changes to the timings of an individual section.  This routine can also
        be used for batch loading times from a file.  Enter the route, section and depart
        and arrive times.  note that there is no validation on timings on previous or
        following sections, only within the section itself.
        """
        if self.show_access(message, 'CHTIMS schedule;section;depart;arrive', 'S') != 0:
            return

        #schedule code -----------------------------------------------------------------------------
        schedule, rc = self.extract_field(message, 0, 'SCHEDULE CODE')
        if rc > 0:
            return

        #read the database
        data = (schedule, 'I')
        sql = 'select id from schedule where schedule = ? and status = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* SCHEDULE DOES NOT EXIST OR IS ACTIVE AND CANNOT BE AMENDED')
            return

        #section code-------------------------------------------------------------------------------
        section, rc = self.extract_field(message, 1, 'SECTION CODE')
        if rc > 0:
            return

        #read the database
        data = (schedule, section)
        sql = 'select depart_station, arrive_station, id from timings ' +\
              'where schedule = ? and section = ?'
        count, ds_sections = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* SCHEDULE/SECTION DOES NOT EXIST')
            return

        for row in ds_sections:
            departing = row[0]
            arriving = row[1]
            timings_id = row[2]

        #depart time -----------------------------------------------------------------
        depart_time, rc = self.extract_field(message, 2, 'DEPARTURE TIME')
        if rc > 0:
            return

        if len(depart_time) != 4:
            print('* TIME MUST BE ENTERED IN FORMAT HHMM')
            return

        hours = int(depart_time[0:2])
        if hours < 0 or hours > 23:
            print('* HOURS MUST BE ENTERED IN RANGE 00-23')
            return

        minutes = int(depart_time[2:4])
        if minutes < 0 or minutes > 59:
            print('* MINUTES MUST BE ENTERED IN RANGE 00-59')
            return

        #arrival time -----------------------------------------------------------------
        arrive_time, rc = self.extract_field(message, 3, 'ARRIVAL TIME')
        if rc > 0:
            return
        
        if self.validate_time(arrive_time, depart_time) != 0:
            return

        #carry out the update and report ----------------------------------------------
        data = (depart_time, arrive_time, timings_id)
        sql = 'update timings set planned_depart = ?, planned_arrive = ? where id = ?'
        if self.db_update(sql, data) != 0:
            return

        print('SCHEDULE TIMINGS CHANGED FOR:' + schedule, departing + ':' + depart_time + arriving + ':' + arrive_time)
        return
    

        
    def validate_time(self, hhmm, prev_time):
        """internal routine to validate a given time to make sure it corresponds
        to an hhmm format.  if a previous_time is entered then it makes sure that the
        new time is later, unless the previous time > 2000 (8pm) and the new time is
        less than 0400 (4am), in which case a new day is assumed
        """
        if len(hhmm) != 4:
            print('* TIME MUST BE ENTERED IN FORMAT HHMM')
            return 1

        try:
            hours = int(hhmm[0:2])
            if hours < 0 or hours > 23:
                print('* HOURS MUST BE ENTERED IN RANGE 00-23')
                return 2

            minutes = int(hhmm[2:4])
            if minutes < 0 or minutes > 59:
                print('* MINUTES MUST BE ENTERED IN RANGE 00-59')
                return 3
        except:
            print('* TIME MUST BE ENTERED IN MINUTES AND HOURS')
            return 5

        if prev_time > '2100':
            if hhmm < '0300':
                return 0
        
        if hhmm < prev_time:
            print('* NEW TIME MUST BE LATE THAN PREVIOUS TIME')
            return 4

        return 0


    def timing(self, message):
        """Lists times and associated information for a schedule, including station type,
        instructions
        """
        if self.show_access(message, 'TIMING schedule', 'R') != 0:
            return

        #schedule code -----------------------------------------------------------------------------
        schedule, rc = self.extract_field(message, 0, 'SCHEDULE CODE')
        if rc > 0:
            return
        
        #get the schedule detail to display
        data = (schedule,)
        sql = 'select name, direction, status, route, run_days from schedule where schedule = ?'
        count, ds_schedules = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('NO SCHEDULE TO DISPLAY')
            return
        else:
            for row in ds_schedules:
                schedule_name = row[0]
                schedule_dirn = row[1]
                schedule_stat = row[2]
                schedule_route = row[3]
                schedule_days = row[4]
        data = (schedule_route,)
        sql = 'select default_direction from route where route = ?'
        count, ds_routes = self.db_read(sql, data)
        if count < 0:
            return
        for row in ds_routes:
            default_direction = row[0]
        
        if schedule_dirn == 'N':
            direction = 'NORTH'
        elif schedule_dirn == 'S':
            direction = 'SOUTH'
        elif schedule_dirn == 'E':
            direction = 'EAST'
        elif schedule_dirn == 'W':
            direction = 'WEST'
        elif schedule_dirn == 'U':
            direction = 'UP'
        elif schedule_dirn == 'D':
            direction = 'DOWN'
        else:
            direction = 'NOT KNOWN'
        if schedule_stat == 'I':
            status = 'INACTIVE'
        elif schedule_stat == 'A':
            status = 'ACTIVE'
        elif schedule_stat == 'R':
            status = 'RUNNING'
        else:
            status = 'NOT KNOWN'

        rundays = ''
        if schedule_days[0:1] == '1':
            rundays = ' MON'
        if schedule_days[1:2] == '2':
            rundays = rundays + ' TUE'
        if schedule_days[2:3] == '3':
            rundays = rundays + ' WED'
        if schedule_days[3:4] == '4':
            rundays = rundays + ' THU'
        if schedule_days[4:5] == '5':
            rundays = rundays + ' FRI'
        if schedule_days[5:6] == '6':
            rundays = rundays + ' SAT'
        if schedule_days[6:7] == '7':
            rundays = rundays + ' SUN'
        if schedule_days[7:8] == '8':
            rundays = rundays + ' HOL'
        print('SCHEDULE:', schedule, schedule_name,' (SCHEDULE STATUS:' + status + ')')
        print('DIRECTION:',direction, ' RUNS:', rundays)

        data = (schedule,)
        sql = 'select instruction from instructions where schedule = ?'
        count, ds_instructions = self.db_read(sql, data)
        for row in ds_instructions:
            print(' - ', row[0])
        
        data = (schedule_route,)
        sql = 'select instruction from instructions where route = ?'
        count, ds_instructions = self.db_read(sql, data)
        for row in ds_instructions:
            print(' - ', row[0])
        print(' ' )
        
                    
        # build the column titles ------------------------------------------
        titles = self.x_field('STATION===', self.staxsize) + ' ' + \
                 self.x_field('NAME====', 8) + ' ' +\
                 self.x_field('TYPE======', self.statsize) + ' ' +\
                 self.x_field('=ARR', 4) + ' ' +\
                 self.x_field('=DEP', 4) + ' ' +\
                 self.x_field('INSTRUCTIONS =========================', 40)

        data = (schedule,)
        if default_direction == schedule_dirn:
            sql = 'select id, section, depart_station, arrive_station, planned_depart, ' +\
                  'planned_arrive from timings where schedule = ? order by section'
        else:
            sql = 'select id, section, depart_station, arrive_station, planned_depart, ' +\
                  'planned_arrive from timings where schedule = ? order by section DESC'
        timing_count, ds_timings = self.db_read(sql, data)
        if count < 0:
            return
        
        #report the extracted data -----------------------------------------
        line_count = 0
        arrival = '    '
        depart_station = ''
        arrive_station = ''
        arrive_name = ''
        depart_name = ''
        station_type = ''
        planned_arrive = ''
        dummy = ''
        instructions = ''
        for row in ds_timings:
            depart_station = row[2]
            arrive_station = row[3]
            planned_depart = row[4]
            planned_arrive = row[5]
            if line_count == 0:
                print(titles)

            #get the name for the departure station
            data = (depart_station,)
            sql = 'select short_name, stationtype from station where station = ?'
            stax_count, ds_departs = self.db_read(sql, data)
            if stax_count < 0:
                return
            for stax_row in ds_departs:
                depart_name = stax_row[0]
                station_type = stax_row[1]

            #get any station instructions - just print the first one
            sql = 'select instruction from instructions where station = ? limit 1'
            count, ds_instructions = self.db_read(sql, data)
            instructions = ' '
            for inst_row in ds_instructions:
                instructions = inst_row[0]

            if not(planned_depart.strip() == '' and planned_arrive.strip() == ''):
                print(self.x_field(row[2], self.staxsize) + " " +
                       self.x_field(depart_name, 8) + " " +
                       self.x_field(station_type, self.statsize) + " " +
                       self.x_field(arrival, 4) + " " +
                       self.x_field(row[4], 4) + " " +
                       self.x_field(instructions, 40))
                arrival = planned_arrive

            #get any station instructions - now print the rest
            sql = 'select instruction from instructions where station = ?'
            count, ds_instructions = self.db_read(sql, data)
            line = 0
            dummy = ' '
            for inst_row in ds_instructions:
                line = line + 1
                instructions = inst_row[0]
                if line != 1:
                    print(self.x_field(dummy, self.staxsize) + " " +
                           self.x_field(dummy, 8)  + " " +
                           self.x_field(dummy, self.statsize) + " " +
                           self.x_field(dummy, 4) + " " +
                           self.x_field(dummy, 4) + " " +
                           self.x_field(instructions, 40))

            
            line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break

        #get the long name for the arrive station (for the last entry)
        sql = 'select short_name, stationtype from station where station = ?'
        data = (arrive_station,)
        stax_count, ds_arrives = self.db_read(sql, data)
        for stax_row in ds_arrives:
            arrive_name = stax_row[0]
            station_type = stax_row[1]
                
        #get any station instructions - just print the first one
        sql = 'select instruction from instructions where station = ? limit 1'
        instructions = ' '
        count, ds_instructions = self.db_read(sql, data)
        for row in ds_instructions:
            instructions = row[0]

        print(self.x_field(arrive_station, self.staxsize) + " " +
               self.x_field(arrive_name, 8) + " " +
               self.x_field(station_type, self.statsize) + " " +
               self.x_field(planned_arrive, 4) + " " +
               self.x_field(dummy, 4) + " " +
               self.x_field(instructions, 40))

        #get any station instructions - now print the rest
        sql = 'select instruction from instructions where station = ?'
        count, ds_instructions = self.db_read(sql, data)
        line = 0 
        for row in ds_instructions:
            line = line + 1
            instructions = row[0]
            if line != 1:
                print(self.x_field(dummy, self.staxsize) + " " +
                       self.x_field(dummy, 8) + " " +
                       self.x_field(dummy, self.statsize) + " " +
                       self.x_field(dummy, 4) + " " +
                       self.x_field(dummy, 4) + " " +
                       self.x_field(instructions, 40))
                    
        print(' ** END OF DATA: ' + str(timing_count) + ' RECORDS DISPLAYED **')         
        
        return


    def ldtims(self, message):
        """Gives detail of Timing records for checking timetables vs routes
        """
        if self.show_access(message, 'LDTIMS schedule', 'R') != 0:
            return

        #schedule code -----------------------------------------------------------------------------
        schedule, rc = self.extract_field(message, 0, 'SCHEDULE CODE')
        if rc > 0:
            return
        
        #get the schedule detail to display
        data = (schedule,)
        sql = 'select name, direction, status, route from schedule where schedule = ?'
        count, ds_schedules = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('NO SCHEDULE TO DISPLAY')
            return
        else:
            for row in ds_schedules:
                schedule_name = row[0]
                schedule_dirn = row[1]
                schedule_stat = row[2]

        if schedule_dirn == 'N':
            direction = 'NORTH'
        elif schedule_dirn == 'S':
            direction = 'SOUTH'
        elif schedule_dirn == 'E':
            direction = 'EAST'
        elif schedule_dirn == 'WEST':
            direction = 'WEST'
        elif schedule_dirn == 'U':
            direction = 'UP'
        elif schedule_dirn == 'D':
            direction = 'DOWN'
        else:
            direction = 'NOT KNOWN'
        if schedule_stat == 'I':
            status = 'INACTIVE'
        elif schedule_stat == 'A':
            status = 'ACTIVE'
        elif schedule_stat == 'R':
            status = 'RUNNING'
        else:
            status = 'NOT KNOWN'
        print('SCHEDULE: ', schedule, schedule_name,' (SCHEDULE STATUS: ' + status + ')')
        print('       DIRECTION:',direction)

        # build the column titles ------------------------------------------
        titles = self.x_field('SECTION===', 10) + ' ' + \
                 self.x_field('DEPARTS===', self.staxsize) + ' ' +\
                 self.x_field('=DEP', 4) + ' ' +\
                 self.x_field('ARRIVES===', self.staxsize) + ' ' +\
                 self.x_field('=ARR', 4)

        data = (schedule,)
        sql = 'select id, section, depart_station, arrive_station, planned_depart, ' +\
              'planned_arrive from timings where schedule = ? order by section'
        timing_count, ds_timings = self.db_read(sql, data)
        if count < 0:
            return
        
        #report the extracted data -----------------------------------------
        line_count = 0
        for row in ds_timings:
            section        = row[1]
            depart_station = row[2]
            arrive_station = row[3]
            planned_depart = row[4]
            planned_arrive = row[5]
            if line_count == 0:
                print(titles)

            print(self.x_field(section       , 10) + " " +
                   self.x_field(depart_station, self.staxsize) + " " +
                   self.x_field(planned_depart, 4) + " " +
                   self.x_field(arrive_station, self.staxsize) + " " +
                   self.x_field(planned_arrive, 4))

            line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break

        print(' ** END OF DATA: ' + str(timing_count) + ' RECORDS DISPLAYED **')         
        
        return
        

    def prtims(self, message, Params):
        """Prints times and associated information for a schedule, including station type,
        instructions
        """
        if self.show_access(message, 'PRTIMS schedule', 'R') != 0:
            return

        #schedule code -----------------------------------------------------------------------------
        schedule, rc = self.extract_field(message, 0, 'SCHEDULE CODE')
        if rc > 0:
            return
        self.temp = {}
        i = 0
        
        #get the schedule detail to display
        data = (schedule,)
        sql = 'select name, direction, status, route from schedule where schedule = ?'
        count, ds_schedules = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('NO SCHEDULE TO DISPLAY')
            return
        else:
            for row in ds_schedules:
                schedule_name = row[0]
                schedule_dirn = row[1]
                schedule_stat = row[2]
                schedule_route = row[3]

        if schedule_dirn == 'N':
            direction = 'NORTH'
        elif schedule_dirn == 'S':
            direction = 'SOUTH'
        elif schedule_dirn == 'E':
            direction = 'EAST'
        elif schedule_dirn == 'WEST':
            direction = 'WEST'
        elif schedule_dirn == 'U':
            direction = 'UP'
        elif schedule_dirn == 'D':
            direction = 'DOWN'
        else:
            direction = 'NOT KNOWN'
        if schedule_stat == 'I':
            status = 'INACTIVE'
        elif schedule_stat == 'A':
            status = 'ACTIVE'
        elif schedule_stat == 'R':
            status = 'RUNNING'
        else:
            status = 'NOT KNOWN'
        print_line = ('SCHEDULE: ' + schedule + ' ' + schedule_name +'  (SCHEDULE STATUS:' + status + ')')
        self.temp[i]= print_line
        i = i + 1
        print_line = ('       DIRECTION: ' + direction)
        self.temp[i]= print_line
        i = i + 1

        t = (schedule,)
        sql = 'select instruction from instructions where schedule = ?'
        count, ds_instructions = self.db_read(sql, t)
        for row in ds_instructions:
            print_line = (' - ' + row[0])
            self.temp[i]= print_line
            i = i + 1
        
        t = (schedule_route,)
        sql = 'select instruction from instructions where route = ?'
        count, ds_instructions = self.db_read(sql, t)
        for row in ds_instructions:
            print_line = (' - ' + row[0])
            self.temp[i]= print_line
            i = i + 1
        print_line = (' ' )
        self.temp[i]= print_line
        i = i + 1
        
                    
        # build the column titles ------------------------------------------
        titles = self.x_field('STATION===', self.staxsize) + ' ' + \
                 self.x_field('NAME====', 8) + ' ' +\
                 self.x_field('TYPE======', self.statsize) + ' ' +\
                 self.x_field('=ARR', 4) + ' ' +\
                 self.x_field('=DEP', 4) + ' ' +\
                 self.x_field('INSTRUCTIONS =========================', 40)

        data = (schedule,)
        sql = 'select id, section, depart_station, arrive_station, planned_depart, ' +\
              'planned_arrive from timings where schedule = ? order by id'
        timing_count, ds_timings = self.db_read(sql, data)
        if timing_count < 0:
            return
        
        #report the extracted data -----------------------------------------
        arrival = '    '
        for row in ds_timings:
            depart_station = row[2]
            arrive_station = row[3]
            planned_depart = row[4]
            planned_arrive = row[5]

            #get the name for the departure station
            data = (depart_station,)
            sql = 'select short_name, stationtype from station where station = ?'
            stax_count, ds_departs = self.db_read(sql, data)
            if stax_count < 0:
                return
            for stax_row in ds_departs:
                depart_name = stax_row[0]
                station_type = stax_row[1]

            #get any station instructions - just print the first one
            sql = 'select instruction from instructions where station = ? limit 1'
            count, ds_instructions = self.db_read(sql, data)
            instructions = ' '
            for inst_row in ds_instructions:
                instructions = inst_row[0]

            if not(planned_depart.strip() == '' and planned_arrive.strip() == ''):
                print_line =  (self.x_field(depart_station, self.staxsize) + ' ' +
                       self.x_field(depart_name, 8) + ' ' +
                       self.x_field(station_type, self.statsize) + ' ' +
                       self.x_field(arrival, 4) + ' ' +
                       self.x_field(planned_depart, 4) + ' ' +
                       self.x_field(instructions, 40))
                arrival = planned_arrive
                self.temp[i]= print_line
                i = i + 1
                
            #get any station instructions - now print the rest
            sql = 'select instruction from instructions where station = ?'
            count, ds_instructions = self.db_read(sql, data)
            line = 0
            dummy = ' '
            for inst_row in ds_instructions:
                line = line + 1
                instructions = inst_row[0]
                if line != 1:
                    print_line = (self.x_field(dummy, self.staxsize) + ' ' +
                           self.x_field(dummy, 8) + ' ' +
                           self.x_field(dummy, self.statsize) + ' ' +
                           self.x_field(dummy, 4) + ' ' +
                           self.x_field(dummy, 4) + ' ' +
                           self.x_field(instructions, 40))
                    self.temp[i]= print_line
                    i = i + 1

        #get the long name for the arrive station (for the last entry)
        sql = 'select short_name, stationtype from station where station = ?'
        data = (arrive_station,)
        stax_count, ds_arrives = self.db_read(sql, data)
        for stax_row in ds_arrives:
            arrive_name = stax_row[0]
            station_type = stax_row[1]
                
        #get any station instructions - just print the first one
        sql = 'select instruction from instructions where station = ? limit 1'
        instructions = ' '
        count, ds_instructions = self.db_read(sql, data)
        for row in ds_instructions:
            instructions = row[0]

        print_line = (self.x_field(arrive_station, self.staxsize) + ' ' +
               self.x_field(arrive_name, 8) + ' ' +
               self.x_field(station_type, self.statsize) + ' ' +
               self.x_field(planned_arrive, 4) + ' ' +
               self.x_field(dummy, 4) + ' ' +
               self.x_field(instructions, 40))
        self.temp[i]= print_line
        i = i + 1

        #get any station instructions - now print the rest
        sql = 'select instruction from instructions where station = ?'
        count, ds_instructions = self.db_read(sql, data)
        line = 0 
        for row in ds_instructions:
            line = line + 1
            instructions = row[0]
            if line != 1:
                print_line = (self.x_field(dummy, self.staxsize) + ' ' +
                       self.x_field(dummy, 8) + ' ' +
                       self.x_field(dummy, self.statsize) + ' ' +
                       self.x_field(dummy, 4) + ' ' +
                       self.x_field(dummy, 4) + ' ' +
                       self.x_field(instructions, 40))
                self.temp[i]= print_line
                i = i + 1
                    
        #report the extracted data ---------------------------------------
        self.print_report (titles = titles,
                           report_id = 'PRTIMS',
                           report_name = 'TIMETABLE FOR ' + schedule,
                           Params = Params)
        return
