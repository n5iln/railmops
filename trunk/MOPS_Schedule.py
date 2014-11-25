'''
Schedule Class
A Schedule is a movement along a Route with specific times and instructions.
A schedule contains the required running information for a train

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    Rev 1 Included schedule in sorted list for LSSCHD
          Corrected bad reference in CHSCHD
          Added TriMOPS handling in CXSCHD
          Added READY status for trains in LSSCHD
          Cancelled count added and message tidied in Z018
          Amended Z018 to delete running and train rows directly
          Removed planned arrival on LSSCHD; and changed column order
'''

import MOPS_Element

class cSchedules(MOPS_Element.cElement):
    """Details about Schedules.  Schedules are header records for timings between sections ie a
    schedule plus a list of timings is a timetable.  Schedules are allocated to a list of days of
    the week on which they run.  A schedule contains an originating station and a destination.
    The direction of a schedule must be either the same as or opposite to the route for which the
    schedule applies.  Schedules are either in Inactive (in edit mode), Active (availale for
    train running), Running (a train is running against the schedule) or Completed (a train has
    just finished running against the Schedule).
    """
    extract_code = 'select * from schedule'
    extract_header = 'id|code|route|name|status|class|rundays|origin|dest|direction\n'


    
    def adschd(self, message):
        """Adds a schedule against a route.  this schedule contains the days on which it runs,
        the timings says when it runs.  Schedule is created as Inactive.  Class indicates
        priority of schedule.  Rundays is in the form mtwtfssh as monday, tuesday, etc to sunday
        then a holiday marker.  days on which it should not run are marked with a dot eg if
        it runs mon, wed and fri then enter m.w.f...    origin and dest taken from the
        route section records.  direction is either same as route or opposite.
        """
        if self.show_access(message,
                            'ADSCHD schedule;^route^;name;class;rundays[12345678];direction[N/S/E/W/U/D]',
                            'S') != 0:
            return
        errors = 0

        #schedule code -----------------------------------------------------------------------------
        schedule, rc = self.extract_field(message, 0, 'SCHEDULE CODE')
        if rc > 0:
            return

        if len(schedule) > self.schdsize:
            print('* SCHEDULE CODE ENTERED IS GREATER THAN THE ALLOWED SIZE')
            return
        
        if len(schedule) ==0:
            print('* NO SCHEDULE CODE ENTERED: A BLANK CODE IS NOT ALLOWED')
            return

        #check it does not already exist
        data = (schedule,)
        sql = 'select id from schedule where schedule = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* SCHEDULE CODE ALREADY EXISTS')
            return

        #route -------------------------------------------------------------------------------------
        route, rc = self.extract_field(message, 1, 'ROUTE CODE')
        if rc > 0:
            return
        
        data = (route, )
        sql = 'select name, default_direction from route where route = ?'
        count, ds_routes = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            print('* ROUTE CODE DOES NOT EXIST (' + route + ')')
            return
        else:
            for row in ds_routes:
                route_name = row[0]
                default_direction = row[1]

        #schedule name -----------------------------------------------------------------------------
        schedule_name, rc = self.extract_field(message, 2, 'SCHEDULE NAME')
        if rc > 0:
            return

        #class -------------------------------------------------------------------------------------
        priority, rc = self.extract_field(message, 3, 'SCHEDULE CLASS PRIORITY')
        if rc > 0:
            return

        if not (priority == '1' or priority == '2' or priority == '3' or priority == '4' or priority == '5' or priority == '6' or priority == '7' or priority == '8' or priority == '9' or priority == 'X'):
            errors = errors + 1
            print('CLASS PRIORITY MUST BE 1 TO 9 OR X')

        #rundays -----------------------------------------------------------------------------------
        rundays, rc = self.extract_field(message, 4, 'RUN DAYS')
        if rc > 0:
            return

        if len(rundays) != 8:
            errors = errors + 1
            print('RUN DAYS MUST BE AS DAYS OF WEEK 12345678; SHOW NON-RUNNING AS .')

        try:
            mon = rundays[0]
            tue = rundays[1]
            wed = rundays[2]
            thu = rundays[3]
            fri = rundays[4]
            sat = rundays[5]
            sun = rundays[6]
            hol = rundays[7]
        except:
            print('* CANNOT DECODE RUNDAYS VALUE: MUST BE 12345678 OR .')
            errors = errors + 1
            return

        if not (mon == '1' or mon == '.'):
            print('* FIRST CHARACTER MUST BE 1 (MONDAY) OR .(DOT)')
            errors = errors + 1

        if not (tue == '2' or tue == '.'):
            print('* SECOND CHARACTER MUST BE 2 (TUESDAY) OR . (DOT)')
            errors = errors + 1
        
        if not (wed == '3' or wed == '.'):
            print('* THIRD CHARACTER MUST BE 3 (WEDNESDAY) OR . (DOT)')
            errors = errors + 1
        
        if not (thu == '4' or thu == '.'):
            print('* FOURTH CHARACTER MUST BE 4 (THURSDAY) OR . (DOT)')
            errors = errors + 1
        
        if not (fri == '5' or fri == '.'):
            print('* FIFTH CHARACTER MUST BE 5 (FRIDAY) OR . (DOT)')
            errors = errors + 1
        
        if not (sat == '6' or sat == '.'):
            print('* SIXTH CHARACTER MUST BE 6 (SATURDAY) OR . (DOT)')
            errors = errors + 1
        
        if not (sun == '7' or sun == '.'):
            print('* SEVENTH CHARACTER MUST BE 7 (SUNDAY) OR . (DOT)')
            errors = errors + 1
        
        if not (hol == '8' or hol == '.'):
            print('* EIGHTH CHARACTER MUST BE 8 (HOLIDAY) OR . (DOT)')
            errors = errors + 1

        if errors > 0:
            return
        
        #direction ---------------------------------------------------------------------------------
        direction, rc = self.extract_field(message, 5, 'DIRECTION')
        if rc > 0:
            return

        reverse = False
        if default_direction == 'N':
            if not(direction == 'N' or direction == 'S'):
                print('* DIRECTION MUST BE EITHER NORTHBOUND (DEFAULT) OR SOUTHBOUND')
                errors  = errors + 1
            if direction == 'S':
                reverse = True

        if default_direction == 'S':
            if not(direction == 'S' or direction == 'N'):
                print('* DIRECTION MUST BE EITHER SOUTHBOUND (DEFAULT) OR NORTHBOUND')
                errors  = errors + 1
            if direction == 'N':
                reverse = True

        if default_direction == 'E':
            if not(direction == 'E' or direction == 'W'):
                print('* DIRECTION MUST BE EITHER EASTBOUND (DEFAULT) OR WESTBOUND')
                errors  = errors + 1
            if direction == 'W':
                reverse = True

        if default_direction == 'W':
            if not(direction == 'E' or direction == 'W'):
                print('* DIRECTION MUST BE EITHER WESTBOUND (DEFAULT) OR EASTBOUND')
                errors  = errors + 1
            if direction == 'E':
                reverse = True

        if default_direction == 'U':
            if not(direction == 'U' or direction == 'D'):
                print('* DIRECTION MUST BE EITHER UP (DEFAULT) OR DOWN')
                errors  = errors + 1
            if direction == 'D':
                reverse = True

        if default_direction == 'D':
            if not(direction == 'D' or direction == 'S'):
                print('* DIRECTION MUST BE EITHER DOWN (DEFAULT) OR UP')
                errors  = errors + 1
            if direction == 'U':
                reverse = True

        if errors > 0:
            return

        #get additional default information, this will populate the schedule header record----------
        data = (route,)
        sql = 'select depart_station, arrive_station from section where route = ? order by section'
        count, ds_sections = self.db_read(sql, data)
        if count < 0:
            return

        first_thru = True
        for row in ds_sections:
            if first_thru:
                first_thru = False
                start_station = row[0]
            end_station = row[1]

        if reverse:
            hold_station = start_station
            start_station = end_station
            end_station = hold_station

        data = (start_station,)
        sql = 'select long_name from station where station = ?'
        count, ds_stations = self.db_read(sql, data)
        for row in ds_stations:
            start_name = row[0]

        data = (end_station,)
        sql = 'select long_name from station where station = ?'
        count, ds_stations = self.db_read(sql, data)
        for row in ds_stations:
            end_name = row[0]

        #carry out the update ----------------------------------------------------------------------
        data = (schedule, route, schedule_name, priority, 'I', rundays,
                start_station, end_station, direction)
        sql = 'insert into schedule values (null, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        if self.db_update(sql, data) != 0:
            return

        data = (route,)
        if reverse:
            sql = 'select section, arrive_station, depart_station from section ' +\
                  'where route = ? order by section desc'
        else:
            sql = 'select section, depart_station, arrive_station from section ' +\
                  'where route = ? order by section'
        count, ds_sections = self.db_read(sql, data)
        if count < 0:
            return
        for section_row in ds_sections:
            t2 = (section_row[0], schedule, section_row[1], section_row[2], '', '')
            sql = 'insert into timings values (null, ?, ?, ?, ?, ?, ?)'
            if self.db_update(sql, t2) != 0:
                print('* ERROR UPDATING DATABASE WITH SCHEDULE TIMINGS')
                return

        dir_name, runschedule = self.get_descs(direction, mon, tue, wed, thu, fri, sat,sun, hol)

        print('SCHEDULE ADDED FOR ROUTE' + route + route_name)
        print(schedule + schedule_name + dir_name + 'CLASS:' + priority + 'STATUS:INACTIVE')
        print('RUNS:' + runschedule)
        print('FROM:' + start_station + start_name + ' TO:' + end_station + end_name)
        return


    
    def chschd(self, message):
        """changes a schedule.  this schedule can only be changed if inactive.  Allow changes
        to the days on which it runs, class, name and description.  Class indicates
        priority of schedule.  Rundays is in the form mtwtfssh as monday, tuesday, etc to sunday
        then a holiday marker.  days on which it should not run are marked with a dot eg if
        it runs mon, wed and fri then enter m.w.f...   direction cannot be changed.
        """
        if self.show_access(message, 'ADSCHD code;(name);(class);(rundays[12345678])', 'S') != 0:
            return
        errors = 0

        #schedule code -----------------------------------------------------------------------------
        schedule, rc = self.extract_field(message, 0, 'SCHEDULE CODE')
        if rc > 0:
            return
        
        #check it exists
        data = (schedule,)
        sql = 'select route, name, status, run_days, orig_station, dest_station, direction, ' +\
              'class from schedule where schedule = ?'
        count, ds_schedules = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* SCHEDULE CODE DOES NOT EXIST')
            return
        else:
            for row in ds_schedules:
                route = row[0]
                schedule_name = row[1]
                schedule_status = row[2]
                rundays = row[3]
                direction = row[6]
                priority = row[7]

        if schedule_status != 'I':
            print('* SCHEDULE NOT IN INACTIVE STATUS, CANNOT BE AMENDED')
            return

        data = (route, )
        sql = 'select name, default_direction from route where route = ?'
        count, ds_routes = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            print('* ROUTE CODE DOES NOT EXIST (' + route + ')')                       #Rev 1
            return
        else:
            for row in ds_routes:
                route_name = row[0]

        #schedule name -----------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            schedule_name = value
        
        #class -------------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            priority = value
        
        if not (priority == '1' or priority == '2' or priority == '3' or priority == '4' or priority == '5' or priority == '6' or priority == '7' or priority == '8' or priority == '9' or priority == 'X'):
            errors = errors + 1
            print('CLASS PRIORITY MUST BE 1 TO 9 OR X')

        #rundays -----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 3, '')
        if rc == 0:
            rundays = value

        if len(rundays) != 8:
            errors = errors + 1
            print('RUN DAYS MUST BE AS DAYS OF WEEK 12345678; SHOW NON-RUNNING AS .')

        try:
            mon = rundays[0]
            tue = rundays[1]
            wed = rundays[2]
            thu = rundays[3]
            fri = rundays[4]
            sat = rundays[5]
            sun = rundays[6]
            hol = rundays[7]
        except:
            print('* CANNOT DECODE RUNDAYS VALUE: MUST BE MTWTFSSH OR .')
            errors = errors + 1
            return

        if not (mon == '1' or mon == '.'):
            print('* FIRST CHARACTER MUST BE 1 (MONDAY) OR .(DOT)')
            errors = errors + 1

        if not (tue == '2' or tue == '.'):
            print('* SECOND CHARACTER MUST BE 2 (TUESDAY) OR . (DOT)')
            errors = errors + 1
        
        if not (wed == '3' or wed == '.'):
            print('* THIRD CHARACTER MUST BE 3 (WEDNESDAY) OR . (DOT)')
            errors = errors + 1
        
        if not (thu == '4' or thu == '.'):
            print('* FOURTH CHARACTER MUST BE 4 (THURSDAY) OR . (DOT)')
            errors = errors + 1
        
        if not (fri == '5' or fri == '.'):
            print('* FIFTH CHARACTER MUST BE 5 (FRIDAY) OR . (DOT)')
            errors = errors + 1
        
        if not (sat == '6' or sat == '.'):
            print('* SIXTH CHARACTER MUST BE 6 (SATURDAY) OR . (DOT)')
            errors = errors + 1
        
        if not (sun == '7' or sun == '.'):
            print('* SEVENTH CHARACTER MUST BE 7 (SUNDAY) OR . (DOT)')
            errors = errors + 1
        
        if not (hol == '8' or hol == '.'):
            print('* EIGHTH CHARACTER MUST BE 8 (HOLIDAY) OR . (DOT)')
            errors = errors + 1

        if errors > 0:
            return
        
        #get additional default information --------------------------------------------------------
        data = (route,)
        sql = 'select depart_station, arrive_station from section ' +\
              'where route = ? order by section'
        count, ds_sections = self.db_read(sql, data)
        if count < 0:
            return

        first_thru = True
        for row in ds_sections:
            if first_thru:
                first_thru = False
                start_station = row[0]
            end_station = row[1]

        data = (start_station,)
        sql = 'select long_name from station where station = ?'
        count, ds_stations = self.db_read(sql, data)
        for row in ds_stations:
            start_name = row[0]

        data = (end_station,)
        sql = 'select long_name from station where station = ?'
        count, ds_stations = self.db_read(sql, data)
        for row in ds_stations:
            end_name = row[0]

        #carry out the update ---------------------------------------------------------------------
        data = (schedule_name, 'I', priority, rundays, schedule)
        sql = 'update schedule set name = ?, status = ?, class = ?, run_days = ? where schedule = ?'
        if self.db_update(sql, data) != 0:
            return

        dir_name, runschedule = self.get_descs(direction, mon, tue, wed, thu, fri, sat,sun, hol)
        print('SCHEDULE ADDED FOR ROUTE', route, route_name)
        print(schedule_name, dir_name, 'CLASS:' +priority, 'STATUS:INACTIVE')
        print('RUNS:', runschedule)
        print('FROM:' + start_station, start_name, ' TO:' + end_station, end_name)
        return



    def active(self, message):
        """activate a schedule - make it visible for train to run against.  For a schedule
        to be activated it must first check that all the times are consecutive (the station order
        will be correct as this will have been checked when the route was published
        """
        if self.show_access(message, 'ACTIVE schedule', 'S') != 0:
            return

        #schedule code
        schedule, rc = self.extract_field(message, 0, 'SCHEDULE CODE')
        if rc > 0:
            return
        data = (schedule, 'I')        

        #validate the change - check there is a record to process
        sql = 'select id, direction, route from schedule where schedule = ? and status == ?'
        count, ds_schedules = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* SCHEDULE CODE DOES NOT EXIST OR IS NOT IN INACTIVE STATUS')
            return
        else:
            for row in ds_schedules:
                direction = row[1]
                route = row[2]

        data = (route,)
        sql = 'select default_direction from route where route = ?'
        count, ds_routes = self.db_read(sql, data)
        if count < 0:
            return
        for route_row in ds_routes:
            default_dir = route_row[0]
            
        #validate the times
        data = (schedule,)
        if direction == default_dir:
            sql = 'select depart_station, arrive_station, planned_depart, planned_arrive ' +\
                  'from timings where schedule = ? order by section'
        else:
            sql = 'select depart_station, arrive_station, planned_depart, planned_arrive ' +\
                  'from timings where schedule = ? order by section desc'
        count, ds_timings = self.db_read(sql, data)
        if count < 0:
            return
        last_arrive = '0000'
        for row in ds_timings:
            planned_depart = row[2]
            planned_arrive = row[3]
            if planned_depart.strip() == '':
                planned_depart = '0000'
            if planned_arrive.strip() == '':
                planned_arrive = '0000'
            if planned_depart < last_arrive:
                if not((planned_depart < '0300') and (last_arrive > '2100')):
                    print('* INVALID TIME SEQUENCE AT STATION', row[0], ' ARRIVES', last_arrive, 'DEPARTS', planned_depart)
                    return
            last_arrive = planned_arrive
            if planned_arrive < planned_depart:
                if not((planned_arrive < '0300') and (planned_depart > '2100')):
                    print('* INVALID TIME SEQUENCE BETWEEN STATIONS', row[0], row[1])
                    return

        #update teh schedule
        data = ('A', schedule)
        sql = 'update schedule set status = ? where schedule = ?'
        if self.db_update(sql, data) != 0:
            return
        print('SCHEDULE ' + schedule + ' SET TO ACTIVE STATUS: AVAILABLE FOR TRAIN RUNNING')
        return
                


    def xctive(self, message):
        """deactivate a schedule - make it invisible for trains to run against.  Schedule must
        be in active status (ie no trains running against it, or not already in inactive status)
        """
        if self.show_access(message, 'XCTIVE schedule', 'S') != 0:
            return

        #schedule code
        schedule, rc = self.extract_field(message, 0, 'SCHEDULE CODE')
        if rc > 0:
            return
        data = (schedule, 'A')        

        #validate the change - check there is a record to set to inactive
        sql = 'select id from schedule where schedule = ? and status == ?'
        count, data = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* SCHEDULE CODE DOES NOT EXIST OR IS NOT IN ACTIVE STATUS')
            return
            
        data = ('I', schedule)
        sql = 'update schedule set status = ? where schedule = ?'
        if self.db_update(sql, data) != 0:
            return
        print('SCHEDULE ', schedule, ' SET TO INACTIVE STATUS: NOT AVAILABLE FOR TRAIN RUNNING')
        return



    def dxschd(self, message):
        """Deletes a Schedule plus all associated timings.  Only allowed if the
        schedule is in Inactive Status.  Also removes any instructions associated
        with the schedule
        """
        if self.show_access(message, 'DXSCHD schedule', 'S') != 0:
            return

        #schedule code
        schedule, rc = self.extract_field(message, 0, 'SCHEDULE CODE')
        if rc > 0:
            return
        data = (schedule, 'I')        

        #validate the change - check there is a record to delete
        sql = 'select id from schedule where schedule = ? and status == ?'
        count, data = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* SCHEDULE CODE DOES NOT EXIST OR IS NOT IN INACTIVE STATUS')
            return
            
        #process the change
        data = (schedule,)
        if self.db_update('delete from instructions where schedule = ?', data) == 0:
            print('INSTRUCTIONS ASSOCIATED WITH SCHEDULE HAVE BEEN DELETED')
        if self.db_update('delete from timings where schedule = ?', data) == 0:
            print('TIMINGS ASSOCIATED WITH SCHEDULE ', schedule, ' HAVE BEEN DELETED')
        if self.db_update('delete from schedule where schedule = ?', data) == 0:
            print('SCHEDULE ', schedule, ' SUCCESSFULLY DELETED')
        return



    def cpschd(self, message):
        """Copies an existing schedule to a new schedule.  Requires the name of the
        schedule to be copied from, the new name and the start time of the new
        schedule.  A new schedule is created, and the timings for the new schedule
        created based on the timings for the old schedule
        """
        if self.show_access(message,
                            'CPSCHD ^old schedule^;new schedule;new schedule name;start time',
                            'S') != 0:
            return

        #old schedule code ------------------------------------------------------------------
        old_schedule, rc = self.extract_field(message, 0, 'OLD SCHEDULE CODE')
        if rc > 0:
            return
        
        #check that it exists
        data = (old_schedule, 'A')
        sql = 'select route, run_days, orig_station, dest_station, direction, class ' +\
              'from schedule where schedule = ? and status = ?'
        count, ds_schedules = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* OLD SCHEDULE DOES NOT EXIST FOR COPYING')
            return
        else:
            for row in ds_schedules:
                route = row[0]
                run_days = row[1]
                orig_station = row[2]
                dest_station = row[3]
                direction = row[4]
                priority = row[5]

        #new schedule code --------------------------------------------------------------
        new_schedule, rc = self.extract_field(message, 1, 'NEW SCHEDULE CODE')
        if rc > 0:
            return
        
        if len(new_schedule) > self.schdsize:
            print('* SCHEDULE CODE ENTERED IS GREATER THAN THE ALLOWED SIZE')
            return
        
        if len(new_schedule) ==0:
            print('* NO SCHEDULE CODE ENTERED: A BLANK CODE IS NOT ALLOWED')
            return

        #check it does not already exist
        data = (new_schedule,)
        sql = 'select id from schedule where schedule = ?'
        count, ds_schedules = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* NEW SCHEDULE CODE ALREADY EXISTS')
            return

        #get the new name
        sched_name, rc = self.extract_field(message, 2, 'NEW SCHEDULE NAME')
        if rc > 0:
            return

        #get the new start time
        start_time, rc = self.extract_field(message, 3, 'NEW SCHEDULE START TIME')
        if rc > 0:
            return

        if len(start_time) != 4:
            print('* TIME MUST BE ENTERED IN FORMAT HHMM')
            return

        new_hours = int(start_time[0:2])
        if new_hours < 0 or new_hours > 23:
            print('* HOURS MUST BE ENTERED IN RANGE 00-23')
            return

        new_mins = int(start_time[2:4])
        if new_mins < 0 or new_mins > 59:
            print('* MINUTES MUST BE ENTERED IN RANGE 00-59')
            return

        #create the new schedule, and new timings records (offset by start time)
        data = (new_schedule, route, sched_name, priority, 'I', run_days, orig_station,
                dest_station, direction)
        sql = 'insert into schedule values (null, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        if self.db_update(sql, data) != 0:
            return

        data = (old_schedule,)
        sql = 'select section, schedule, depart_station, arrive_station, planned_depart, ' +\
              'planned_arrive from timings where schedule = ? order by id'
        count, ds_timings = self.db_read(sql, data)
        first_thru = True
        for row in ds_timings:
            old_depart = row[4]
            old_dep_hours = old_depart[0:2]
            old_dep_mins = old_depart[2:4]
            old_arrive = row[5]
            old_arr_hours = old_arrive[0:2]
            old_arr_mins = old_arrive[2:4]
            if first_thru:
                diff_hours = new_hours - int(old_dep_hours)
                diff_mins =  new_mins  - int(old_dep_mins)
                first_thru = False

            #work out the new departure time
            new_dep_hours = int(old_dep_hours) + diff_hours
            new_dep_mins  = int(old_dep_mins)  + diff_mins
            if new_dep_mins > 59:
                new_dep_hours = new_dep_hours + 1
                new_dep_mins =  new_dep_mins - 60
            if new_dep_mins < 0:
                new_dep_hours = new_dep_hours -1
                new_dep_mins =  new_dep_mins + 60
            if new_dep_hours < 0:
                new_dep_hours = new_dep_hours + 24
            if new_dep_hours > 23:
                new_dep_hours = new_dep_hours - 24
            new_dep_mins_s = str(new_dep_mins)
            new_dep_hours_s = str(new_dep_hours)
            if len(new_dep_mins_s) == 1:
                new_dep_mins_s = '0' + new_dep_mins_s
            if len(new_dep_hours_s) == 1:
                new_dep_hours_s = '0' + new_dep_hours_s
            new_departure = new_dep_hours_s + new_dep_mins_s

            #work out the new arrival time
            new_arr_hours = int(old_arr_hours) + diff_hours
            new_arr_mins  = int(old_arr_mins)  + diff_mins
            if new_arr_mins > 59:
                new_arr_hours = new_arr_hours + 1
                new_arr_mins =  new_arr_mins - 60
            if new_arr_mins < 0:
                new_arr_hours = new_arr_hours -1
                new_arr_mins = new_arr_mins + 60
            if new_arr_hours < 0:
                new_arr_hours = new_arr_hours + 24
            if new_arr_hours > 23:
                new_arr_hours = new_arr_hours - 24
            new_arr_mins_s = str(new_arr_mins)
            new_arr_hours_s = str(new_arr_hours)
            if len(new_arr_mins_s) == 1:
                new_arr_mins_s = '0' + new_arr_mins_s
            if len(new_arr_hours_s) == 1:
                new_arr_hours_s = '0' + new_arr_hours_s
            new_arrival = new_arr_hours_s + new_arr_mins_s

            data = (row[0], new_schedule, row[2], row[3], new_departure, new_arrival)
            sql = 'insert into timings values(null, ?, ?, ?, ?, ?, ?)'
            if self.db_update(sql, data) != 0:
                return
        print('NEW SCHEDULE CREATED', new_schedule)
        return


    def cxschd(self, message, Params):
        """cancel an active schedule for the current day
        """
        if self.show_access(message, 'CXSCHD schedule', 'R') != 0:
            return

        #schedule
        schedule, rc = self.extract_field(message, 0, 'SCHEDULE')
        if rc > 0:
            return

        data = (schedule, 'A')
        sql = 'select id from schedule where schedule = ? and status = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* SCHEDULE NOT FOUND OR NOT IN ACTIVE STATUS')
            return

        data = ('C', schedule)
        sql = 'update schedule set status = ? where schedule = ?'
        if self.db_update(sql, data) != 0:
            return

        #append the updated details to the history file   #Rev 1 - TriMOPS
        #see if we want to process the messages
        process_trimops = Params.get_param_value('TRIMOPS', 'NO')
        if process_trimops == 'YES':
            filename = self.directory + 'exMOPStrains.txt'
            with open(filename, "a") as f:
    
                #current list of schedules
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
                        f.write('29' + Params.get_date() + Params.get_time() + record_data + '\n')

        print('SCHEDULE ', schedule, ' SET TO CANCELLED FOR TODAY')
        return

        

    def lsschd(self, message):
        """lists all schedules active for today in either Active or Running Status
        """
        if self.show_access(message, 'LSSCHD', 'R') != 0:
            return

        titles = self.x_field('SCHEDULE==', self.schdsize) + ' ' +\
                 self.x_field('C', 1) + ' ' +\
                 self.x_field('ROUTE=====', self.routsize) + ' ' +\
                 self.x_field('ORIGIN====', self.staxsize) + ' ' +\
                 self.x_field('DESTINATN=', self.staxsize) + ' ' +\
                 self.x_field('TIME', 4) + ' ' +\
                 self.x_field('STATUS', 6) + ' ' +\
                 self.x_field('TRAIN', 10)

        data = ('S', 'R', 'A')
        sql = 'select schedule.schedule, schedule.route, schedule.class,  ' +\
                'schedule.status, schedule.orig_station, schedule.dest_station,  ' +\
                'train.train  ' +\
                'from schedule ' +\
                'left outer join train on (train.schedule = schedule.schedule and train.type = ?)  ' +\
                'where (schedule.status = ? or schedule.status = ?)  '
        count, ds_schedules = self.db_read(sql, data)
        if count < 0:
            return

        extract = {}
        for row in ds_schedules:
            schedule = row[0]
            route = row[1]
            schedule_c = row[2]
            status = row[3]
            orig_station = row[4]
            dest_station = row[5]
            train = row[6]
            if train == None:
                train = ''
            if status == 'A':
                status = 'ACTIVE'
            if status =='R':
                status = 'TRAIN*'
                
            sql = 'select id from running where train = ? and act_depart != ?'     #Rev 1
            data = (train, '')
            r_count, dummy = self.db_read (sql, data)
            if r_count < 0:
                return
            if (r_count == 0) and (status == 'TRAIN*'):
                status = '-READY'
                
            data2 = (schedule,)
            sql = 'select planned_depart, planned_arrive from timings ' +\
                  'where schedule = ? ' +\
                  'order by planned_depart'
            t_count, ds_timings = self.db_read(sql, data2)
            if t_count < 0:
                return
            got_arrival = False
            planned_depart = ''
            for row2 in ds_timings:
                if not got_arrival:
                    planned_depart = row2[0]
                    got_arrival = True
                
            extract[planned_depart + schedule] = self.x_field(schedule, self.schdsize) +' '+\
                   self.x_field(schedule_c, 1) +' '+\
                   self.x_field(route, self.routsize) +' '+\
                   self.x_field(orig_station, self.staxsize) +' '+\
                   self.x_field(dest_station, self.staxsize) +' '+\
                   self.x_field(planned_depart, 4) +' '+\
                   self.x_field(status, 6) +' '+\
                   self.x_field(train, 10)
        
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
        print(' ** END OF DATA: ' + str(line_count) + ' RECORDS DISPLAYED **')         
    

    def lischd(self, message):
        """list schedules on file, in start time order.  allow filtering by status, and
        if a day is entered filter it based on the runday
        """
        if self.show_access(message, 'LISCHD (status);(runday[12345678])', 'R') != 0:
            return
        
        #status
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            filter_status = value
        else:
            filter_status = ''

        #rundays
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            filter_runday = value
        else:
            filter_runday = ''
            
        # build the column titles
        name_size = 80 - self.schdsize - self.routsize - 29 - 2 * self.staxsize
        if name_size > 30:
            name_size = 30
        titles = self.x_field('SCHEDULE==', self.schdsize) + ' ' +\
                 self.x_field('ROUTE=====', self.routsize) + ' ' +\
                 self.x_field('NAME==========================', name_size) + ' ' +\
                 self.x_field('STATUS==', 8) + ' ' +\
                 self.x_field('RUN DAYS', 8) + ' ' +\
                 self.x_field('D', 1) + ' ' +\
                 self.x_field('C', 1) + ' ' +\
                 self.x_field('=DEP', 4) + ' ' +\
                 self.x_field('ORIG======', self.staxsize) + ' ' +\
                 self.x_field('DEST======', self.staxsize) 

        # get the extract data
        sql = 'select schedule, route, name, status, run_days, direction, class, ' +\
              'orig_station, dest_station from schedule'
        schedule_count, ds_schedules = self.db_read(sql, '')

        extract = {}
        if schedule_count < 0:
            return
        for seq_row in ds_schedules:
            rundays     = seq_row[4]
            status      = seq_row[3]
            schedule_id = seq_row[0]
            dep_stax    = seq_row[7]
            arr_stax    = seq_row[8]
            if filter_runday == '' or filter_runday == rundays[0:1] or filter_runday == rundays[1:2] or filter_runday == rundays[2:3] or filter_runday == rundays[3:4] or filter_runday == rundays[4:5] or filter_runday == rundays[5:6] or filter_runday == rundays[6:7] or filter_runday == rundays[7:8]:
                if filter_status == '' or filter_status == status:
                    data = (schedule_id, '')
                    sql = 'select planned_depart from timings where ' +\
                          'schedule = ? and planned_depart != ? order by id limit 1'
                    count, ds_timings = self.db_read(sql, data)
                    if count < 0:
                        return
                    depart = '    '
                    for seq_tim in ds_timings:
                        depart = seq_tim[0]
                    if seq_row[3] == 'I':
                        stat = 'INACTIVE'
                    elif seq_row[3] == 'A':
                        stat = 'ACTIVE  '
                    elif seq_row[3] == 'R':
                        stat = 'RUNNING '
                    else:
                        stat = 'COMPLETE'
                    extract[depart+schedule_id] = self.x_field(schedule_id, self.schdsize)+' '+\
                                       self.x_field(seq_row[1], self.routsize) + ' ' +\
                                       self.x_field(seq_row[2], name_size) + ' ' +\
                                       self.x_field(stat, 8) + ' ' +\
                                       self.x_field(seq_row[4], 8) + ' ' +\
                                       self.x_field(seq_row[5], 1) + ' ' +\
                                       self.x_field(seq_row[6], 1) + ' ' +\
                                       self.x_field(depart, 4) + ' ' +\
                                       self.x_field(dep_stax, self.staxsize) + ' ' +\
                                       self.x_field(arr_stax, self.staxsize)
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
        print(' ** END OF DATA: ' + str(schedule_count) + ' RECORDS DISPLAYED **')         
        return
            


    def prschd(self, message, Params):
        """prints schedules on file, in start time order.  allow filtering by status, and
        if a day is entered filter it based on the runday
        """
        if self.show_access(message, 'PRSCHD (status);(runday[12345678])', 'R') != 0:
            return
        extract = {}
        
        #status
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            filter_status = value
        else:
            filter_status = ''

        #rundays
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            filter_runday = value
        else:
            filter_runday = ''
            
        # build the column titles
        name_size = 80 - self.schdsize - self.routsize - 29
        if name_size > 30:
            name_size = 30
        titles = self.x_field('SCHEDULE==', self.schdsize) + ' ' +\
                 self.x_field('ROUTE=====', self.routsize) + ' ' +\
                 self.x_field('NAME=========================', name_size) + ' ' +\
                 self.x_field('STATUS==', 8) + ' ' +\
                 self.x_field('RUN DAYS', 8) + ' ' +\
                 self.x_field('D', 1) + ' ' +\
                 self.x_field('C', 1) + ' ' +\
                 self.x_field('=DEP', 4)

        # get the extract data
        sql = 'select schedule, route, name, status, run_days, direction, class from schedule'
        schedule_count, ds_schedules = self.db_read(sql, '')
        if schedule_count < 0:
            return
        for seq_row in ds_schedules:
            rundays = seq_row[4]
            status = seq_row[3]
            schedule_id = seq_row[0]
            if filter_runday == '' or filter_runday == rundays[0:1] or filter_runday == rundays[1:2] or filter_runday == rundays[2:3] or filter_runday == rundays[3:4] or filter_runday == rundays[4:5] or filter_runday == rundays[5:6] or filter_runday == rundays[6:7] or filter_runday == rundays[7:8]:
                if filter_status == '' or filter_status == status:
                    data = (schedule_id, '')
                    sql = 'select planned_depart from timings where schedule = ? ' +\
                          'and planned_depart != ? order by id limit 1'
                    count, ds_timings = self.db_read(sql, data)
                    if count < 0:
                        return
                    depart = '    '
                    for seq_tim in ds_timings:
                        depart = seq_tim[0]
                    if seq_row[3] == 'I':
                        stat = 'INACTIVE'
                    elif seq_row[3] == 'A':
                        stat = 'ACTIVE  '
                    else:
                        stat = 'RUNNING '
                    extract[depart + schedule_id]=self.x_field(schedule_id, self.schdsize) + ' ' +\
                                       self.x_field(seq_row[1], self.routsize) + ' ' +\
                                       self.x_field(seq_row[2], name_size) + ' ' +\
                                       self.x_field(stat, 8) + ' ' +\
                                       self.x_field(seq_row[4], 8) + ' ' +\
                                       self.x_field(seq_row[5], 1) + ' ' +\
                                       self.x_field(seq_row[6], 1) + ' ' +\
                                       self.x_field(depart, 4)
        data_sort = list(extract.keys())
        data_sort.sort()
        self.temp = {}
        for x in data_sort:
            self.temp[x] = extract[x]
            
        #report the extracted data ---------------------------------------
        self.print_report (titles = titles,
                           report_id = 'PRSCHD',
                           report_name = 'LIST OF SCHEDULES',
                           Params = Params)       
        return


        
    def Z008_set_schedules_to_cancel(self, Flash, Params):
        """For each Schedule in Active status, check the runday.  If the runday agrees with the day
        of the week (checking for holidays) then leave as running, otherwise mark as Completed
        """
        data = ('A',)
        sql = 'select id, run_days, schedule from schedule where status = ? order by id'
        count, ds_schedules = self.db_read(sql, data)
        if count < 1:
            return

        dow = Params.get_day_of_week()
        if dow == 'XXX':
            print('Z008: WARNING INVALID DAY OF WEEK ON PARAMETER FILE')
            return

        cancelled_count = 0                                                          #Rev 1
        for row in ds_schedules:
            schedule_id = row[0]
            rundays = row[1]

            set_to_running = False
            if dow == 'MON' and rundays[0:1] == '1':
                set_to_running = True
            elif dow == 'TUE' and rundays[1:2] == '2':
                set_to_running = True
            elif dow == 'WED' and rundays[2:3] == '3':
                set_to_running = True
            elif dow == 'THU' and rundays[3:4] == '4':
                set_to_running = True
            elif dow == 'FRI' and rundays[4:5] == '5':
                set_to_running = True
            elif dow == 'SAT' and rundays[5:6] == '6':
                set_to_running = True
            elif dow == 'SUN' and rundays[6:7] == '7':
                set_to_running = True
                print(dow, rundays)
            elif dow == 'HOL' and rundays[7:8] == '8':
                set_to_running = True

            if not set_to_running:
                cancelled_count = cancelled_count + 1
                data = ('C', schedule_id)
                sql = 'update schedule set status = ? where id = ?'
                if self.db_update(sql, data) != 0:
                    return
            
        print(Params.get_date() + ' ' + Params.get_time() + ' Z008: UNWANTED SCHEDULES (' + str(cancelled_count) + ') CANCELLED')
        return



    def Z018_set_schedules_to_active(self, Flash, Params):
        """For each Schedule in Completed status, set to Active.
        """
        #delete the train and associated timings for completed schedules        #Rev 1
        data = ('C',)
        sql = 'select train from train where status = ?'
        count, ds_trains = self.db_read(sql, data)
        if count < 0:
            return
        for trains in ds_trains:
            train = trains[0]
            data = (train,)
            sql = 'delete from running were train = ?'
            self.db_update(sql, data)
            sql = 'delete from train where train = ?'
            self.db_update(sql, data)
            
        
        #reset the schedule so it can accept a new train
        data = ('A', 'C')
        sql = 'update schedule set status = ? where status = ?'
        self.db_update(sql, data)
        print(Params.get_date() + ' ' + Params.get_time() + ' Z018: SCHEDULES SET TO ACTIVE')
        return
    


    def get_descs(self, direction, mon, tue, wed, thu, fri, sat, sun, hol):
        """get descriptions for direction and days
        """
        if direction == 'N':
            dir_name = 'NORTHBOUND'
        elif direction == 'S':
            dir_name = 'SOUTHBOUND'
        elif direction == 'E':
            dir_name = 'EASTBOUND'
        elif direction == 'W':
            dir_name = 'WESTBOUND'
        elif direction == 'U':
            dir_name = 'UP'
        elif direction == 'D':
            dir_name = 'DOWN'
        else:
            dir_name = 'NOT KNOWN'

        runschedule = ''
        if mon == '1':
            runschedule = 'MONDAY'
        if tue == '2':
            runschedule = runschedule + ' TUESDAY'
        if wed == '3':
            runschedule = runschedule + ' WEDNESDAY'
        if thu == '4':
            runschedule = runschedule + ' THURSDAY'
        if fri == '5':
            runschedule = runschedule + ' FRIDAY'
        if sat == '6':
            runschedule = runschedule + ' SATURDAY'
        if sun == '7':
            runschedule = runschedule + ' SUNDAY'
        if hol == '8':
            runschedule = runschedule + ' HOLIDAYS'

        return dir_name, runschedule
