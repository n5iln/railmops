'''
Station Class
A working section of railroad that functions together and within which
operations can take place without reference to higher authority
or other stations
Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    15/08/2010 Ver 1 Removed unused variables
'''

import MOPS_Element


class cStations(MOPS_Element.cElement):
    """details about stations.  stations are linked to areas and are of a station type.  stations can
    also be an alias: if a station has an alias then (from a modelling point of view) it is at the
    same physical location on the layout.  stations have places (where actions happen).  stations
    are also locations where cars and locos may be placed.
    """
    extract_code = 'select * from station'
    extract_header = 'id|stax|shortname|long name|area|type|alias\n'

        
    def adstax(self, message, Params):
        """Add a new Station code, along with a short (8-character) name and a long name.
        Link to an Area and to a Station Type.  Optionally allow it to be an alias
        to another station by linking to that other station.  cars and locos belong to stations
        by having home stations, and also are at stations.
        """
        if self.show_access(message,
                            'ADSTAX station;short name;long name;^area^;^station type^;(^alias^)',
                            'S') != 0:
            return
        errors = 0

        #station code-------------------------------------------------------------------------------
        station, rc = self.extract_field(message, 0, 'STATION CODE')
        if rc > 0:
            return
        
        if len(station) > self.staxsize:
            print('* STATION CODE ENTERED IS GREATER THAN THE ALLOWED SIZE')
            return
        
        if len(station) ==0:
            print('* NO STATION CODE ENTERED: A BLANK CODE IS NOT ALLOWED')
            return

        data = (station,)
        sql = 'select id from station where station = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* STATION CODE ALREADY EXISTS')
            return

        #short name---------------------------------------------------------------------------------
        short_name, rc = self.extract_field(message, 1, 'SHORT NAME')
        if rc > 0:
            return

        #long name----------------------------------------------------------------------------------
        long_name, rc = self.extract_field(message, 2, 'LONG NAME')
        if rc > 0:
            return

        #stax area----------------------------------------------------------------------------------
        area, rc = self.extract_field(message, 3, 'AREA CODE')
        if rc > 0:
            return

        data = (area, )
        sql = 'select name from area where area = ?'
        count, ds_areas = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* AREA CODE DOES NOT EXIST (' + area + ')')
        else:
            for row in ds_areas:
                area_name = row[0]
        
        #stax type----------------------------------------------------------------------------------
        station_type, rc = self.extract_field(message, 4, 'STATION TYPE CODE')
        if rc > 0:
            return

        data = (station_type, )
        sql = 'select desc from stationtype where stationtype = ?'
        count, ds_station_types = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* STATION TYPE CODE DOES NOT EXIST (' + station_type + ')')
        else:
            for row in ds_station_types:
                station_type_desc = row[0]
                
        #stax alias---------------------------------------------------------------------------------
        alias, rc = self.extract_field(message, 5, '')
        if rc > 1:
            return

        #if the alias is not a null value then validate
        if rc == 0:
            data = (alias, )
            sql = 'select id, long_name from station where station = ?'
            count, ds_alias = self.db_read(sql, data)
            if count < 0:
                return

            if count == 0:
                errors = errors + 1
                print('* STATION CODE FOR ALIAS DOES NOT EXIST (' + alias + ')')
            else:
                for row in ds_alias:
                    alias_name = row[1]

        #carry out the update-----------------------------------------------------------------------
        if errors > 0:
            return

        data = (station, short_name, long_name, area, station_type, alias)
        sql = 'insert into station values (null, ?, ?, ?, ?, ?, ?)'
        if self.db_update(sql, data) != 0:
            return

        #extract update to station
        self.Z043_trimop_stations(Params, station)

        #report the change to the screen
        print('NEW STATION ADDED SUCCESSFULLY')
        print(station + ' ' + short_name + long_name)
        print('AREA: ' + area + area_name + ' TYPE: ' + station_type + station_type_desc)
        if alias != '':
            print('ALIAS OF: ' + alias, alias_name)
        return errors



    def chstax(self, message, Params):
        """change a station's details, including a short (8-character) name and a long name.  link to
        an area and to a station type.  optionally allow it to be an alias to another station by
        linking to that other station. to remove a previously-linked alias, use the alias 'REMOVE'
        """
        if self.show_access(message,
                            'CHSTAX station;(short name);(long name);(^area^);(^station type^);(^alias^)',
                            'S') != 0:
            return

        errors = 0
        
        #station code-------------------------------------------------------------------------------
        station, rc = self.extract_field(message, 0, 'STATION CODE')
        if rc > 0:
            return
        
        #read the database and populate the fields
        data = (station,)
        sql = 'select short_name, long_name, area, stationtype, alias from station where station = ?'
        count, ds_stations = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* STATION CODE DOES NOT EXIST')
            return

        for row in ds_stations:
            short_name   = row[0]
            long_name    = row[1]
            area         = row[2]
            station_type = row[3]
            alias        = row[4]

        #short name---------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            short_name = value

        #long name----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            long_name = value

        #stax area----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 3, '')
        if rc == 0:
            area = value

        data = (area, )
        sql = 'select name from area where area = ?'
        count, ds_areas = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* AREA CODE DOES NOT EXIST (' + area + ')')
        else:
            for row in ds_areas:
                area_name = row[0]
        
        #stax type----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 4, '')
        if rc == 0:
            station_type = value
        
        data = (station_type, )
        sql = 'select desc from stationtype where stationtype = ?'
        count, ds_station_types = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* STATION TYPE CODE DOES NOT EXIST (' + station_type + ')')
        else:
            for row in ds_station_types:
                station_type_desc = row[0]
 
        #stax alias---------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 5, '')
        if rc == 0:
            alias = value

        #check if the alias is being reset to a null value
        if alias == 'REMOVE':
            alias = '          '
            alias = alias.ljust(self.staxsize)[:self.staxsize]

        #if the alias is not a null value then validate
        found_alias = False
        if alias.strip() == '':
            alias_name = ''
        else:
            found_alias = True
            data = (alias, )
            sql = 'select long_name from station where station = ?'
            count, ds_alias = self.db_read(sql, data)
            if count < 0:
                return

            if count == 0:
                errors = errors + 1
                print('* STATION CODE FOR ALIAS DOES NOT EXIST (' + alias + ')')
            else:
                for row in ds_alias:
                    alias_name = row[0]
                    
        #carry out the update-----------------------------------------------------------------------
        if errors != 0:
            return
        
        data = (short_name, long_name, area, station_type, alias, station)
        sql = 'update station set short_name = ?, long_name = ?, area = ?, ' +\
              'stationtype = ?, alias = ? where station = ?'
        if self.db_update(sql, data) != 0:
            return

        #extract update to station
        self.Z043_trimop_stations(Params, station)

        #report the change to the screen------------------------------------------------------------
        print('STATION DETAILS CHANGED SUCCESSFULLY')
        print(station + ' ' + short_name + long_name)
        print('AREA: ' + area + area_name + ' TYPE: ' + station_type + station_type_desc)
        if found_alias:
            print('ALIAS OF: ' + alias + alias_name)
        return 



    def dxstax(self, message):
        """removes a stax from the dictionary list.  it cannot be linked to a place, loco
        (3 links), an alias (station), cars (4 instances), or route sections (2 instances).
        if any instructions exist then these are also deleted.
        """
        if self.show_access(message, 'DXSTAX station', 'S') != 0:
            return

        #station code-------------------------------------------------------------------------------
        stax, rc = self.extract_field(message, 0, 'STATION CODE')
        if rc > 0:
            return
        data = (stax,)

        #validate the change------------------------------------------------------------------------
        sql = 'select id from station where station = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* STATION CODE DOES NOT EXIST')
            return

        #make sure that there is not a place linked to the station----------------------------------
        sql = 'select id from place where station = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* PLACES ARE ATTACHED TO THIS STATION - CANNOT DELETE')
            return

        #make sure that there is not an alias linked to the station---------------------------------
        sql = 'select id from station where alias = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* ALIASES EXIST FOR THIS STATION - CANNOT DELETE')
            return

        #make sure that there is not a loco linked to the station as home station-------------------
        sql = 'select id from locomotive where home_station = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* THIS IS A HOME STATION FOR LOCOMOTIVES - CANNOT DELETE')
            return

        #make sure that there is not a loco linked to the station as current station
        sql = 'select id from locomotive where station = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* LOCOMOTIVES ARE AT THIS STATION - CANNOT DELETE')
            return

        #make sure that there is not a car linked to the station as home station---------------------
        sql = 'select id from car where home_station = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* CARS HAVE THIS AS A HOME STATION - CANNOT DELETE')
            return

        #make sure that there is not a car linked to the station as  station
        sql = 'select id from car where station = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* CARS ARE AT THIS STATION - CANNOT DELETE')
            return

        #make sure that there is not a route section linked to the station---------------------------
        sql = 'select id from section where depart_station = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* ROUTES HAVE BEEN CREATED WITH THIS AS A DEPARTURE STATION - CANNOT DELETE')
            return

        #make sure that there is not a route section linked to the station
        sql = 'select id from section where arrive_station = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* ROUTES HAVE BEEN CREATED WITH THIS AS AN ARRIVAL STATION - CANNOT DELETE')
            return

        #process the change - delete any instructions first------------------------------------------
        if self.db_update('delete from instructions where station = ?', data) != 0:
            return
        if self.db_update('delete from station where station = ?', data) == 0:
            print('STATION ' + stax + ' SUCCESSFULLY DELETED')
        return



    def listax(self, message):
        """list station details.  allow filtering by area and sorting by station code,
        short name or by area/station
        """
        if self.show_access(message, 'LISTAX (sort[0/1/2/3]);(^area^)', 'R') != 0:
            return
        
        #work out the various parameters------------------------------------------------------------
        sort_order, rc = self.extract_field(message, 0, '')
        if rc > 1:
            sort_order = ''

        filter_area, rc = self.extract_field(message, 1, '')
        if rc > 1:
            filter_area = ''

        # build the column titles-------------------------------------------------------------------
        long_name_size = 80 - self.areasize - self.statsize - self.staxsize - self.staxsize - 13 
        if long_name_size > 30:
            long_name_size = 30
        titles = self.x_field('AREA======', self.areasize)  + ' ' +\
                 self.x_field('STATION===', self.staxsize)  + ' ' +\
                 self.x_field('SHORT NAME', 8) + ' ' +\
                 self.x_field('LONG NAME=====================', long_name_size) + ' ' +\
                 self.x_field('TYPE======', self.statsize) + ' ' +\
                 self.x_field('ALIAS=====', self.staxsize)

        # get the extract data----------------------------------------------------------------------
        if sort_order == '1':
            sql = 'select area.area, station.station, station.short_name, '    +\
                  'station.long_name, station.stationtype, station.alias ' +\
                  'from area, station where area.area = station.area '     +\
                  'order by station.station'
        elif sort_order == '2':
            sql = 'select area.area, station.station, station.short_name, '    +\
                  'station.long_name, station.stationtype, station.alias ' +\
                  'from area, station where area.area = station.area '     +\
                  'order by station.short_name'
        else:
            sql = 'select area.area, station.station, station.short_name, '    +\
                  'station.long_name, station.stationtype, station.alias ' +\
                  'from area, station where area.area = station.area '     +\
                  'order by area.area, station.station'

        count, ds_stations = self.db_read(sql, '')
        if count < 0:
            return

        #report the extracted data------------------------------------------------------------------
        line_count = 0
        counter = 0
        for row in ds_stations:
            area_code = row[0]
            if filter_area == '' or filter_area == area_code:
                if line_count == 0:
                    print(titles)
                print(self.x_field(row[0], self.areasize) + " " +
                       self.x_field(row[1], self.staxsize) + " " +
                       self.x_field(row[2], 8) + " " +
                       self.x_field(row[3], long_name_size) + " " +
                       self.x_field(row[4], self.statsize) + " " +
                       self.x_field(row[5], self.staxsize))
                line_count = line_count + 1
                counter = counter + 1
                if line_count > 20:
                    line_count = 0
                    reply = raw_input('+')
                    if reply == 'x':
                        break
        print(' ** END OF DATA: ' + str(counter) + ' RECORDS DISPLAYED **')         
        return



    def prstax(self, message, Params):
        """Report station details.  Allow filtering by area and sorting by station code,
        short anme or by area/station
        """
        if self.show_access(message, 'PRSTAX (sort[0/1/2/3]);(^area^)', 'R') != 0:
            return

        #work out the various parameters------------------------------------------------------------
        sort_order, rc = self.extract_field(message, 0, '')
        if rc > 1:
            sort_order = ''

        filter_area, rc = self.extract_field(message, 1, '')
        if rc > 1:
            filter_area = ''

        # build the column titles-------------------------------------------------------------------
        long_name_size = 80 - self.areasize - self.statsize - self.staxsize - self.staxsize - 13
        if long_name_size > 30:
            long_name_size = 30
        titles = self.x_field('AREA======', self.areasize)  + ' ' +\
                 self.x_field('STATION===', self.staxsize)  + ' ' +\
                 self.x_field('SHORT NAME', 8) + ' ' +\
                 self.x_field('LONG NAME=====================', long_name_size) + ' ' +\
                 self.x_field('TYPE======', self.statsize) + ' ' +\
                 self.x_field('ALIAS=====', self.staxsize)

        # get the extract data----------------------------------------------------------------------
        if sort_order == '1':
            sql = 'select area.area, station.station, station.short_name, '    +\
                  'station.long_name, station.stationtype, station.alias ' +\
                  'from area, station where area.area = station.area '     +\
                  'order by station.station'
            report_desc = 'LIST STATIONS BY STATION CODE'
        elif sort_order == '2':
            sql = 'select area.area, station.station, station.short_name, '    +\
                  'station.long_name, station.stationtype, station.alias ' +\
                  'from area, station where area.area = station.area '     +\
                  'order by station.short_name'
            report_desc = 'LIST STATIONS BY STATION SHORT NAME'
        else:
            sql = 'select area.area, station.station, station.short_name, '    +\
                  'station.long_name, station.stationtype, station.alias ' +\
                  'from area, station where area.area = station.area '     +\
                  'order by area.area, station.station'
            report_desc = 'LIST STATIONS BY AREA, STATION'

        count, ds_stations = self.db_read(sql, '')
        if count < 0:
            return

        #build the extracted data ------------------------------------------------------------------
        self.temp = {}

        for row in ds_stations:
            area_code = row[0]
            if filter_area == '' or filter_area == area_code:
                print_line =   self.x_field(row[0], self.areasize) + ' ' +\
                               self.x_field(row[1], self.staxsize) + ' ' +\
                               self.x_field(row[2], 8) + ' ' +\
                               self.x_field(row[3], long_name_size) + ' ' +\
                               self.x_field(row[4], self.statsize) + ' ' +\
                               self.x_field(row[5], self.staxsize)
            if sort_order == '1':
                self.temp[row[1]] = print_line
            elif sort_order == '2':
                self.temp[row[2]] = print_line
            else:
                self.temp[row[0] + row[1]] = print_line  

        #report the extracted data ---------------------------------------
        self.print_report (titles = titles,
                           report_id = 'PRSTAX',
                           report_name = report_desc,
                           Params = Params)
        return



    def Z043_trimop_stations(self, Params, station):
        """write out a station record update for TriMOPS.
        """
        #see if we want to process the messages
        process_trimops = Params.get_param_value('TRIMOPS', 'NO')
        if process_trimops != 'YES':
            return

        #append the updated details to the history file
        filename = self.directory + 'exMOPStrains.txt'
        with open(filename, "a") as f:

            #current list of stations
            data = (station,)
            sql = 'select station, short_name, long_name, area, stationtype, alias from station ' +\
                  'where station = ?'
            count, ds_station = self.db_read(sql, data)
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
                f.write('11' + Params.get_date() + Params.get_time() + record_data + '\n')
        return
