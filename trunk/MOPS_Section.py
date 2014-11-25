'''
Route Section Class
The sequence of stations that make up a route.  A Section consists of a section
of track, with a departing station and an arriving station

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    15/08/2010 Ver 1 Unused variables removed; handled database return errors
'''
import MOPS_Element

class cSections(MOPS_Element.cElement):
    """sections are the building blocks for routes.  a series of contiguous sections creates
    a route; the section reference indicates the order in which the sections are created
    """
    extract_code = 'select * from section'
    extract_header = 'id|route|section|depart_station|arrive_station\n'



    def adsect(self, message):
        """add a new section to an existing route.  needs a station from/to, and a section
        (sequence).  route must not be in published status: and if set to draft it is reset to
        incomplete
        """
        if self.show_access(message, 'ADSECT route;section;^from^;^to^', 'S') != 0:
            return

        errors = 0

        #route code---------------------------------------------------------------------------------
        route, rc = self.extract_field(message, 0, 'ROUTE CODE')
        if rc > 0:
            return

        data = (route, 'P')
        sql = 'select name from route where route = ? and status != ?'
        count, ds_routes = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            print('* ROUTE CODE DOES NOT EXIST OR ROUTE IN PUBLISHED STATUS')
            return
        else:
            for row in ds_routes:
                route_name = row[0]

        #sequence-----------------------------------------------------------------------------------
        section, rc = self.extract_field(message, 1, 'SECTION')
        if rc > 0:
            return

        data = (section, route)
        sql = 'select id from section where section = ? and route = ?'
        count, ds_routes = self.db_read(sql, data)
        if count < 0:
            return

        if count > 0:
            print('* SECTION ALREADY EXISTS FOR THIS ROUTE (' + section + ')')
            errors = errors + 1

        #depart-------------------------------------------------------------------------------------
        depart, rc = self.extract_field(message, 2, 'DEPARTURE STATION')
        if rc > 0:
            return

        data = (depart, )
        sql = 'select long_name from station where station = ?'
        count, ds_stations = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* DEPARTURE STATION CODE DOES NOT EXIST (' + depart + ')')
        else:
            for row in ds_stations:
                long_name_depart = row[0]

        #arrive-------------------------------------------------------------------------------------
        arrive, rc = self.extract_field(message, 3, 'ARRIVAL STATION')
        if rc > 0:
            return

        data = (arrive, )
        sql = 'select long_name from station where station = ?'
        count, ds_stations = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* ARRIVAL STATION CODE DOES NOT EXIST (' + arrive + ')')
        else:
            for row in ds_stations:
                long_name_arrive = row[0]

        #carry out the update-----------------------------------------------------------------------
        if errors != 0:
            return
        
        data = (route, section, depart, arrive)
        sql = 'insert into section values (null, ?, ?, ?, ?)'
        if self.db_update(sql, data) != 0:
            return

        #the route is reset to initial status as it needs revalidating
        data = ('I', route)
        sql = 'update route set status = ? where route = ?'
        if self.db_update(sql, data) != 0:
            return
        
        print('NEW ROUTE SECTION ADDED SUCCESSFULLY')
        print('ROUTE:' + route + route_name)
        print('FROM:' + depart + long_name_depart + 'TO:' + arrive + long_name_arrive)
        return 



    def dxsect (self, message):
        """deletes a section from a route.  the route cannot already be in publshed status
        """
        if self.show_access(message, 'DXSECT section id', 'S') != 0:
            return

        #section id---------------------------------------------------------------------------------
        section_id, rc = self.extract_field(message, 0, 'SECTION ID')
        if rc > 0:
            return

        #validate the change------------------------------------------------------------------------
        data = (section_id,)
        sql = 'select id, route from section where id = ?'
        count, ds_sections = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* SECTION ID DOES NOT EXIST')
            return
        else:
            for row in ds_sections:
                route = row[1]

        #make sure that the route is not in published status-----------------------------------------
        data = (route, 'P')
        sql = 'select id from route where route = ? and status = ?'
        count, data = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* ROUTE IS IN PUBLISHED STATUS - CANNOT DELETE')
            return

        #process the change-------------------------------------------------------------------------
        data = ('I', route)
        if self.db_update('update route set status = ? where route  = ?', data) != 0:
            return
        data = (section_id,)
        if self.db_update('delete from section where id = ?', data) == 0:
            print('SECTION' + section_id + 'SUCCESSFULLY DELETED: ROUTE' +
                   route + 'AT INCOMPLETE STATUS')
        return
    


    def lsrout(self, message):
        """display the route name and all the associated sections in sequence.
        """
        if self.show_access(message, 'LSROUT route', 'R') != 0:
            return

        #route code---------------------------------------------------------------------------------
        route, rc = self.extract_field(message, 0, 'ROUTE CODE')
        if rc > 1:
            return

        if rc == 1:
            print('* ROUTE CODE REQUIRED FOR ENQUIRY')
            return

        data = (route,)
        sql = 'select name, status, default_direction from route where route = ?'
        count, routes = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('NO ROUTE TO DISPLAY')
            return
        
        for row in routes:
            route_name  = row[0]
            route_stat  = row[1]
            route_dirn  = row[2]
            direction, status = self.build_descs(route_dirn, route_stat)

        print('ROUTE:' + route, route_name + 'DIRN:' + direction + 'STATUS:' + status)

        # build the column titles-------------------------------------------------------------------
        titles = self.x_field('ID===', 5)    + ' '       + \
                 self.x_field('SECTION=', 8) + ' ' +\
                 self.x_field('DEPARTING=========', self.staxsize + 9)   + ' '       + \
                 self.x_field('ARRIVING==========', self.staxsize + 9)        

        sql = 'select id, section, depart_station, arrive_station from section where route = ? ' +\
              'order by section'
        count, ds_sections = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            print('* NO SECTIONS FOUND FOR ROUTE')
            return
        
        #report the extracted data------------------------------------------------------------------
        line_count = 0
        for row in ds_sections:
            if line_count == 0:
                print(titles)
            depart = row[2]
            arrive = row[3]
            data = (depart,)
            sql = 'select short_name from station where station = ?'
            stax_count, ds_departs = self.db_read(sql, data)
            if stax_count < 0:
                return
            for stax_row in ds_departs:
                depart_short_name = stax_row[0]
                depart_name = depart + ' ' + depart_short_name

            data = (arrive,)
            sql = 'select short_name from station where station = ?'
            stax_count, ds_arrives = self.db_read(sql, data)
            if stax_count < 0:
                return

            for stax_row in ds_arrives:
                arrive_short_name = stax_row[0]
                arrive_name = arrive + ' ' + arrive_short_name
                print(self.x_field(row[0], 5, 'R') + " " +
                        self.x_field(row[1], 8, 'R') + " " +
                        self.x_field(depart_name, self.staxsize + 9) + " " +
                        self.x_field(arrive_name, self.staxsize + 9))
                line_count = line_count + 1
                if line_count > 20:
                    line_count = 0
                    reply = raw_input('+')
                    if reply == 'x':
                        break
        print(' ** END OF DATA:' + str(count) + ' RECORDS DISPLAYED **')         
        return



    def ldrout(self, message):
        """display the route name, sequence and instructions
        """
        if self.show_access(message, 'LDROUT route', 'R') != 0:
            return

        #route code---------------------------------------------------------------------------------
        route, rc = self.extract_field(message, 0, 'ROUTE CODE')
        if rc > 0:
            return

        #get the route detail to display------------------------------------------------------------
        data = (route,)
        sql = 'select name, default_direction, status from route where route = ?'
        count, ds_routes = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('NO ROUTE TO DISPLAY')
            return
        else:
            for row in ds_routes:
                route_name = row[0]
                route_dirn = row[1]
                route_stat = row[2]

        direction, status = self.build_descs(route_dirn, route_stat)
        print('ROUTE:' + route + route_name + ' (ROUTE STATUS:' + status + ')')
        print('       DIRECTION:' + direction)

        sql = 'select instruction from instructions where route = ?'
        count, ds_instructions = self.db_read(sql, data)
        for row in ds_instructions:
            print(' - ' + row[0])
        print(' ' )
                    
        # build the column titles-------------------------------------------------------------------
        titles = self.x_field('DEPARTING=============================', 40) +\
                 self.x_field('STATION INSTRUCTIONS =================', 39)        

        sql = 'select id, section, depart_station, arrive_station from section ' +\
              'where route = ? order by section'
        count, ds_routes = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            print('NO SECTIONS FOUND FOR ROUTE')
            return
        
        #report the extracted data------------------------------------------------------------------
        line_count = 0
        for row in ds_routes:
            if line_count == 0:
                print(titles)
            arrival = row[3]
            depart_station = row[2]

            data = (depart_station,)
            sql = 'select long_name from station where station = ?'
            stax_count, ds_departs = self.db_read(sql, data)
            if stax_count < 0:
                return
            for stax_row in ds_departs:
                depart_name = stax_row[0]
                depart_name = depart_station + ' ' + depart_name
                depart_name = self.x_field(depart_name, 40)

            #get any station instructions - just print the first one
            sql = 'select instruction from instructions where station = ? limit 1'
            count, ds_instructions = self.db_read(sql, data)
            for row in ds_instructions:
                instruction = row[0]
                depart_name = depart_name + instruction

            print(self.x_field(depart_name, self.staxsize + 79))

            #get any station instructions - now print the rest
            sql = 'select instruction from instructions where station = ?'
            count, ds_instructions = self.db_read(sql, data)
            line = 0 
            for row in ds_instructions:
                instruction = row[0]
                line = line + 1
                if line != 1:
                    print('                                       ' + instruction)

            line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break

        #get the long name for the arrive station (for the last entry)
        data = (arrival,)
        sql = 'select long_name from station where station = ?'
        stax_count, ds_arrives = self.db_read(sql, data)
        for stax_row in ds_arrives:
            arrive_name = arrival + ' ' + stax_row[0]
            arrive_name = self.x_field(arrive_name, 40)
                
        #get any station instructions - just print the first one------------------------------------
        sql = 'select instruction from instructions where station = ? limit 1'
        count, ds_instructions = self.db_read(sql, data)
        for row in ds_instructions:
            arrive_name = arrive_name + row[0]

        print(self.x_field(arrive_name, 80))

        #get any station instructions - now print the rest------------------------------------------
        sql = 'select instruction from instructions where station = ?'
        count, ds_instructions = self.db_read(sql, data)
        line = 0 
        for row in ds_instructions:
            line = line + 1
            instruction = row[0]
            if line != 1:
                print('                                       ' + instruction)
                    
        print(' ** END OF DATA:' + str(count) + ' RECORDS DISPLAYED **')         
        return



    def pdrout(self, message, Params):
        """display the route name, sequence and instructions
        """
        if self.show_access(message, 'PDROUT route', 'R') != 0:
            return

        self.temp = {}
        i_temp = 0

        #route code---------------------------------------------------------------------------------
        route, rc = self.extract_field(message, 0, '')
        if rc > 1:
            return
        if rc == 1:
            print('* ROUTE CODE REQUIRED FOR REPORT')

        #get the route detail to display------------------------------------------------------------
        data = (route,)
        sql = 'select name, default_direction, status from route where route = ?'
        count, ds_routes = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('NO ROUTE TO DISPLAY')
            return
        else:
            for row in ds_routes:
                route_name = row[0]
                route_dirn = row[1]
                route_stat = row[2]

        direction, status = self.build_descs(route_dirn, route_stat)

        print_line = 'ROUTE: ' + route + ' ' + route_name + ' (ROUTE STATUS:' + status + ')'
        self.temp[i_temp] = print_line
        i_temp = i_temp + 1

        print_line = '       DIRECTION:' + direction
        self.temp[i_temp] = print_line
        i_temp = i_temp + 1

        sql = 'select instruction from instructions where route = ?'
        count, ds_instructions = self.db_read(sql, data)
        for row in ds_instructions:
            instruction = row[0]
            print_line = ' - ' +  instruction
            self.temp[i_temp] = print_line
            i_temp = i_temp + 1
            print_line = ' '
            self.temp[i_temp] = print_line
            i_temp = i_temp + 1
            self.temp[i_temp] = print_line
            i_temp = i_temp + 1
            self.temp[i_temp] = print_line
            i_temp = i_temp + 1
                    
        # build the column titles--------------------------------------------------------------------
        titles = self.x_field('DEPARTING=============================', self.staxsize + 29) + ' ' + \
                 self.x_field('INSTRUCTIONS =========================', 40)        

        sql = 'select id, section, depart_station, arrive_station from section ' +\
              'where route = ? order by section'
        count, ds_routes = self.db_read(sql, data)
        if count < 0:
            return
        
        #report the extracted data-------------------------------------------------------------------
        for row in ds_routes:
            arrival = row[3]
            depart  = row[2]
            section = row[1]

            #get the long name for the departure station
            data = (depart,)
            sql = 'select long_name from station where station = ?'
            stax_count, ds_departs = self.db_read(sql, data)
            if stax_count < 0:
                return
            for stax_row in ds_departs:
                depart_name = stax_row[0]
                depart_name = str(section) + ' ' + depart_name
                depart_name = self.x_field(depart_name, self.staxsize + 30)

            #get any station instructions - just print the first one
            sql = 'select instruction from instructions where station = ? limit 1'
            count, ds_instructions = self.db_read(sql, data)
            for row in ds_instructions:
                instruction = row[0]
                depart_name = depart_name + instruction

            print_line = self.x_field(depart_name, self.staxsize + 79)
            self.temp[i_temp] = print_line
            i_temp = i_temp + 1

            #get any station instructions - now print the rest
            sql = 'select instruction from instructions where station = ?'
            count, ds_instructions = self.db_read(sql, data)
            line = 0 
            for row in ds_instructions:
                instruction = row[0]
                line = line + 1
                if line != 1:
                    print_line = '                                  ' + instruction
                    self.temp[i_temp] = print_line
                    i_temp = i_temp + 1

        #get the long name for the arrive station (for the last entry)
        sql = 'select long_name from station where station = ?'
        data = (arrival,)
        stax_count, ds_arrives = self.db_read(sql, data)
        for stax_row in ds_arrives:
            arrive_name = stax_row[0]
            arrive_name = arrival + ' ' + arrive_name
            arrive_name = self.x_field(arrive_name, self.staxsize + 30)
                
        #get any station instructions - just print the first one
        sql = 'select instruction from instructions where station = ? limit 1'
        count, ds_instructions = self.db_read(sql, data)
        for row in ds_instructions:
            instruction = row[0]
            arrive_name = arrive_name + instruction

        print_line = self.x_field(arrive_name, self.staxsize + 79)
        self.temp[i_temp] = print_line
        i_temp = i_temp + 1

        #get any station instructions - now print the rest
        sql = 'select instruction from instructions where station = ?'
        count, ds_instructions = self.db_read(sql, data)
        line = 0 
        for row in ds_instructions:
            instruction = row[0]
            line = line + 1
            if line != 1:
                print_line = '                                  ' + instruction
                self.temp[i_temp] = print_line
                i_temp = i_temp + 1

        #report the extracted data-------------------------------------------------------------------
        self.print_report (titles = titles,
                           report_id = 'PDROUT',
                           report_name = 'ROUTE LISTING',
                           Params = Params)
        return



    def build_descs(self, route_dirn, route_stat):
        """returns descriptions for route direction and status
        """
        if route_dirn == 'N':
            direction = 'NORTH'
        elif route_dirn == 'S':
            direction = 'SOUTH'
        elif route_dirn == 'E':
            direction = 'EAST'
        elif route_dirn == 'W':
            direction = 'WEST'
        elif route_dirn == 'U':
            direction = 'UP'
        elif route_dirn == 'D':
            direction = 'DOWN'
        else:
            direction = 'NOT KNOWN'
        if route_stat == 'I':
            status = 'INCOMPLETE'
        elif route_stat == 'D':
            status = 'DRAFT'
        elif route_stat == 'P':
            status = 'PUBLISHED'
        else:
            status = 'NOT KNOWN'
        return direction, status
