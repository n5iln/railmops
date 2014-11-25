'''
Car Order Class

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    13/08/2010 Ver 1. Removed import module re 
                      Corrected name of variable in LORDER
                      Added details of cars to DEMPTY
'''

import MOPS_Element
therr = ""
class cOrders(MOPS_Element.cElement):
    """provides information about requirements for empty cars and car orders to move
    loaded cars
    """
    extract_code = 'select * from waybill'
    extract_header = 'id|warehouse|type|requires|clean_cars|loading|unloading|' +\
                     'commodity|origin|destination|status|timestamp\n'


    def lempty(self, message):
        """list outstanding order for empty cars
        """
        if self.show_access(message, 'LEMPTY', 'R') != 0:
            return

        # titles for report
        titles = self.x_field('ORDER', 5) + ' ' +\
                 self.x_field('INDUSTRY==', 10) + ' ' +\
                 self.x_field('STATION===', 8) + ' ' +\
                 self.x_field('CLASS=====', self.classize) + ' ' +\
                 self.x_field('CARS=', 5) + ' ' +\
                 self.x_field('CLN', 3) + ' ' +\
                 self.x_field('DESTINATN=', 10) + ' ' +\
                 self.x_field('DEST STN==', 8) + ' ' +\
                 self.x_field('REQUESTED======', 15)

        #get the extract data
        t = ('E', 'O')
        sql = 'select waybill.id, '   +\
              'waybill.origin, '    + \
              'station.short_name, '     + \
              'waybill.commodity, '   + \
              'waybill.requires, '        +\
              'waybill.clean_cars, '  +\
              'waybill.destination, ' +\
              'waybill.timestamp, '        +\
              'warehouse.threshold_class ' +\
              'from waybill, warehouse, place, station ' +\
              'where waybill.warehouse = warehouse.id and ' +\
              'warehouse.industry = place.industry and '             +\
              'place.station = station.station and '   +\
              'waybill.type = ? and waybill.status = ? ' +\
              'order by waybill.timestamp'
        count, ds_orders = self.db_read(sql, t)
        if count < 0:
            return

        #--------------------------------------------------------------------------------------------
        #process the extracted data
        line_count = 0
        for row in ds_orders:
            if line_count == 0:
                print(titles)
            waybill_id = row[0]
            data = (waybill_id,)
            sql = 'select station.short_name '     + \
                  'from waybill, place, station ' +\
                  'where waybill.destination = place.industry and '             +\
                  'place.station = station.station and ' +\
                  'waybill.id = ?'
            countx, ds_dest = self.db_read(sql, data)
            if countx < 0:
                return
            for dest_row in ds_dest:
                dest_name = dest_row[0]
            print(self.x_field(str(row[0]), 5, 'R') + ' ' +
                   self.x_field(row[1], 10) + ' ' +
                   self.x_field(row[2], 8) + ' ' +
                   self.x_field(row[8], self.classize) + ' ' +
                   self.x_field(row[4], 5, 'R') + ' ' +
                   self.x_field(row[5], 3, 'R') + ' ' +
                   self.x_field(row[6], 10) + ' ' +
                   self.x_field(dest_name, 8) + ' ' +
                   self.x_field(row[7], 15, 'R'))
            line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break
        print(' ** END OF DATA:' + str(count) + ' RECORDS DISPLAYED **')         
        return


    def lorder(self, message):
        """list all outstanding orders for loaded and empty cars
        """
        if self.show_access(message, 'LORDER', 'R') != 0:
            return

        # titles for report
        titles = self.x_field('ORDER', 5) + ' ' +\
                 self.x_field('TYPE', 4) + ' ' +\
                 self.x_field('STAT', 4) + ' ' +\
                 self.x_field('INDUSTRY==', 10) + ' ' +\
                 self.x_field('ORIG/PLACE==========', self.staxsize + self.plaxsize + 1) + ' ' +\
                 self.x_field('DESTINATN=', 10) + ' ' +\
                 self.x_field('DEST/PLACE=========', self.staxsize + self.plaxsize + 1) + ' ' +\
                 self.x_field('CLASS=====', self.classize) + ' ' +\
                 self.x_field('CLN', 5) + ' ' +\
                 self.x_field('O/S C', 3) 

        #get the extract data
        data = ('C',)
        sql =   'select waybill.id, waybill.type, waybill.status, waybill.origin, ' +\
                'orig.station as o_station, orig.code as o_plax,' +\
                'waybill.destination, dest.station as d_station, dest.code as d_plax,' +\
                'warehouse.threshold_class, ' +\
                'waybill.clean_cars, waybill.requires ' +\
                'from waybill, warehouse, place orig, place dest ' +\
                'where waybill.warehouse = warehouse.id ' +\
                'and orig.industry = waybill.origin ' +\
                'and dest.industry = waybill.destination ' +\
                'and status != ? ' +\
                'order by waybill.timestamp '
        count, ds_orders = self.db_read(sql, data)
        if count < 0:
            return

        #--------------------------------------------------------------------------------------------
        #process the extracted data
        line_count = 0
        for row in ds_orders:
            bill_id    = row[0]
            bill_type  = row[1]
            bill_stat  = row[2]
            bill_orig  = row[3]
            orig_stax  = row[4]
            orig_plax  = row[5]
            bill_dest  = row[6]
            dest_stax  = row[7]
            dest_plax  = row[8]
            bill_class = row[9]
            bill_clean = row[10]
            bill_cars  = row[11]
            if bill_type == 'E':
                bill_type = 'MTY '
            else:
                bill_type = 'LOAD'
            if bill_stat == 'O':
                bill_stat = 'O/S '
            else:
                bill_stat = '    '                                                        #Ver 1
            orig_stax = orig_stax + '/' + orig_plax
            dest_stax = dest_stax + '/' + dest_plax
            if line_count == 0:
                print(titles)
                
            print(self.x_field(str(bill_id), 5, 'R') + " " +
                   self.x_field(bill_type, 4) + " " +
                   self.x_field(bill_stat, 4) + " " +
                   self.x_field(bill_orig, 10) + " " +
                   self.x_field(orig_stax, self.staxsize + self.plaxsize + 1) + " " +
                   self.x_field(bill_dest, 10) + " " +
                   self.x_field(dest_stax, self.staxsize + self.plaxsize + 1) + " " +
                   self.x_field(bill_class, self.classize) + " " +
                   self.x_field(bill_clean, 2, 'R') + " " +
                   self.x_field(bill_cars, 6, 'R'))
            line_count = line_count + 1
            if line_count > 22:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break
        print(' ** END OF DATA:' + str(count) + ' RECORDS DISPLAYED **')         
        return


    def dempty(self, message):
        """list detail of an outstanding order for empty cars
        """
        if self.show_access(message, 'DEMPTY (^order^)', 'R') != 0:
            return

        order, rc = self.extract_field(message, 0, 'ORDER ID')
        if rc > 0:
            return

        #get the extract data
        t = (order, )
        sql = 'select waybill.id, '   +\
              'waybill.origin, '    + \
              'station.short_name, '     + \
              'waybill.commodity, '   + \
              'waybill.requires, '        +\
              'waybill.clean_cars, '  +\
              'waybill.destination, ' +\
              'waybill.timestamp, '        +\
              'warehouse.threshold_class ' +\
              'from waybill, warehouse, place, station ' +\
              'where waybill.warehouse = warehouse.id and ' +\
              'warehouse.industry = place.industry and '             +\
              'place.station = station.station and '   +\
              'waybill.id = ?'
        count, ds_orders = self.db_read(sql, t)
        if count < 0:
            return

        for row in ds_orders:
            waybill_id = row[0]
            origin = row[1]
            origin_name = row[2]
            commodity = row[3]
            requires = row[4]
            clean_cars = row[5]
            destination = row[6]
            timestamp = row[7]
            car_class = row[8]

        data = (waybill_id,)
        sql = 'select station.short_name, place.unloading '     + \
              'from waybill, place, station ' +\
              'where waybill.destination = place.industry and '             +\
              'place.station = station.station and ' +\
              'waybill.id = ?'
        countx, ds_dest = self.db_read(sql, data)
        if countx < 0:
            return
        for dest_row in ds_dest:
            dest_name = dest_row[0]
            dest_unloading = dest_row[1]

        data = (origin,)
        sql = 'select id, track_length, loading ' +\
              'from place ' +\
              'where place.industry = ?'
        county, ds_plax = self.db_read(sql, data)
        if county < 0:
            return
        for plax_row in ds_plax:
            plax_id = plax_row[0]
            track_length = plax_row[1]
            loading = plax_row[2]

        data = (plax_id,)
        sql = 'select cartype.length, car.commodity ' +\
              'from cartype, car ' +\
              'where cartype.cartype = car.cartype ' +\
              'and car.place_id = ?'
        countz, ds_cars = self.db_read(sql, data)
        if countz < 0:
            return
        cars_length = 0
        for cars_row in ds_cars:
            length = cars_row[0]
            cars_length = cars_length + length
            commodity = cars_row[1]

        data = (commodity,)
        sql = 'select name from commodity where commodity = ?'
        countzz, ds_comm = self.db_read(sql, data)
        if countzz < 0:
            return
        for row_comm in ds_comm:
            commodity_name = row_comm[0]

        print('ID:' + str(waybill_id) + ' ORIGIN:' + origin + origin_name + ' DEST:' + destination + dest_name)
        print('COMMODITY:' + commodity + " " + ' LOAD:' + loading + ' UNLOAD:' + dest_unloading + ' CLEAN CARS?' + clean_cars)
        print('REQUIRES:' + str(requires) + car_class + ' TRACK:' + str(track_length) + 'OCCUPIED:' + str(cars_length))
        print('ORDER ORIGINALLY RAISED' + timestamp)
        
        data = (waybill_id,)                                                   #Rev 1 added cars
        sql = 'select car.railroad, car.car, car.carclass, car.commodity, car.station, car.place_id,  ' +\
              'car.train, car.block ' +\
              'from car ' +\
              'where carorder = ? ' +\
              'order by car.railroad, car.car'
        count, ds_cars = self.db_read(sql, data)
        if count < 0:
            return
        for cars in ds_cars:
            rr = cars[0]
            car = cars[1]
            carclass = cars[2]
            if cars[3] != '':
                status = 'LOAD'
            else:
                status = 'MTY '
            station = cars[4]
            place = cars[5]
            train = cars[6]
            block = cars[7]
            print(self.x_field(rr, self.railsize) + " " +
                   self.x_field(car, self.carxsize) + " " +
                   self.x_field(carclass, self.classize) + " " +
                   self.x_field('AT:', 3) + " " +
                   self.x_field(station, self.staxsize) + " " +
                   self.x_field(place, self.plaxsize) + " " +
                   self.x_field('TRAIN:', 6) + " " +
                   self.x_field(train, 5) + " " +
                   self.x_field(block, 5) + " " +
                   self.x_field(status, 4))
        return


    def pempty(self, message, Params):
        """prints outstanding order for empty cars
        """
        if self.show_access(message, 'PEMPTY', 'R') != 0:
            return

        # titles for report
        titles = self.x_field('ORDER', 5) + ' ' +\
                 self.x_field('INDUSTRY==', 10) + ' ' +\
                 self.x_field('STATION===', 8) + ' ' +\
                 self.x_field('COMMODITY=', self.commsize) + ' ' +\
                 self.x_field('CARS=', 5) + ' ' +\
                 self.x_field('CLN', 3) + ' ' +\
                 self.x_field('DESTINATN=', 10) + ' ' +\
                 self.x_field('DEST STN==', 8) + ' ' +\
                 self.x_field('REQUESTED======', 15)

        #get the extract data
        t = ('E', 'O')
        sql = 'select waybill.id, '   +\
              'waybill.origin, '    + \
              'station.short_name, '     + \
              'waybill.commodity, '   + \
              'waybill.requires, '        +\
              'waybill.clean_cars, '  +\
              'waybill.destination, ' +\
              'waybill.timestamp '        +\
              'from waybill, warehouse, place, station ' +\
              'where waybill.warehouse = warehouse.id and ' +\
              'warehouse.industry = place.industry and '             +\
              'place.station = station.station and '   +\
              'waybill.type = ? and waybill.status = ? ' +\
              'order by waybill.timestamp'
        count, ds_orders = self.db_read(sql, t)
        if count < 0:
            return

        #process the extracted data
        self.temp = {}
        i = 0

        for row in ds_orders:
            i = i + 1
            waybill_id = row[0]
            data = (waybill_id,)
            sql = 'select station.short_name '     + \
                  'from waybill, place, station ' +\
                  'where waybill.destination = place.industry and '             +\
                  'place.station = station.station and ' +\
                  'waybill.id = ?'
            countx, ds_dest = self.db_read(sql, data)
            if countx < 0:
                return
            for dest_row in ds_dest:
                dest_name = dest_row[0]
            print_line = self.x_field(str(row[0]), 5, 'R') + ' ' +\
                   self.x_field(row[1], 10) + ' ' +\
                   self.x_field(row[2], 8) + ' ' +\
                   self.x_field(row[3], self.commsize) + ' ' +\
                   self.x_field(row[4], 5, 'R') + ' ' +\
                   self.x_field(row[5], 3, 'R') + ' ' +\
                   self.x_field(row[6], 10) + ' ' +\
                   self.x_field(dest_name, 8) + ' ' +\
                   self.x_field(row[7], 15, 'R')
            self.temp[i] = print_line

        #--------------------------------------------------------------------------------------------
        #report the extracted data
        self.print_report (titles = titles,
                           report_id = 'PEMPTY',
                           report_name = 'LIST DEMANDS FOR EMPTY CARS',
                           Params = Params)       
        return
    
