'''
Routes Class
A route defines a method of moving from one station to another

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    Rev 1 Unused variables removed

'''
import MOPS_Element

class cRoutes(MOPS_Element.cElement):
    """details about routes - these are header records for route sections.  Routes have a status
    (incomplete - being built; draft - validated but not available for timetabling; published -
    available for timetabling). routes also have a default direction east / west / north / south
    up / down (up/down for uk users)
    """
    extract_code = 'select * from route'
    extract_header = 'id|route|name|status|default direction\n'



    def adrout(self, message, Params):
        """creates a new route header.  the route includes a default direction, and the status
        is set to incomplete
        """
        if self.show_access(message, 'ADROUT route;route name', 'S') != 0:        #Rev 1
            return

        #route code---------------------------------------------------------------------------------
        route, rc = self.extract_field(message, 0, 'ROUTE CODE')
        if rc > 0:
            return
        
        if len(route) > self.routsize:
            print('* ROUTE CODE ENTERED IS GREATER THAN THE ALLOWED SIZE')
            return
        
        if len(route) ==0:
            print('* NO ROUTE CODE ENTERED: A BLANK CODE IS NOT ALLOWED')
            return

        #--------------------------------------------------------------------------------------------
        #read the database and populate the fields
        data = (route,)
        sql = 'select * from route where route = ?'
        count, dummy = self.db_read(sql, data)

        if count < 0:
            return
        if count != 0:
            print('* ROUTE CODE ALREADY EXISTS')
            return

        #route name---------------------------------------------------------------------------------
        route_name, rc = self.extract_field(message, 1, 'ROUTE NAME')
        if rc > 0:
            return

        #route direction----------------------------------------------------------------------------
        #Rev 1 default direction now obtained from parameter file
        default_direction = Params.get_param_value('DIRECTION', 'W')

        #carry out the update-----------------------------------------------------------------------
        data = (route, route_name, 'I', default_direction)
        sql = 'insert into route values (null, ?, ?, ?, ?)'
        if self.db_update(sql, data) != 0:
            return

        #report the change to the screen
        print('NEW ROUTE HEADER ADDED SUCCESSFULLY')
        print(route + route_name + ' DEFAULT DIRECTION:' + default_direction)
        return 



    def chrout(self, message):
        """change the name of a route.  because routes are set up with a given default direction,
        and there may already be sections in place based on the direction, the default
        direction cannot be changed.  
        """
        if self.show_access(message, 'CHROUT route;route name', 'S') != 0:
            return

        #route code---------------------------------------------------------------------------------
        route, rc = self.extract_field(message, 0, 'ROUTE CODE')
        if rc > 0:
            return

        data = (route,)
        sql = 'select name from route where route = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* ROUTE CODE DOES NOT EXIST')
            return
        
        #route name---------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            route_name = value

        #carry out the update and report the change-------------------------------------------------
        data = (route_name, route)
        sql = 'update route set name = ? where route = ?'
        if self.db_update(sql, data) != 0:
            return

        print('ROUTE NAME CHANGED SUCCESSFULLY')
        print(route + route_name)
        return 



    def dxrout(self, message):
        """deletes a route and sections from the database.  only allows delete if route is in draft
        or incomplete status.  also deletes any associated sections or instructions"""
        if self.show_access(message, 'DXROUT route', 'S') != 0:
            return

        #route code---------------------------------------------------------------------------------
        route, rc = self.extract_field(message, 0, 'ROUTE CODE')
        if rc > 0:
            return

        #validate the change - check there is a record to delete------------------------------------
        data = (route, 'P')        
        sql = 'select id from route where route = ? and status != ?'
        count, data = self.db_read(sql, data)
        
        if count < 0:
            return
        if count == 0:
            print('* ROUTE CODE DOES NOT EXIST OR IS IN PUBLISHED STATUS AND CANNOT BE DELETED')
            return
            
        #process the change-------------------------------------------------------------------------
        data = (route,)
        if self.db_update('delete from instructions where route = ?', data) == 0:
            print('INSTRUCTIONS ASSOCIATED WITH ROUTE HAVE BEEN DELETED')
        if self.db_update('delete from section where route = ?', data) == 0:
            print('SECTIONS ASSOCIATED WITH ROUTE' + route + 'HAVE BEEN DELETED')
        if self.db_update('delete from route where route = ?', data) == 0:
            print('ROUTE' + route + 'SUCCESSFULLY DELETED')
        return
       


    def validr(self, message):
        """validates a route, making sure that the stations along the way are contiguous.
        if all the sections are contiguous the route is set to draft status
        """
        if self.show_access(message, 'VALIDR route', 'S') != 0:
            return

        #route code---------------------------------------------------------------------------------
        route, rc = self.extract_field(message, 0, 'ROUTE CODE')
        if rc > 0:
            return

        #validate the route exists and get the route name-------------------------------------------
        data = (route, 'I')
        sql = 'select name from route where route = ? and status = ?'
        count, ds_routes = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            print('* ROUTE NOT FOUND OR NOT IN INCOMPLETE STATUS')
            return

        for row in ds_routes:
            route_name = row[0]

        print('VALIDATING ROUTE FOR' + route_name)

        #read the route sections in order-----------------------------------------------------------
        data = (route,)
        sql = 'select route, section, depart_station, arrive_station from section ' +\
              'where route = ? order by section'
        count, ds_sections = self.db_read(sql, data)

        linecount = 0
        arrival = ''
        for row in ds_sections:

            #get departure station from the section
            section = row[1]
            depart_station = row[2]
            arrive_station = row[3]
            data = (depart_station,)
            sql = 'select short_name from station where station = ?'
            count, ds_stations = self.db_read(sql, data)
            if count < 0:
                return
            if count == 0:
                print('* STATION ON ROUTE IS NO LONGER VALID' + depart_station)
                return
            for ro2 in ds_stations:
                depart_name = ro2[0]

            #for the departure, get the arrival
            sql = 'select short_name from station where station = ?'
            data = (arrive_station,)
            count, ds_stations = self.db_read(sql, data)
            if count < 0:
                return
            if count == 0:
                print('* STATION ON ROUTE IS NO LONGER VALID' + arrive_station)
                return
            for ro2 in ds_stations:
                arrive_name = ro2[0]

            #check the previous arrival from the current departure
            if linecount != 0:
                if str(depart_station) != str(arrival):
                    print('SEQUENCE:' + str(section), 'FROM:' +
                           depart_station + '<<< DOES NOT MATCH PREVIOUS DEPARTURE')
                    print('* SECTIONS ARE NOT CONTIGUOUS, CANNOT SET TO DRAFT *')
                    return
            arrival = arrive_station
            print('SEQUENCE:' + str(section) + 'FROM:' + depart_station + depart_name + 'TO:' +
                   arrive_station + arrive_name)
            linecount = linecount + 1

        data = ('D', route)
        sql = 'update route set status = ? where route = ?'
        if self.db_update(sql, data) != 0:
            return
        print('ROUTE VALIDATED: SET TO DRAFT STATUS')
        return



    def publsh(self, message):
        """publish a route from draft status.  this makes it available for scheduling
        """
        if self.show_access(message, 'PUBLSH route', 'S') != 0:
            return

        #route code---------------------------------------------------------------------------------
        route, rc = self.extract_field(message, 0, 'ROUTE CODE')
        if rc > 0:
            return

        data = (route, 'D')

        #get the route details----------------------------------------------------------------------
        sql = 'select name from route where route = ? and status = ?'
        count, ds_routes = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* ROUTE NOT FOUND OR NOT IN DRAFT STATUS')
            return
        for row in ds_routes:
            route_name = row[0]

        #get the section details--------------------------------------------------------------------
        print('PUBLISHING ROUTE FOR' + route_name)

        data = (route,)
        sql = 'select * from section where route = ? order by section'
        count, ds_sections = self.db_read(sql, data)

        for row in ds_sections:
            sql = 'select short_name from station where station = ?'
            data = (row[3],)
            count, stations = self.db_read(sql, data)
            for ro2 in stations:
                depart_name = ro2[0]

            sql = 'select short_name from station where station = ?'
            data = (row[4],)
            count, stations = self.db_read(sql, data)
            for ro2 in stations:
                arrive_name = ro2[0]

            print(route + row[3] + depart_name + '--' + row[4] + arrive_name)
        
        #update the route to published status-------------------------------------------------------
        data = ('P', route)
        sql = 'update route set status = ? where route = ?'
        if self.db_update(sql, data) != 0:
            return
        print('ROUTE SET TO PUBLISHED STATUS')
        return



    def unpubl(self, message):
        """set a route already published to draft status.  the route must not be being used
        on any schedule
        """
        if self.show_access(message, 'UNPUBL route', 'S') != 0:
            return

        #route code---------------------------------------------------------------------------------
        route, rc = self.extract_field(message, 0, 'ROUTE CODE')
        if rc > 0:
            return

        #check that the route is already in published status----------------------------------------
        data = (route, 'P')
        sql = 'select name from route where route = ? and status = ?'
        count, ds_routes = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* ROUTE NOT FOUND OR NOT IN PUBLISHED STATUS')
            return
        for row in ds_routes:
            route_name = row[0]

        #check that no schedules exist against this route-------------------------------------------
        data = (route,)
        sql = 'select id from schedule where route = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* SCHEDULES EXIST AGAINST THIS ROUTE, CANNOT UNPUBLISH')
            return

        #update the route to draft status-----------------------------------------------------------
        data = ('D', route)
        sql = 'update route set status = ? where route = ?'
        if self.db_update(sql, data) != 0:
            return
        print(route + route_name + 'RESET TO DRAFT STATUS')
        return

        

    def lirout(self, message):
        """list all routes to the screen.  the routes are always displayed in name order.
        """
        if self.show_access(message, 'LIROUT', 'R') != 0:
            return        
            
        # build the column titles-------------------------------------------------------------------
        name_size = 80 - self.routsize - 2 * self.staxsize - 14
        if name_size > 30:
            name_size = 30
        titles = self.x_field('ROUTE=====', self.routsize) + ' ' +\
                 self.x_field('NAME=========================', name_size) + ' ' +\
                 self.x_field('DIR', 3) + ' ' +\
                 self.x_field('STATUS', 6) + ' ' +\
                 self.x_field('DEPART===============', 9 + self.staxsize) + ' ' +\
                 self.x_field('ARRIVE===============', 9 + self.staxsize)
        
        # get the extract data----------------------------------------------------------------------
        sql = 'select route, name, status, default_direction from route order by route'
        route_count, ds_routes = self.db_read(sql, '')
        if route_count < 0:
            return

        line_count = 0
        for row in ds_routes:
            route = row[0]
            status = row[2]
            if line_count == 0:
                print(titles)
            if status == 'I':
                status_desc = 'INCMPL'
            elif status == 'D':
                status_desc = 'DRAFT '
            else:
                status_desc = 'PUBLSH'

            #get the sections fo rthe route
            sql = 'select depart_station, arrive_station from section where route = ? ' +\
                  'order by section'
            data = (route,)
            count, ds_sections = self.db_read(sql, data)
            if count < 0:
                return
            first_thru = True
            arriving = ''
            departing = ''
            departing_stax = ''
            depart_stax = ''
            arrive_stax = ''
            for sect in ds_sections:
                depart_stax = sect[0]
                arrive_stax = sect[1]

                if first_thru:
                    data = (depart_stax,)
                    sql = 'select short_name from station where station = ?'
                    count, ds_stationsa = self.db_read(sql, data)
                    for departs in ds_stationsa:
                        departing = departs[0]
                        departing_stax = depart_stax
                        first_thru = False

                data = (arrive_stax,)
                sql = 'select short_name from station where station = ?'
                count, ds_stationsb = self.db_read(sql, data)
                for arrives in ds_stationsb:
                    arriving = arrives[0]

            print(self.x_field(row[0], self.routsize) + " " +
                   self.x_field(row[1], name_size) + " " +
                   self.x_field(' ' + row[3] + ' ', 3) + " " +
                   self.x_field(status_desc, 6) + " " +
                   self.x_field(departing_stax + ' ' + departing, self.staxsize + 9) + " " +
                   self.x_field(arrive_stax + ' ' + arriving, self.staxsize + 9))

            line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break
        print(' ** END OF DATA:' + str(route_count) + ' RECORDS DISPLAYED **')         
        return



    def prrout(self, message, Params):
        """prints all routes to a report.  the routes are always displayed in name order.
        """
        if self.show_access(message, 'PRROUT', 'R') != 0:
            return        
            
        # build the column titles-------------------------------------------------------------------
        name_size = 80 - self.routsize - 2 * self.staxsize - 14
        if name_size > 30:
            name_size = 30
        titles = self.x_field('ROUTE=====', self.routsize) + ' ' +\
                 self.x_field('NAME=========================', name_size) + ' ' +\
                 self.x_field('DIR', 3) + ' ' +\
                 self.x_field('STATUS', 6) + ' ' +\
                 self.x_field('DEPART===============', 9 + self.staxsize) + ' ' +\
                 self.x_field('ARRIVE===============', 9 + self.staxsize)
        
        # get the extract data----------------------------------------------------------------------
        sql = 'select route, name, status, default_direction from route order by name'
        route_count, ds_routes = self.db_read(sql, '')
        if route_count < 0:
            return

        self.temp = {}
        for row in ds_routes:
            route       = row[0]
            name        = row[1]
            status      = row[2]
            default_dir = row[3]
            if status == 'I':
                status_desc = 'INCMPL'
            elif status == 'D':
                status_desc = 'DRAFT '
            else:
                status_desc = 'PUBLSH'
            sql = 'select depart_station, arrive_station from section where route = ? ' +\
                  'order by section'
            data = (route,)
            count, ds_sections = self.db_read(sql, data)
            if count < 0:
                return
            first_thru = True
            arriving = ''
            departing = ''
            departing_stax = ''
            for sect in ds_sections:
                depart_stax = sect[0]
                arrive_stax = sect[1]

                if first_thru:
                    data = (depart_stax,)
                    sql = 'select short_name from station where station = ?'
                    count, ds_stationsa = self.db_read(sql, data)
                    for departs in ds_stationsa:
                        departing = departs[0]
                        departing_stax = depart_stax
                        first_thru = False

                data = (arrive_stax,)
                sql = 'select short_name from station where station = ?'
                count, ds_stationsb = self.db_read(sql, data)
                for arrives in ds_stationsb:
                    arriving = arrives[0]

            print_line =  self.x_field(row[0], self.routsize) + ' ' +\
                   self.x_field(name, name_size) + ' ' +\
                   self.x_field(' ' + default_dir + ' ', 3) + ' ' +\
                   self.x_field(status_desc, 6) + ' ' +\
                   self.x_field(departing_stax + ' ' + departing, self.staxsize + 9) + ' ' +\
                   self.x_field(arrive_stax + ' ' + arriving, self.staxsize + 9)
            self.temp[route] = print_line

        #report the extracted data------------------------------------------------------------------
        self.print_report (titles = titles,
                           report_id = 'PRROUT',
                           report_name = 'SUMMARY LIST OF ROUTES',
                           Params = Params)
        return
