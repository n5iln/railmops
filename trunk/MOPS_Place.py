'''
Zone-Track-Spot Class
Places are particular locations on the railroad where events take place.
Places can also be used to structure locations in a Zone-Track-Spot format
by structuring the Place Code

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    31/07/2010 Ver 1.  Removed unused variables
'''
import MOPS_Element


class cPlaces(MOPS_Element.cElement):
    """details about place locations.  places are locations of activity on mops, and determine where
    warehouses are located and where locomotive maintenance, fuelling etc can take place.  places are
    linked to stations, and can be occupied by cars and locos, and warehouses are also linked to them.
    """
    extract_code = 'select * from place'
    extract_header = 'id|name|station|code|track length|industry|place type|loading|unloading|' +\
                     'car_being_processed\n'




    def adplax(self, message):
        """add a place; the place code is unique within a station only (but a unique id will be
        generated.  Indicate the location by linking to a Station.  Optionally include track length,
        whether locos can refuel (diesel, steam, other), whether locos or cars can be repaired
        and whether cars can be cleaned.  Industries are added with a separate verb.
        """
        if self.show_access(message, 'ADPLAX ^station^;place;name;place type[C/D/L/M/O/S/X];' +\
                            '(track_length)', 'S') != 0:
            return
        errors = 0

        #station------------------------------------------------------------------------------------
        stax, rc = self.extract_field(message, 0, 'STATION CODE')
        if rc > 0:
            return

        #check the station exists on the database
        data = (stax,)
        sql = 'select id, long_name from station where station = ?'
        count, ds_stations = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* STATION CODE DOES NOT EXIST')
            return
        else:
            for row in ds_stations:
                station_name = row[1]

        #plax code----------------------------------------------------------------------------------
        plax, rc = self.extract_field(message, 1, 'PLACE CODE')
        if rc > 0:
            return

        if len(plax) > self.plaxsize:
            print('* PLACE CODE ENTERED IS GREATER THAN THE ALLOWED SIZE')
            return
        
        if len(plax) == 0:
            print('* NO PLACE CODE ENTERED: A BLANK CODE IS NOT ALLOWED')
            return

        #get plax id for stax/plac combination
        place_id = self.get_id_for_station_and_place(stax, plax)
        if place_id != 0:
            print('* STATION/PLACE COMBINATION ALREADY EXISTS')
            return

        #name---------------------------------------------------------------------------------------
        place_name, rc = self.extract_field(message, 2, 'PLACE NAME')
        if rc > 1:
            return

        #place_type---------------------------------------------------------------------------------
        place_type, rc = self.extract_field(message, 3, 'PLACE TYPE')
        if rc > 0:
            return

        if not(place_type == 'D' or place_type == 'S' or place_type == 'O' or place_type == 'M' or place_type == 'L' or place_type == 'C' or place_type == 'X'):
            errors = errors + 1
            print('* PLACE TYPE MUST BE OF A VALUE C, D, L, M, O, S, OR X)')

        desc = self.get_usage_name(place_type, '')

        #track_length-------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 4, '')
        if rc == 0:
            track_length = value
        else:
            track_length = '0'

        try:
            if int(track_length) > 99999 or int(track_length) < 0:
                errors = errors + 1
                print('* TRACK LENGTH MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* TRACK LENGTH MUST BE A WHOLE NUMBER')

        #carry out the update-----------------------------------------------------------------------
        if errors != 0:
            return

        data = (place_name, stax, plax, track_length, '', place_type, '', '', 0)
        sql = 'insert into place values (null, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        if self.db_update(sql, data) != 0:
            return

        place_id = self.get_id_for_station_and_place(stax, plax)

        #report the change to the screen
        print('NEW PLACE ADDED SUCCESSFULLY')
        print('STATION: ' + stax, station_name, ' PLACE: ' + plax , place_name,
               '(GEN. ID IS ', str(place_id) + ')')
        print('TRACK LENGTH: ' + track_length, desc)
        return 



    def adindy(self, message):
        """add a place as an industry; the place code is unique within a station only (but a unique
        id will be generated.  Indicate the location by linking to a Station.  Indicate the type of
        loading and unloading that can take place here.
        """
        if self.show_access(message,
               'ADINDY station;place;place name;length;industry code;(^load^);(^(un)load^)',
               'S') != 0:
            return
        errors = 0

        #station------------------------------------------------------------------------------------
        stax, rc = self.extract_field(message, 0, 'STATION CODE')
        if rc > 0:
            return

        #check the station exists on the database
        data = (stax,)
        sql = 'select id, long_name from station where station = ?'
        count, ds_stations = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* STATION CODE (FOR INDUSTRY) DOES NOT EXIST')
            return
        else:
            for row in ds_stations:
                station_name = row[1]

        #plax code----------------------------------------------------------------------------------
        plax, rc = self.extract_field(message, 1, 'PLACE CODE')
        if rc > 0:
            return

        if len(plax) > self.plaxsize:
            print('* PLACE CODE ENTERED IS GREATER THAN THE ALLOWED SIZE')
            return
        
        if len(plax) == 0:
            print('* NO PLACE CODE ENTERED: A BLANK CODE IS NOT ALLOWED')
            return

        #get plax id for stax/plac combination
        place_id = self.get_id_for_station_and_place(stax, plax)
        if place_id != 0:
            print('* STATION/PLACE COMBINATION ALREADY EXISTS')
            return

        #name---------------------------------------------------------------------------------------
        place_name, rc = self.extract_field(message, 2, 'PLACE NAME ')
        if rc > 1:
            return

        #track_length-------------------------------------------------------------------------------
        track_length, rc = self.extract_field(message, 3, 'TRACK LENGTH ')
        if rc > 1:
            return
        if rc == 1:
            track_length = '0'

        try:
            if int(track_length) > 99999 or int(track_length) < 0:
                errors = errors + 1
                print('* TRACK LENGTH MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* TRACK LENGTH MUST BE A WHOLE NUMBER')

        #name---------------------------------------------------------------------------------------
        industry, rc = self.extract_field(message, 4, '')
        if rc > 0:
            return

        #check that the length of the industry is no more than 10 characters
        if len(industry) > 10:
            errors = errors + 1
            print('* LENGTH OF INDUSTRY NAME MUST BE 10 CHARACTERS OR FEWER')
            
        #check that the name has not already been used as it needs to be unique
        data = (industry,)
        sql = 'select id from place where industry = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return

        if count > 0:
            errors = errors + 1
            print('* INDUSTRY NAME ALREADY IN USE; MUST BE UNIQUE AT EACH PLACE')

        #loading------------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 5, '')
        if rc == 0:
            load = value
        else:
            load = ''

        if load.strip() == '':
            loading_desc = ''
        else:
            flag_value = 'Y'
            data = (load, flag_value)
            sql = 'select desc from loading where loading = ? and can_load = ?'
            count, ds_loading = self.db_read(sql, data)
            if count < 0:
                return

            if count == 0:
                errors = errors + 1
                print('* LOADING CODE DOES NOT EXIST OR NOT SET FOR LOADING (' + load + ')')
            else:
                for row in ds_loading:
                    loading_desc = row[0]

        #unloading----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 6, '')
        if rc == 0:
            unload = value
        else:
            unload = ''

        if unload.strip() == '':
            unloading_desc = ''
        else:
            flag_value = 'Y'
            data = (unload, flag_value)
            sql = 'select desc from loading where loading = ? and can_unload = ?'
            count, ds_unloading = self.db_read(sql, data)
            if count < 0:
                return
                
            if count == 0:
                errors = errors + 1
                print('* LOADING CODE DOES NOT EXIST (' + unload + ')')
            else:
                for row in ds_unloading:
                    unloading_desc = row[0]

        #carry out the update-----------------------------------------------------------------------
        if errors != 0:
            return

        data = (place_name, stax, plax, track_length, industry, 'I', load, unload, 0)
        sql = 'insert into place values (null, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        if self.db_update(sql, data) != 0:
            return

        place_id = self.get_id_for_station_and_place(stax, plax)

        #report the change to the screen
        print('NEW INDUSTRY ADDED SUCCESSFULLY: ', industry)
        print('STATION: ' + stax, station_name, ' PLACE: ' + plax, place_name,
               '(GEN. ID IS ', str(place_id) + ')')
        print('TRACK LENGTH: ' + track_length)
        if load != '':
            print('  LOAD: ' + load, '(' + loading_desc.strip() + ')')
        if unload != '':
            print('UNLOAD: '+ unload, '(' + unloading_desc.strip() + ')')
        return 



    def chplax(self, message):
        """change details of a place; changes can be to the name and track length only: if the
        place type needs changing then the place needs to be deleted and re-added.  Industries are
        maintained on a different verb
        """                                                                     
        if self.show_access(message, 'CHPLAX ^station^;place;(name);(track_length)',
                            'S') != 0:
            return

        #station------------------------------------------------------------------------------------
        stax, rc = self.extract_field(message, 0, 'STATION CODE')
        if rc > 0:
            return

        data = (stax, )
        sql = 'select long_name from station where station = ?'
        count, ds_stations = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            print('* STATION CODE DOES NOT EXIST (' + stax + ')')
            return
        else:
            for row in ds_stations:
                station_name = row[0]

        #plax code----------------------------------------------------------------------------------
        plax, rc = self.extract_field(message, 1, 'PLACE CODE')
        if rc > 0:
            return

        #read the database and populate the fields
        data = (stax, plax, 'I')
        sql = 'select id, name, track_length from place where station = ? and code = ? ' +\
              'and place_type != ?'
        count, ds_places = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            print('* STATION/PLACE DOES NOT EXIST, OR IS AN INDUSTRY', stax, plax)
            return

        for row in ds_places:
            place_name     = row[1]
            track_length   = row[2]

        #name---------------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            place_name = value

        #track_length------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 3, '')
        if rc == 0:
            track_length = value

        try:
            if int(track_length) > 99999 or int(track_length) < 0:
                print('* TRACK LENGTH MUST BE IN THE RANGE 0 to 99999')
                return
        except:
            print('* TRACK LENGTH MUST BE A WHOLE NUMBER')
            return

        #update the database with the new name-----------------------------------------------------
        place_id = self.get_id_for_station_and_place(stax, plax)
        data = (place_name, track_length, place_id)
        sql = 'update place set name = ?, track_length = ? where id = ?'
        if self.db_update(sql, data) != 0:
            return

        #report the change to the screen
        print('PLACE NAME CHANGED SUCCESSFULLY')
        print('STATION: ', stax, station_name, ' PLACE: ', plax , place_name, '(GENERATED ID IS ', str(place_id) + ')')
        print('TRACK LENGTH:', track_length)
        return
   


    def chindy(self, message):
        """change details of a place; changes can include name, industry code, track length,
        and loading and unloading codes for the location.
        """                                                                     
        if self.show_access(message,
                            'CHPLAX station;place;(place name);(track length);' +\
                            '(^load^);(^(un)load)', 'S') != 0:
            return
        errors = 0

        #station------------------------------------------------------------------------------------
        stax, rc = self.extract_field(message, 0, 'STATION CODE')
        if rc > 0:
            return

        data = (stax, )
        sql = 'select long_name from station where station = ?'
        count, ds_stations = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* STATION CODE DOES NOT EXIST (' + stax + ')')
        else:
            for row in ds_stations:
                station_name = row[0]

        #plax code----------------------------------------------------------------------------------
        plax, rc = self.extract_field(message, 1, 'PLACE CODE')
        if rc > 0:
            return

        #read the database and populate the fields
        data = (stax, plax, 'I')
        sql = 'select id, name, track_length, industry, loading, unloading from place ' +\
              'where station = ? and code = ? and place_type = ?'
        count, ds_places = self.db_read(sql, data)
        if count < 0:
            return

        if count == 0:
            print('* STATION/PLACE DOES NOT EXIST, OR IS NOT AN INDUSTRY', stax, plax)
            return

        for row in ds_places:
            place_name     = row[1]
            industry       = row[3]
            load           = row[4]
            unload         = row[5]

        #name--------------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            industry = value

        #track_length------------------------------------------------------------------------------
        track_length, rc = self.extract_field(message, 3, '')
        if rc > 1:
            return
        if rc == 1:
            track_length = '0'

        try:
            if int(track_length) > 99999 or int(track_length) < 0:
                errors = errors + 1
                print('* TRACK LENGTH MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* TRACK LENGTH MUST BE A WHOLE NUMBER')

        #loading-----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 5, '')
        if rc == 0:
            load = value

        flag_value = 'N'
        if load.strip() == '':
            loading_desc = ''
        else:
            flag_value = 'Y'
            data = (load, flag_value)
            sql = 'select desc from loading where loading = ? and can_load = ?'
            count, ds_loading = self.db_read(sql, data)
            if count < 0:
                return

            if count == 0:
                errors = errors + 1
                print('* LOADING CODE DOES NOT EXIST OR NOT SET FOR LOADING (', load, ')')
            else:
                for row in ds_loading:
                    loading_desc = row[0]

        #unloading---------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 6, '')
        if rc == 0:
            unload = value

        flag_value = 'N'
        if unload.strip() == '':
            unloading_desc = ''
        else:
            data = (unload, flag_value)
            sql = 'select desc from loading where loading = ? and can_unload = ?'
            count, ds_unloading = self.db_read(sql, data)
            if count < 0:
                return
                
            if count == 0:
                errors = errors + 1
                print('* LOADING CODE DOES NOT EXIST (' + unload + ')')
            else:
                for row in ds_unloading:
                    unloading_desc = row[0]

        #carry out the update----------------------------------------------------------------------
        if errors != 0:
            return

        place_id = self.get_id_for_station_and_place(stax, plax)
        data = (place_name, track_length, load, unload, place_id)
        sql = 'update place set name = ?, track_length = ?, loading = ?,  unloading = ? where id = ?'
        if self.db_update(sql, data) != 0:
            return

        #report the change to the screen
        print('PLACE DETAILS CHANGED SUCCESSFULLY:', industry)
        print('STATION: ', stax, station_name, ' PLACE: ', plax ,
               place_name, '(GENERATED ID IS ', str(place_id) + ')')
        print('TRACK LENGTH: ', track_length, 'LOAD: ', load,
               '(' + loading_desc.strip() + ')  UNLOAD: ',
               unload, '(' + unloading_desc.strip() + ')')
        return



    def dxplax(self, message):
        """removes a place from the database (unless it is an industry).  check that there are no
        locos or cars at the place
        """
        if self.show_access(message, 'DXPLAX id', 'S') != 0:
            return

        #plax code----------------------------------------------------------------------------------
        plax_id, rc = self.extract_field(message, 0, 'PLACE ID')
        if rc > 0:
            return

        #validate the change - check there is a record to delete------------------------------------
        data = (plax_id, 'I')
        sql = 'select id from place where id = ? and place_type != ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* PLACE CODE DOES NOT EXIST OR IS AN INDUSTRY')
            return

        #check that no locomotive is at that place--------------------------------------------------
        data = (plax_id,)
        sql = 'select id from locomotive where place_id = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* LOCOMOTIVES ARE LOCATED AT THIS PLACE: DELETE CANCELLED')
            return
            
        #check that no car is at that place--------------------------------------------------
        data = (plax_id,)
        sql = 'select id from car where place_id = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* CARS ARE LOCATED AT THIS PLACE: DELETE CANCELLED')
            return
            
        #process the change-------------------------------------------------------------------------
        if self.db_update ('delete from place where id = ?', data) == 0:
            print('PLACE', plax_id, 'SUCCESSFULLY DELETED')
        return



    def dxindy(self, message):
        """removes a place from the database if it is an industry.  check there are no warehouses
        there, nor any cars.
        """
        if self.show_access(message, 'DXINDY place id', 'S') != 0:
            return

        #plax code----------------------------------------------------------------------------------
        plax_id, rc = self.extract_field(message, 0, 'PLACE ID')
        if rc > 0:
            return

        #validate the change - check there is a record to delete------------------------------------
        data = (plax_id, 'I')
        sql = 'select id, industry from place where id = ? and place_type = ?'
        count, ds_places = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* PLACE CODE DOES NOT EXIST OR IS NOT AN INDUSTRY')
            return
        for row in ds_places:
            industry = row[1]

        data = (industry,)
        sql = 'select id from warehouse where industry = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* WAREHOUSES ARE ATTACHED TO THIS INDUSTRY')
            return
        sql = 'select id from warehouse where destination = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* WAREHOUSES HAVE THIS INDUSTRY AS A DESTINATION')
            return
        

        #process the change-------------------------------------------------------------------------
        data = (plax_id,)
        if self.db_update ('delete from place where id = ?', data) == 0:
            print('PLACE', plax_id, 'SUCCESSFULLY DELETED')
        return



    def liplax(self, message):
        """list details of facilities at a place, and include its unique id as well as the
        station/place codes.  allow filtering by station and sorting by unqiue id, name or
        station/place.  also allow filtering by type.
        """
        if self.show_access(message, 'LIPLAX (sort[0/1/2]);(^station^)', 'R') != 0:
            return

        #report parameters--------------------------------------------------------------------------
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            filter_station = value
        else:
            filter_station = ''

        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            filter_type = value
        else:
            filter_type = ''

        # build the column titles-------------------------------------------------------------------
        name_size = 80 - self.staxsize - self.plaxsize - 22 - 2 * self.loadsize
        if name_size > 30:
            name_size = 30
        titles = self.x_field('===ID', 5)  + ' ' +\
                 self.x_field('STATION===', self.staxsize) + ' ' +\
                 self.x_field('PLACE=====', self.plaxsize) + ' ' +\
                 self.x_field('NAME============================', name_size) + ' ' +\
                 self.x_field('LNGTH', 5) + ' ' +\
                 self.x_field('INDUSTRY=========', 10) + ' ' +\
                 self.x_field('LOADING=====', self.loadsize) + ' ' +\
                 self.x_field('UNLOADING===', self.loadsize)
    
        # get the extract data----------------------------------------------------------------------
        if sort_order == '1':
            sql = 'select id, name, station, code, track_length, industry, place_type, loading, ' +\
                  'unloading from place order by id'
        elif sort_order == '2':
            sql = 'select id, name, station, code, track_length, industry, place_type, loading, ' +\
                  'unloading from place order by name'
        else:
            sql = 'select id, name, station, code, track_length, industry, place_type, loading, ' +\
                  'unloading from place order by station, code'

        count, ds_places = self.db_read(sql, '')
        if count < 0:
            return

        #report the extracted data------------------------------------------------------------------
        line_count = 0
        for row in ds_places:
            station_code = row[2]
            place_type   = row[6]
            if filter_station == '' or filter_station == station_code:
                if filter_type == '' or filter_type == place_type:
                    if line_count == 0:
                        print(titles)
                    usage = self.get_usage_name(row[6], row[5])

                    print(self.x_field(row[0], 5, 'R') + " " +
                           self.x_field(row[2], self.staxsize) + " " +
                           self.x_field(row[3], self.plaxsize) + " " +
                           self.x_field(row[1], name_size) + " " +
                           self.x_field(row[4], 5, 'R') + " " +
                           self.x_field(usage, 10) + " " +
                           self.x_field(row[7], self.loadsize) + " " +
                           self.x_field(row[8], self.loadsize))
                    line_count = line_count + 1
                    if line_count > 20:
                        line_count = 0
                        reply = raw_input('+')
                        if reply == 'x':
                            break
        print(' ** END OF DATA:' + str(count) + ' RECORDS DISPLAYED **')         
        return



    def prplax(self, message, Params):
        """report details of facilities at a place, and include its unique id as well as the
        station/place codes.  allow filtering by station and type, and sorting by unqiue id, name
        or station/place
        """
        if self.show_access(message, 'PRPLAX (sort[0/1/2]);(^station^)', 'R') != 0:
            return

        #report parameters--------------------------------------------------------------------------
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            filter_station = value
        else:
            filter_station = ''

        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            filter_type = value
        else:
            filter_type = ''

        # build the column titles-------------------------------------------------------------------
        name_size = 80 - self.staxsize - self.plaxsize - 22 - ( 2 * self.loadsize )
        if name_size > 30:
            name_size = 30
        titles = self.x_field('===ID', 5)  + ' ' +\
                 self.x_field('STATION===', self.staxsize) + ' ' +\
                 self.x_field('PLACE=====', self.plaxsize) + ' ' +\
                 self.x_field('NAME==========================', name_size) + ' ' +\
                 self.x_field('LNGTH', 5) + ' ' +\
                 self.x_field('USAGE=========', 10) + ' ' +\
                 self.x_field('LOADING=====', self.loadsize) + ' ' +\
                 self.x_field('UNLOADING===', self.loadsize)
    
        # get the extract data----------------------------------------------------------------------
        if sort_order == '1':
            sql = 'select id, name, station, code, track_length, industry, place_type, loading, ' +\
                  'unloading from place order by id'
            report_desc = 'LIST OF PLACES SORTED BY ID'
        elif sort_order == '2':
            sql = 'select id, name, station, code, track_length, industry, place_type, loading, ' +\
                  'unloading from place order by name'
            report_desc = 'LIST OF PLACES SORTED BY NAME'
        else:
            sql = 'select id, name, station, code, track_length, industry, place_type, loading, ' +\
                  'unloading from place order by station, code'
            report_desc = 'LIST OF PLACES SORTED BY STATION, CODE'

        count, ds_places = self.db_read(sql, '')
        if count < 0:
            return

        #build the extracted data-------------------------------------------------------------------
        self.temp = {}
                       
        for row in ds_places:
            station_code = row[2]
            place_type   = row[6]
            if filter_station == '' or filter_station == station_code:
                if filter_type == '' or filter_type == place_type:
                    usage = self.get_usage_name(row[6], row[5])

                    print_line =   self.x_field(row[0], 5, 'R') + ' ' +\
                                   self.x_field(row[2], self.staxsize) + ' ' +\
                                   self.x_field(row[3], self.plaxsize) + ' ' +\
                                   self.x_field(row[1], name_size) + ' ' +\
                                   self.x_field(row[4], 5, 'R') + ' ' +\
                                   self.x_field(usage, 10) + ' ' +\
                                   self.x_field(row[7], self.loadsize) + ' ' +\
                                   self.x_field(row[8], self.loadsize)
                    if sort_order == '1':
                        self.temp[row[0]] = print_line
                    elif sort_order == '2':
                        self.temp[row[1]] = print_line
                    else:
                        self.temp[row[2] + row[3]] = print_line                

        #report the extracted data------------------------------------------------------------------
        self.print_report (titles = titles,
                           report_id = 'PRSTAX',
                           report_name = report_desc,
                           Params = Params)
        return



    def ligeog(self, message):
        """list the geography of the railroad.  for each railroad, list the areas.  for each
        area, list the stations.  for each station, list the places (with unigue id as well as
        the station/place code)
        """
        if self.show_access(message, 'LIGEOG', 'R') != 0:
            return
        print('                       RAILROAD / AREA / STATION / PLACE')

        sql = 'select railroad, name from railroad order by railroad'
        count, ds_railroads = self.db_read(sql, '')
        for rr in ds_railroads:
            print(rr[0] + ' ' + rr[1])
            sql2 = 'select area, name from area where railroad = ? order by area'
            t2 = (rr[0],)
            count, ds_areas = self.db_read(sql2, t2)
            for area in ds_areas:
                print('    ' + area[0] + ' ' + area[1])
                sql3 = 'select station, long_name from station where area = ? order by station'
                t3 = (area[0],)
                count, ds_stations = self.db_read(sql3, t3)
                for station in ds_stations:
                    print('        ' + station[0] + ' ' + station[1])
                    sql4 = 'select code, name, id from place where station = ? order by code'
                    t4 = (station[0],)
                    count, ds_places = self.db_read(sql4, t4)
                    for place in ds_places:
                        print('            ' + place[0] + ' ' + place[1] + ' (+' + str(place[2]) + ')' )
        print(' ** END OF DATA:' + str(count) + ' RECORDS DISPLAYED **')         
        return


    def prgeog(self, message, Params):
        """report the geography of the railroad.  for each railroad, list the areas.  for each
        area, list the stations.  for each station, list the places (with unigue id as well as
        the station/place code)
        """
        if self.show_access(message, 'PRGEOG', 'R') != 0:
            return
        titles = 'RAILROAD / AREA / STATION / PLACE'
        i = 1
        self.temp = {}

        sql = 'select railroad, name from railroad order by railroad'
        count, ds_railroads = self.db_read(sql, '')
        if count < 0:
            return
        for rr in ds_railroads:
            self.temp[i] = rr[0] + ' ' + rr[1]
            i = i + 1
            sql2 = 'select area, name from area where railroad = ? order by area'
            t2 = (rr[0],)
            count, ds_areas = self.db_read(sql2, t2)
            if count < 0:
                return
            for area in ds_areas:
                self.temp[i] =  '    ' + area[0] + ' ' + area[1]
                i = i + 1
                sql3 = 'select station, long_name from station where area = ? order by station'
                t3 = (area[0],)
                count, ds_stations = self.db_read(sql3, t3)
                for station in ds_stations:
                    self.temp[i] =  '        ' + station[0] + ' ' + station[1]
                    i = i + 1
                    sql4 = 'select code, name, id from place where station = ? order by code'
                    t4 = (station[0],)
                    count, ds_places = self.db_read(sql4, t4)
                    for place in ds_places:
                        self.temp[i] = '            ' + place[0] + ' ' + place[1] + ' (+' + str(place[2]) + ')' 
                        i = i + 1
            
        #report the extracted data -----------------------------------------------------------------
        self.print_report (titles = titles,
                           report_id = 'PRGEOG',
                           report_name = 'GEOGRAPHICAL LIST OF PLACES',
                           Params = Params)
        return



    def get_id_for_station_and_place(self, station, place):
        """look up to return a unique id given a station and a place
        """
        place_found = 0
        data = (station, place)
        sql = 'select id from place where station = ? and code = ?'
        count, ds_places = self.db_read(sql, data)
        if count < 0:
            return 0
        if count == 0:
            return 0

        for row in ds_places:
            place_found = row[0]
        return place_found
        


    def get_usage_name(self, place_type, industry):
        """provides a description for the place usage type.  if an industry returns the industry
        name
        """
        if place_type == 'D':
            usage = 'REFUEL DIESL'
        elif place_type == 'S':
            usage = 'REFUEL STEAM'
        elif place_type == 'O':
            usage = 'REFUEL OTHER'
        elif place_type == 'L':
            usage = 'MAINT LOCOS'
        elif place_type == 'M':
            usage = 'MAINT CARS'
        elif place_type == 'C':
            usage = 'CLEAN CARS'
        elif place_type == 'I':
            usage = industry
        else:
            usage = ' '
        return usage
