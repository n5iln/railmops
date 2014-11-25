'''
Station Types Class

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    15/08/2010 Ver 1 Removed unused variables
                     Changed handling of default description on CHSTAT
'''

import MOPS_Element


class cStationTypes(MOPS_Element.cElement):
    """details about station types.  station types determine the nature of a station.  a station type
    holds a description and are linked to stations.
    """
    extract_code = 'select * from stationtype'
    extract_header = 'id|stat|station_type_desc\n'



    def adstat(self, message):
        """add a station type and a description.  the station type cannot already exist.
        """
        if self.show_access(message, 'ADSTAT station type;description', 'S') != 0:
            return

        #station type code--------------------------------------------------------------------------
        station_type, rc = self.extract_field(message, 0, 'STATION TYPE CODE')
        if rc > 0:
            return

        if len(station_type) > self.statsize:
            print('* STATION TYPE CODE IS GREATER THAN THE ALLOWED SIZE')
            return
                
        if len(station_type) == 0:
            print('* CANNOT DETERMINE STATION TYPE CODE - BLANKS NOT ALLOWED')
            return

        #check it does not already exist on the database
        data = (station_type,)
        sql = 'select id from stationtype where stationtype = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count != 0:
            print('* STATION TYPE CODE ALREADY EXISTS')
            return        

        #station type description-------------------------------------------------------------------
        station_type_desc, rc = self.extract_field(message, 1, 'STATION TYPE DESCRIPTION')
        if rc > 0:
            return

        #carry out the update-----------------------------------------------------------------------
        data = (station_type, station_type_desc)
        sql = 'insert into stationtype values (null, ?, ?)'
        if self.db_update(sql, data) != 0:
            return

        print('NEW STATION TYPE ADDED SUCCESSFULLY')
        print(station_type + station_type_desc)
        return 



    def chstat(self, message):
        """change a station type description
        """
        if self.show_access(message, 'CHSTAT station type;description', 'S') != 0:
            return

        #station type code--------------------------------------------------------------------------
        station_type, rc = self.extract_field(message, 0, 'STATION TYPE CODE')
        if rc > 0:
            return

        #read the database and populate the fields
        data = (station_type,)
        sql = 'select desc from stationtype where stationtype = ?'
        count, ds_station_types = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* STATION TYPE CODE DOES NOT EXIST')
            return

        for row in ds_station_types:
            station_type_desc = row[0]

        #station type description-------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, 'STATION TYPE DESCRIPTION')
        if rc > 0:
            return
        if rc == 0:
            station_type_desc = value

        #carry out the update-----------------------------------------------------------------------
        data = (station_type_desc, station_type)
        sql = 'update stationtype set desc = ? where stationtype = ?'
        if self.db_update(sql, data) != 0:
            return

        print('STATION TYPE DESCRIPTION CHANGED')
        print(station_type + station_type_desc)
        return

    
    
    def dxstat(self, message):
        """deletes a station type from the list.  checks that no stations are using it
        """
        if self.show_access(message, 'DXSTAT station type', 'S') != 0:
            return

        #station type code
        station_type, rc = self.extract_field(message, 0, 'STATION TYPE CODE')
        if rc > 0:
            return

        data = (station_type,)

        #validate the change
        sql = 'select id from stationtype where stationtype = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* STATION TYPE CODE DOES NOT EXIST')
            return

        #make sure that there is no station linked to the type
        sql = 'select id from station where stationtype = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count > 0:
            print('* STATIONS ARE LINKED TO THIS RAILROAD: DELETE CANCELLED')
            return

        #process the delete
        if self.db_update('delete from stationtype where stationtype = ?', data) != 0:
            return
        print('STATION TYPE' + station_type + 'SUCCESSFULLY DELETED')
        return



    def listat(self, message):
        """list station type details to the screen.  sortable by description or code.
        """
        if self.show_access(message, 'LISTAT (sort[0/1])', 'R') != 0:
            return

        #get the sort requirement from teh message
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort = value
        else:
            sort = '0'

        #build the column titles
        titles = self.x_field('TYPE====', self.statsize)  + ' '      +\
                 self.x_field('DESCRIPTION=================== ', 30)
        
        #get the extract data
        if sort == '1':
            sql = 'select stationtype, desc from stationtype order by desc'
        else:
            sql = 'select stationtype, desc from stationtype order by stationtype'

        count, ds_station_types = self.db_read(sql, '')
        if count < 0:
            return
        
        #report the extracted data
        line_count = 0
        for row in ds_station_types:
            if line_count == 0:
                print(titles)
            print(self.x_field(row[0], self.statsize) + " " +
                   self.x_field(row[1], 30))
            line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break
        print(' ** END OF DATA:' + str(count) + ' RECORDS DISPLAYED **')         
        return



    def prstat(self, message, Params):
        """print station type details to a file.  sortable by description or code.  the report also
        shows the number of stations allocated to that station type
        """
        if self.show_access(message, 'PRSTAT (sort[0/1])', 'R') != 0:
            return

        #get the sort requirement
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort = value
        else:
            sort = '0'

        # build the column titles.  this is different to the listing as it includes a
        #station count
        titles = self.x_field('TYPE====', self.statsize) + ' '        +\
                 self.x_field('DESCRIPTION=================== ', 31)  +\
                 self.x_field('STTNS=', 6)

        #get the extract data
        if sort == '1':
            sql = 'select stationtype, desc from stationtype order by desc'
            report_desc = 'LIST OF STATION TYPES SORTED BY DESCRIPTION'
        else:
            sql = 'select stationtype, desc from stationtype order by stationtype'
            report_desc = 'LIST OF STATION TYPES SORTED BY CODE'

        count, ds_station_types = self.db_read(sql, '')
        if count < 0:
            return
        
        #build the extracted data
        self.temp = {}
        for row in ds_station_types:
            data = (row[0],)
            sql = 'select id from station where stationtype = ?'
            stations_count, data = self.db_read(sql, data)
            print_line = self.x_field(row[0], self.statsize)      + ' ' +\
                         self.x_field(row[1], 30)                 + ' ' +\
                         self.x_field(str(stations_count), 6, 'R')
            if message == '1':
                self.temp[row[1]] = print_line
            else:
                self.temp[row[0]] = print_line

        #report the extracted data
        self.print_report (titles = titles,
                           report_id = 'PRSTAT',
                           report_name = report_desc,
                           Params = Params)
        return
