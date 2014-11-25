'''
Warehouse Class

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    Rev 1 Unused variables removed
          Changed handling of default production rate in CPWARE
          LDWARE to only report outstanding waybills on order
          Amended LDWARE to reduce ordered by cars already at warehouse
          Amended LDWARE to show difference between ordered/onway
          LDWARE amended to not show loaded movements
          Station and Place added to Flash message (both Origin and Destination)
'''

import MOPS_Element


class cWarehouses(MOPS_Element.cElement):
    """details about warehouses.  warehouses are unique on an origin-commodity-destination basis.
    warehouses are allocated to industries on the place file.  industries produce commodities at
    a given rate which are stored up to a given value.  at threshold values, empty cars of the
    required type are ordered.  warehouses know about the required customer routing of loaded
    cars.
    """
    extract_code = 'select * from warehouse'
    extract_header = 'id|industry|commodity|dest industry|prodn rate|threshold goods|' +\
                     'threshold cars|threshold class|max storage|in storage|ordered|routing\n'



    def adware(self, message):
        """add a new warehouse.  the warehouse is linked to an industry, a destination (for the
        loaded wagons) and a commodity.  the rate of production is held.  at a given threshold
        value of production, cars of a specific type are requested.  a note of previously ordered
        wagons is held (to enable further requests for empty cars to be made).
        """
        if self.show_access(message,
                            'ADWARE ^industry^;^commodity^;^destination^;prod rate;threshold quantity;' +\
                            'cars to order;^class of car^;max storage;^customer routing^',
                            'S') != 0:
            return
        errors = 0

        #industry------------------------------------------------------------------------------------
        industry, rc = self.extract_field(message, 0, 'INDUSTRY')
        if rc > 0:
            return

        t = (industry, )
        sql = 'select name, loading from place where industry = ?'
        count, ds_industries = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* INDUSTRY CODE DOES NOT EXIST (' + str(industry) + ')')
            return
        else:
            for row in ds_industries:
                industry_name = row[0]
                industry_loading = row[1]

        #commodity----------------------------------------------------------------------------------
        commodity, rc = self.extract_field(message, 1, 'COMMODITY')
        if rc > 0:
            return

        t = (commodity, )
        sql = 'select name, loading from commodity where commodity = ?'
        count, data = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            print('* COMMODITY CODE DOES NOT EXIST (' + commodity + ')')
            return
        else:
            for row in data:
                commodity_name = row[0]
                commodity_loading = row[1]

        if commodity_loading != industry_loading:
            errors = errors + 1
            print('* COMMODITY CANNOT BE LOADED AT THIS PLACE: LOADING CODES DISAGREE')

        #destination industry-----------------------------------------------------------------------
        destination, rc = self.extract_field(message, 2, 'DESTINATION INDUSTRY')
        if rc > 0:
            return

        t = (destination, )
        sql = 'select name, unloading from place where industry = ?'
        count, data = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* DESTINATION INDUSTRY CODE DOES NOT EXIST (' + destination + ')')
        else:
            for row in data:
                destination_name = row[0]
                destination_unloading = row[1]

        # check that the industry/commodity/destination combo doesn't exist-------------------------
        t = (industry, commodity, destination)
        sql = 'select id from warehouse where industry = ? and commodity = ? and destination = ?'
        count, data = self.db_read(sql, t)
        if count < 0:
            return
        if count > 0:
            print('* INDUSTRY/COMMODITY/DESTINATION COMBINATION ALREADY EXISTS')
            errors = errors + 1

        #production---------------------------------------------------------------------------------
        production, rc = self.extract_field(message, 3, 'PRODUCTION RATE')
        if rc > 0:
            return

        try:
            if int(production) > 99999 or int(production) < 0:
                errors = errors + 1
                print('* PRODUCTION RATE MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* PRODUCTION RATE MUST BE A WHOLE NUMBER')
            
        #threshold goods----------------------------------------------------------------------------
        threshold_goods, rc = self.extract_field(message, 4, 'THRESHOLD TO ORDER CARS')
        if rc > 0:
            return

        try:
            if int(threshold_goods) > 99999 or int(threshold_goods) < 0:
                errors = errors + 1
                print('* THRESHOLD MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* THRESHOLD MUST BE A WHOLE NUMBER')

        #threshold cars-----------------------------------------------------------------------------
        threshold_cars, rc = self.extract_field(message, 5, 'NUMBER OF CARS TO ORDER')
        if rc > 0:
            return

        try:
            if int(threshold_cars) > 99999 or int(threshold_cars) < 0:
                errors = errors + 1
                print('* NUMBER OF CARS MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* NUMBER OF CARS MUST BE A WHOLE NUMBER')

        #threshold car class------------------------------------------------------------------------
        threshold_class, rc = self.extract_field(message, 6, 'CAR CLASS')
        if rc > 0:
            return

        t = (threshold_class, )
        sql = 'select id from carclass where carclass = ?'
        count, data = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* CAR CLASS CODE DOES NOT EXIST (' + threshold_class + ')')

        #max storage--------------------------------------------------------------------------------
        max_storage, rc = self.extract_field(message, 7, 'MAXIMUM STORAGE')
        if rc > 0:
            return

        try:
            if int(max_storage) > 99999 or int(max_storage) < 0:
                errors = errors + 1
                print('* MAXIMUM STORAGE MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* MAXIMUM STORAGE MUST BE A WHOLE NUMBER')

        #routing------------------------------------------------------------------------------------
        routing, rc = self.extract_field(message, 8, 'ROUTING CODE')
        if rc > 0:
            return

        t = (routing, )
        sql = 'select desc from routing where routing = ?'
        count, ds_routing = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* ROUTING CODE DOES NOT EXIST (' + routing + ')')
        else:
            for row in ds_routing:
                routing_name = row[0]

        #carry out the update-----------------------------------------------------------------------
        if errors != 0:
            return

        ordered = 0
        in_storage = 0
        t = (industry, commodity, destination, production, threshold_goods, threshold_cars,
             threshold_class, max_storage, in_storage, ordered, routing)
        sql = 'insert into warehouse values (null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        if self.db_update(sql, t) != 0:
            return

        t = (industry, commodity)
        sql = 'select id from warehouse where industry = ? and commodity = ? order by id'
        count, data = self.db_read(sql, t)
        for row in data:
            code = row[0]

        print('NEW WAREHOUSE ADDED SUCCESSFULLY')
        print('ID:' + str(code) + industry + industry_name)
        print('COMMODITY:' + commodity + commodity_name)
        print('DESTINATION:' + destination + destination_name + 'UNLOADING:',
               destination_unloading)
        print('PRODUCTION:' + str(production) + 'MAX STORAGE:' + str(max_storage) +
               'ORDER AT:' + str(threshold_goods) + 'FOR:' + str(threshold_cars) +
               'CAR(S) OF TYPE:' + threshold_class)
        print('ROUTING:' + routing + '(' + routing_name + ')')
        return errors



    def chware(self, message):
        """change a new warehouse.  the warehouse is linked to an industry, a destination (for the
        loaded wagons) and a commodity.  the rate of production is held.  at a given threshold
        value of production, cars of a specific type are requested.  a note of previously ordered
        wagons is held (to enable further requests for empty cars to be made).
        """
        if self.show_access(message,
                            'CHWARE warehouse id;(^industry^);(^commodity^);(^destination^);(prod rate);' +\
                            '(threshold quantity);(cars to order);(^class of car^);' +\
                            '(max storage);(^customer routing^)',
                            'S') != 0:
            return
        errors = 0

        #warehouse code-----------------------------------------------------------------------------
        warehouse, rc = self.extract_field(message, 0, 'WAREHOUSE CODE')
        if rc > 0:
            return

        #read the database and populate the fields
        t = (warehouse,)
        sql = 'select industry, commodity, destination, production, '    +\
              'threshold_goods, threshold_cars, threshold_class, max_storage, '   +\
              'in_storage, routing from warehouse where warehouse.id = ?'
        count, ds_warehouse = self.db_read(sql, t)
        if count < 0:
            return

        for row in ds_warehouse:
            industry        = row[0]
            commodity       = row[1]
            destination     = row[2]
            production      = row[3]
            threshold_goods = row[4]
            threshold_cars  = row[5]
            threshold_class = row[6]
            max_storage     = row[7]
            routing         = row[9]
                
        #industry-----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 1, '')
        if rc == 0:
            industry = value

        t = (industry, )
        sql = 'select industry from place where industry = ?'
        count, ds_industry = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* INDUSTRY CODE DOES NOT EXIST (' + str(value) + ')')
        else:
            for row in ds_industry:
                industry_name = row[0]

        #commodity----------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 2, '')
        if rc == 0:
            commodity = value

        t = (commodity, )
        sql = 'select name from commodity where commodity = ?'
        count, ds_commodity = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* COMMODITY CODE DOES NOT EXIST (' + value + ')')
        else:
            for row in ds_commodity:
                commodity_name = row[0]

        #destination industry-----------------------------------------------------------------------
        value, rc = self.extract_field(message, 3, '')
        if rc == 0:
            destination = value

        t = (destination, )
        sql = 'select industry, unloading from place where industry = ?'
        count, ds_destination = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* DESTINATION INDUSTRY CODE DOES NOT EXIST (' + destination + ')')
        else:
            for row in ds_destination:
                destination_name = row[0]
                destination_unloading = row[1]

        # check that the industry/commodity/destination combo doesn't exist-------------------------
        t = (industry, commodity, destination)
        sql = 'select id, industry, commodity, destination from warehouse ' +\
              'where industry = ? and commodity = ? and destination = ?'
        count, ds_warehouses = self.db_read(sql, t)
        if count < 0:
            return
        if count > 0:
            for row in ds_warehouses:
                if str(row[0]) != str(warehouse):
                    print('* INDUSTRY/COMMODITY/DESTINATION COMBINATION ALREADY EXISTS')
                    errors = errors + 1

        #production---------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 4, '')
        if rc == 0:
            production = value

        try:
            if int(production) > 99999 or int(production) < 0:
                errors = errors + 1
                print('* PRODUCTION RATE MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* PRODUCTION RATE MUST BE A WHOLE NUMBER')
            
        #threshold goods----------------------------------------------------------------------------
        value, rc = self.extract_field(message, 5, '')
        if rc == 0:
            threshold_goods = value

        try:
            if int(threshold_goods) > 99999 or int(threshold_goods) < 0:
                errors = errors + 1
                print('* THRESHOLD MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* THRESHOLD MUST BE A WHOLE NUMBER')

        #threshold cars-----------------------------------------------------------------------------
        value, rc = self.extract_field(message, 6, '')
        if rc == 0:
            threshold_cars = value

        try:
            if int(threshold_cars) > 99999 or int(threshold_cars) < 0:
                errors = errors + 1
                print('* NUMBER OF CARS MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* NUMBER OF CARS MUST BE A WHOLE NUMBER')

        #threshold car class------------------------------------------------------------------------
        value, rc = self.extract_field(message, 7, '')
        if rc == 0:
            threshold_cars = value

        t = (threshold_class, )
        sql = 'select id from carclass where carclass = ?'
        count, dummy = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            errors = errors + 1
            print('* CAR CLASS CODE DOES NOT EXIST (' + value + ')')

        #max storage--------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 8, '')
        if rc == 0:
            max_storage = value

        try:
            if int(max_storage) > 99999 or int(max_storage) < 0:
                errors = errors + 1
                print('* MAXIMUM STORAGE MUST BE IN THE RANGE 0 to 99999')
        except:
            errors = errors + 1
            print('* MAXIMUM STORAGE MUST BE A WHOLE NUMBER')

        #routing------------------------------------------------------------------------------------
        value, rc = self.extract_field(message, 9, '')
        if rc == 0:
            routing = value

        t = (routing, )
        sql = 'select desc from routing where routing = ?'
        count, ds_routing = self.db_read(sql, t)
        if count < 0:
            return

        if count == 0:
            errors = errors + 1
            print('* ROUTING CODE DOES NOT EXIST (' + value + ')')
        else:
            for row in ds_routing:
                routing_name = row[0]
                
        #carry out the update-----------------------------------------------------------------------
        if errors != 0:
            return
        
        t = (industry, commodity, destination, production, threshold_goods, threshold_cars,
             threshold_class, max_storage, routing, warehouse)
        sql = 'update warehouse set industry = ?, commodity = ?, destination = ?, ' +\
              'production = ?, threshold_goods = ?, threshold_cars = ?, threshold_class = ?, ' +\
              'max_storage = ?, routing = ? where id = ?'
        if self.db_update(sql, t) != 0:
            return

        print('WAREHOUSE DETAILS CHANGED SUCCESSFULLY')
        print('ID:' + str(warehouse), industry, industry_name)
        print('COMMODITY:' + commodity, commodity_name)
        print('DESTINATION:' + destination, destination_name, 'UNLOADING:',
               destination_unloading)
        print('PRODUCTION:' + str(production), 'MAX STORAGE:' + str(max_storage),
               'ORDER AT:' + str(threshold_goods), 'FOR:' + str(threshold_cars),
               'CAR(S) OF TYPE:' + threshold_class)
        print('ROUTING:' + routing, '(' + routing_name + ')')
        return

    

    def dxware(self, message):
        """deletes a warehouse from the list.  checks that it is not on a car order
        """
        if self.show_access(message, 'DXWARE id', 'S') != 0:
            return

        #warehouse code-----------------------------------------------------------------------------
        ware, rc = self.extract_field(message, 0, 'WAREHOUSE CODE')
        if rc > 0:
            return

        t = (ware,)

        #validate the change - check there is a record to delete------------------------------------
        sql = 'select id from warehouse where id = ?'
        count, dummy = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            print('* WAREHOUSE DOES NOT EXIST')
            return
        
        #check whether the warehouse is on a car order----------------------------------------------
        sql = 'select id from waybill where warehouse = ?'
        count, dummy = self.db_read(sql, t)
        if count < 0:
            return
        if count > 0:
            print('* WAREHOUSE CURRENTLY IN USE ON A CAR ORDER, CANNOT DELETE')
            return

        #process the change-------------------------------------------------------------------------
        if self.db_update('delete from warehouse where id = ?', t) == 0:
            print('WAREHOUSE', ware, 'SUCCESSFULLY DELETED')
        return



    def cpware(self, message):
        """change a production rate at a warehouse
        """
        if self.show_access(message, 'CPWARE warehouse id;prod rate', 'S') != 0:
            return

        #warehouse code-----------------------------------------------------------------------------
        warehouse, rc = self.extract_field(message, 0, 'WAREHOUSE CODE')
        if rc > 0:
            return

        #read the database and populate the fields
        t = (warehouse,)
        sql = 'select production from warehouse where warehouse.id = ?'
        count, ds_warehouse = self.db_read(sql, t)
        if count < 0:
            return
        if count == 0:
            print('* WAREHOUSE CODE DOES NOT EXIST FOR CHANGE')
            return

        for row in ds_warehouse:
            production      = row[0]

        #production
        value, rc = self.extract_field(message, 1, 'PRODUCTION RATE')
        if rc > 0:
            return
        if rc == 0:
            production = value

        try:
            if int(production) > 99999 or int(production) < 0:
                print('* PRODUCTION RATE MUST BE IN THE RANGE 0 to 99999')
                return
        except:
            print('* PRODUCTION RATE MUST BE A WHOLE NUMBER')
            return

        #carry out the update
        t = (production, warehouse)
        sql = 'update warehouse set production = ? where id = ?'
        self.db_update(sql, t)
        print('WAREHOUSE PRODUCTION RATE CHANGED SUCCESSFULLY')
        print('PRODUCTION RATE:' + str(production), 'FOR WAREHOUSE:' + str(warehouse))
        return



    def liware(self, message):
        """lists warehouse details. sortable by station/place/warehouse or by warehouse id
        """
        if self.show_access(message, 'LIWARE (sort[0/1])', 'R') != 0:
            return        

        #get any sort order
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        # build the column titles
        place_name = 78 - self.staxsize - self.plaxsize - self.commsize - self.classize - 45
        if place_name < 0:
            place_name = 1
        if place_name > 30:
            place_name = 30
        titles = self.x_field('STATION===', self.staxsize) + ' ' +\
                 self.x_field('PLACE=====', self.plaxsize) + ' ' +\
                 self.x_field('==============================', place_name) + ' ' +\
                 self.x_field('INDUSTRY==', 10) + ' ' +\
                 self.x_field('WAREHOUSE=', 5) + ' ' +\
                 self.x_field('COMMODITY=', self.commsize) + ' ' +\
                 self.x_field('PRODN', 5) + ' ' +\
                 self.x_field('MAX==', 5) + ' ' +\
                 self.x_field('ORDER', 5) + ' ' +\
                 self.x_field('CARS=', 5) + ' ' +\
                 self.x_field('CLASS=====', self.classize)

        #get the extract data
        if sort_order == '1':
            sql =   'select warehouse.id, warehouse.industry, warehouse.commodity, '  +\
                    'warehouse.production, warehouse.threshold_goods, ' +\
                    'warehouse.threshold_cars, warehouse.threshold_class, '         +\
                    'warehouse.max_storage, place.station, place.code, place.name ' +\
                    'from warehouse, place where warehouse.industry = place.industry ' +\
                    'order by place.station, place.code, place.industry, warehouse.id'
        else:
            sql =   'select warehouse.id, warehouse.industry, warehouse.commodity, '  +\
                    'warehouse.production, warehouse.threshold_goods, ' +\
                    'warehouse.threshold_cars, warehouse.threshold_class, '         +\
                    'warehouse.max_storage, place.station, place.code, place.name ' +\
                    'from warehouse, place where warehouse.industry = place.industry ' +\
                    'order by warehouse.id'
            
        count, ds_warehouses = self.db_read(sql, '')
        if count < 0:
            return

        #--------------------------------------------------------------------------------------------
        #report the extracted data
        line_count = 0
        for row in ds_warehouses:
            if line_count == 0:
                print(titles)               
            print(self.x_field(row[8], self.staxsize) + " " +
                   self.x_field(row[9], self.plaxsize) + " " +
                   self.x_field(row[10], place_name) + " " +
                   self.x_field(row[1], 10) + " " +
                   self.x_field(row[0], 5, 'R') + " " +
                   self.x_field(row[2], self.commsize) + " " +
                   self.x_field(row[3], 5, 'R') + " " +
                   self.x_field(row[7], 5, 'R') + " " +
                   self.x_field(row[4], 5, 'R') + " " +
                   self.x_field(row[5], 5, 'R') + " " +
                   self.x_field(row[6], self.classize))
            line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break
        print(' ** END OF DATA:' + str(count) + ' RECORDS DISPLAYED **')         
        return                   
                   


    def prware(self, message, Params):
        """print warehouse details.  sortable by station/place or by warehouse id
        """
        if self.show_access(message, 'PRWARE (sort[0/1])', 'R') != 0:
            return        

        #get any sort order
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        # build the column titles
        place_name = 79 - self.staxsize - self.plaxsize - self.commsize - self.classize - 45
        if place_name < 0:
            place_name = 1
        if place_name > 30:
            place_name = 30
        titles = self.x_field('STATION===', self.staxsize) + ' ' +\
                 self.x_field('PLACE=====', self.plaxsize) + ' ' +\
                 self.x_field('==============================', place_name) + ' ' +\
                 self.x_field('INDUSTRY==', 10) + ' ' +\
                 self.x_field('WAREHOUSE=', 5) + ' ' +\
                 self.x_field('COMMODITY=', self.commsize) + ' ' +\
                 self.x_field('PRODN', 5) + ' ' +\
                 self.x_field('MAX==', 5) + ' ' +\
                 self.x_field('ORDER', 5) + ' ' +\
                 self.x_field('CARS=', 5) + ' ' +\
                 self.x_field('CLASS=====', self.classize)

        #get the extract data
        if sort_order == '1':
            sql =   'select warehouse.id, warehouse.industry, warehouse.commodity, '  +\
                    'warehouse.production, warehouse.threshold_goods, ' +\
                    'warehouse.threshold_cars, warehouse.threshold_class, '         +\
                    'warehouse.max_storage, place.station, place.code, place.name ' +\
                    'from warehouse, place where warehouse.industry = place.industry ' +\
                    'order by place.station, place.code, place.industry, warehouse.id'
        else:
            sql =   'select warehouse.id, warehouse.industry, warehouse.commodity, '  +\
                    'warehouse.production, warehouse.threshold_goods, ' +\
                    'warehouse.threshold_cars, warehouse.threshold_class, '         +\
                    'warehouse.max_storage, place.station, place.code, place.name ' +\
                    'from warehouse, place where warehouse.industry = place.industry ' +\
                    'order by warehouse.id'
            
        count, ds_warehouses = self.db_read(sql, '')
        if count < 0:
            return

        #--------------------------------------------------------------------------------------------
        #report the extracted data
        self.temp = {}
        order = 0
        
        for row in ds_warehouses:
            order = order + 1
            print_line = self.x_field(row[8], self.staxsize) + ' ' +\
                   self.x_field(row[9], self.plaxsize) + ' ' +\
                   self.x_field(row[10], place_name) + ' ' +\
                   self.x_field(row[1], 10) + ' ' +\
                   self.x_field(row[0], 5, 'R') + ' ' +\
                   self.x_field(row[2], self.commsize) + ' ' +\
                   self.x_field(row[3], 5, 'R') + ' ' +\
                   self.x_field(row[7], 5, 'R') + ' ' +\
                   self.x_field(row[4], 5, 'R') + ' ' +\
                   self.x_field(row[5], 5, 'R') + ' ' +\
                   self.x_field(row[6], self.classize)
            self.temp[order] = print_line

        #--------------------------------------------------------------------------------------------
        #report the extracted data
        self.print_report (titles = titles,
                           report_id = 'PRWARE',
                           report_name = 'LIST OF WAREHOUSES',
                           Params = Params)
        return                 


    def ldware(self, message):
        """lists warehouse status. sortable by station/place/warehouse or by warehouse id
        """
        if self.show_access(message, 'LDWARE (sort[0/1])', 'R') != 0:
            return        

        #get any sort order
        value, rc = self.extract_field(message, 0, '')
        if rc == 0:
            sort_order = value
        else:
            sort_order = '0'

        # build the column titles
        place_name = 78 - self.staxsize - self.plaxsize - self.commsize - self.classize - 45
        if place_name < 0:
            place_name = 1
        if place_name > 30:
            place_name = 30
        titles = self.x_field('STATION===', self.staxsize) + ' ' +\
                 self.x_field('PLACE=====', self.plaxsize) + ' ' +\
                 self.x_field('INDUSTRY==', 10) + ' ' +\
                 self.x_field('WAREHOUSE=', 5) + ' ' +\
                 self.x_field('CAPY%', 5) + ' ' +\
                 self.x_field('ORDER', 5) + ' ' +\
                 self.x_field('ONWAY', 5) + ' ' +\
                 self.x_field('EMPTY', 5) + ' ' +\
                 self.x_field('LOADS', 5) + ' ' +\
                 self.x_field('TRACK', 5) + ' ' +\
                 self.x_field('USED.', 5) + ' ' +\
                 self.x_field('ROUTING=====', self.curosize)

        #get the extract data
        if sort_order == '1':
            sql = 'select place.station, place.code, warehouse.industry, warehouse.id, '  +\
                  'warehouse.in_storage, warehouse.max_storage, place.track_length, ' +\
                  'warehouse.routing, warehouse.ordered ' +\
                  'from warehouse, place where warehouse.industry = place.industry ' +\
                  'order by place.station, place.code, place.industry, warehouse.id'
        else:
            sql = 'select place.station, place.code, warehouse.industry, warehouse.id, '  +\
                  'warehouse.in_storage, warehouse.max_storage, place.track_length, ' +\
                  'warehouse.routing, warehouse.ordered ' +\
                  'from warehouse, place where warehouse.industry = place.industry ' +\
                  'order by warehouse.id'
            
        count, ds_warehouses = self.db_read(sql, '')
        if count < 0:
            return

        #--------------------------------------------------------------------------------------------
        #report the extracted data
        line_count = 0
        counted = 0
        for row in ds_warehouses:
            industry = row[2]
            warehouse = row[3]
            in_storage = row[4]
            max_storage = row[5]
            track = row[6]
            routing = row[7]
            ordered = row[8]
            
            data = (industry,)
            sql = 'select car.commodity, cartype.length, place.track_length ' +\
                  'from car, place, cartype ' +\
                  'where car.place_id = place.id ' +\
                  'and car.cartype = cartype.cartype ' +\
                  'and place.industry = ?'
            count, ds_cars = self.db_read(sql, data)
            if count < 0:
                return
            empty = 0
            loaded = 0
            car_length = 0
            for car_row in ds_cars:
                car_commodity = car_row[0]
                cartype_length = car_row[1]
                car_length = car_length + cartype_length
                if car_commodity == '':
                    empty = empty + 1
                else:
                    loaded = loaded + 1

            ordered = ordered - empty - loaded                                   #Rev 1

            data = (warehouse, 'I', 'E')                                         #Rev 1
            sql = 'select car.id from car, waybill ' +\
                  'where warehouse = ? and status = ? and type = ? ' +\
                  'and car.carorder = waybill.id'
            onway, dummy = self.db_read(sql, data)
            if onway < 0:
                return
            
            ordered = ordered - onway                                            #Rev 1

            data = (warehouse, 'W')                                              #Rev 1 start
            sql = 'select car.id from car, waybill ' +\
                  'where warehouse = ? and type = ? ' +\
                  'and car.carorder = waybill.id'
            waybills, dummy = self.db_read(sql, data)
            if waybills < 0:
                return
            
            ordered = ordered - waybills                                         #Rev 1 end
                
            if line_count == 0:
                print(titles)
            capacity = int(100 * in_storage/max_storage)
            print(self.x_field(row[0], self.staxsize) + " " +
                   self.x_field(row[1], self.plaxsize) + " " +
                   self.x_field(industry, 10) + " " +
                   self.x_field(warehouse, 5, 'R') + " " +
                   self.x_field(capacity, 5, 'R') + " " +
                   self.x_field(ordered, 5, 'R') + " " +
                   self.x_field(onway, 5, 'R') + " " +
                   self.x_field(empty, 5, 'R') + " " +
                   self.x_field(loaded, 5, 'R') + " " +
                   self.x_field(track, 5, 'R') + " " +
                   self.x_field(car_length, 5, 'R') + " " +
                   self.x_field(routing, self.curosize))
            counted = counted + 1
            line_count = line_count + 1
            if line_count > 20:
                line_count = 0
                reply = raw_input('+')
                if reply == 'x':
                    break
        print(' ** END OF DATA:' + str(counted), ' RECORDS DISPLAYED **')         
        return                   


    def lsware(self, message):
        """lists warehouse details for all warehouses at a station. each warehouse is
        shown over several lines and is a detailed breakdown of the warehouse
        """
        if self.show_access(message, 'LSWARE station', 'R') != 0:
            return        

        #industry------------------------------------------------------------------------------------
        station, rc = self.extract_field(message, 0, 'STATION')
        if rc > 0:
            return

        data = (station,)
        sql = 'select id from station where station = ?'
        count, dummy = self.db_read(sql, data)
        if count < 0:
            return
        if count == 0:
            print('* STATION NOT FOUND')
            return

        #get the extract data
        data = (station,)        
        sql =   'select station.station, station.long_name, ' +\
                'origin.code as o_code, origin.track_length as o_track_length, ' +\
                'origin.name as o_name, origin.loading as o_loading, ' +\
                'dest.station, dest.code, dest.name, dest.unloading, ' +\
                'warehouse.id, warehouse.industry, warehouse.destination, ' +\
                'warehouse.commodity, warehouse.threshold_class, ' +\
                'warehouse.production, warehouse.threshold_goods, ' +\
                'warehouse.max_storage, warehouse.in_storage, warehouse.ordered, ' +\
                'commodity.name, routing.routing, routing.desc ' +\
                'from place origin ' +\
                'left outer join station on station.station = origin.station ' +\
                'left outer join warehouse on warehouse.industry = origin.industry ' +\
                'left outer join place as dest on warehouse.destination = dest.industry ' +\
                'left outer join commodity on warehouse.commodity = commodity.commodity ' +\
                'left outer join routing on routing.routing = warehouse.routing ' +\
                'where origin.station = ? ' +\
                'order by station.station, origin.code '
        count, ds_warehouses = self.db_read(sql, data)
        if count < 0:
            return

        #--------------------------------------------------------------------------------------------
        #report the extracted data
        line_count = 0
        for row in ds_warehouses:
            station       = row[0]
            stax_name     = row[1]
            orig_plax     = row[2]
            orig_track    = row[3]
            orig_name     = row[4]
            orig_load     = row[5]
            dest_stax     = row[6]
            dest_plax     = row[7]
            dest_name     = row[8]
            dest_unload   = row[9]
            ware_id       = row[10]
            ware_industry = row[11]
            ware_dest     = row[12]
            ware_comm     = row[13]
            ware_class    = row[14]
            ware_prod     = row[15]
            ware_goods    = row[16]
            ware_max      = row[17]
            ware_stored   = row[18]
            ware_ordered  = row[19]
            comm_name     = row[20]
            route_code    = row[21]
            route_desc    = row[22]
            
            if line_count == 0:
                print(' ')
                print('STATION:%s STATION NAME:%s' % (station, stax_name))
                print('-------------------------------------------------------------')
            line_count = line_count + 1

            print('PLACE:%s NAME:%-25s TRACK LENGTH:%5d   LOADING:%s' % (orig_plax, orig_name, orig_track, orig_load))
            if ware_id == None:
                print('NO WAREHOUSE ATTCHED TO PLACE')
            else:
                print('DEST:%s PLACE:%s %-41s UNLOADING:%s' % (dest_stax, dest_plax, dest_name, dest_unload))
                print('WAREHOUSE:%5s %-10s SHIPS TO:%-10s SHIPPING:%s %s' % (ware_id, ware_industry, ware_dest, ware_comm, comm_name))
                print('CAR CLASS:%s CUSTOMER ROUTE:%s %s' % (ware_class, route_code, route_desc))
                print('PROD RATE:%5s ORDER AT:%5s STORED:%5s MAX STORE:%5s CARS ORDERED:%5s' % (ware_prod, ware_goods, ware_stored, ware_max, ware_ordered))
            print(' ')

        print(' ** END OF DATA:' + str(count) + ' RECORDS DISPLAYED **')         
        return                   

        

    def Z001_generation_production(self, Flash, Params):
        """checks all warehouses for production
        read all warehouses.  for each warehouse, get the current number of wagons called, as
        we need to see if this changes.  add the production amount to the in_storage amount.  if the
        in_storage amount > maximum, reduce in_storage to maximum.

        work out how many cars have been called for.  this is in_storage/threshold_goods * threshold cars.
        if ordered cars has gone up since last time, change the number of ordered cars and create a
        request for empties on the car order file
        """
        sql = 'select id, industry, commodity, destination, production, threshold_goods, ' +\
              'threshold_cars, threshold_class, max_storage, in_storage, ordered, routing ' +\
              'from warehouse where in_storage < max_storage order by industry, id'
        count, ds_warehouses = self.db_read(sql, '')
        if count < 0:
            return

        for row in ds_warehouses:
            wh_id = row[0]
            industry = row[1]
            commodity = row[2]
            destination = row[3]
            production = row[4]
            threshold_goods = row[5]
            threshold_cars = row[6]
            threshold_class = row[7]
            max_storage = row[8]
            in_storage = row[9]
            ordered = row[10]

            t = (destination,)
            sql = 'select unloading, station, code from place where industry = ?'
            count, ds_dest = self.db_read(sql, t)
            if count < 0:
                return
            for row in ds_dest:
                unloading = row[0]
                d_stax = row[1]
                d_plax = row[2]

            t = (industry,)
            sql = 'select station, code from place where industry = ?'
            count, ds_origin = self.db_read(sql, t)
            if count < 0:
                return
            for row in ds_origin:
                o_stax = row[0]
                o_plax = row[1]
            
            in_storage = in_storage + production
            if in_storage > max_storage:
                in_storage = max_storage
                print(Params.get_date() + ' ' + Params.get_time(),
                      'Z001: INDUSTRY', industry, 'AT MAXIMUM STORAGE', in_storage)

            cars_required = int(in_storage / threshold_goods) * threshold_cars
            if cars_required > ordered:
                to_order = cars_required - ordered
                ordered = cars_required

                sql = 'select loading, clean_cars from commodity where commodity = ?'
                t = (commodity,)
                count, comm = self.db_read(sql, t)
                for row2 in comm:
                    loading = row2[0]
                    clean_cars = row2[1]
                timestamp = Params.get_date() + ' ' + Params.get_time()

                t = (wh_id, 'E', str(to_order), clean_cars, loading,
                     unloading, commodity, industry, destination, 'O', timestamp)
                sql = 'insert into waybill values (null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
                self.db_update(sql, t)
                message = 'INDUSTRY ' + industry + o_stax + '/' + o_plax + ' RAISED REQUEST FOR ' + str(to_order) + ' ' + threshold_class + ' EMPTIES'
                message2 = Params.get_date() + ' ' + Params.get_time() + 'Z001:' + industry + o_stax + '/' + o_plax + 'REQUIRES' + str(to_order) + ' ' + threshold_class + ' EMPTIES TO' + d_stax + '/' + d_plax
                t = (message, )
                Flash.Z003_generate_flash_message(message, Params)
                Flash.flashx(message, Params)
                print(Params.get_date() + ' ' + Params.get_time() + 'Z001:' +
                       industry, o_stax + '/' + o_plax + 'REQUIRES' +
                       str(to_order) + ' ' + threshold_class + ' EMPTIES TO' + d_stax + '/' + d_plax)

            sql = 'update warehouse set in_storage = ?, ordered = ? where id = ?'
            t = (in_storage, ordered, wh_id)
            if self.db_update(sql, t) != 0:
                return
        return
