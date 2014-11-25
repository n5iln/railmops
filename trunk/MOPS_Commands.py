'''
Commands: Basic module to handle all commands.  Commands for mops are driven by one-line
exec statements; these exec statements are held in a dictionary.

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
    Rev 1 Added Params as a parameter to CXSCHD for triMOPS
          Added Params as a parameter to ADROUT for default direction
          Added Params to LINEUP for passenger car checking
          Added Params to LICONS for passenger car checking
'''

def load_commands(commands):
    """This contains a list of commands to be exec'd in the main loop.  The key
    is the input command and the value is the line to be executed (generally a 
    class method).
    
    Command structure:
        verb data
        where verb is (almost always) a 6-figure word which translates to a 
        class method and data is a set of parameters for the class method 
        delimited by semi-colons
    Verb structure
        special verbs are available which equate to specific commands and these
        are described in the user manual or can be see below.

        general verbs are constructed on the following basis:
        chars 1 + 2  AD  - Add a new item
                     CH  - Change existing item
                           (addittional changes will be C*)
                     DX  - Delete item
                     LI  - List items (to screen)
                           (additional list verions will be LA, LB etc)
                     LX  - unformatted list versions
                     PA  - Print items (to file)
                           (additional print version will be PA, PB etx)
                     PX  - unformatted print versions (for .csv files)
                     XX  - Supervisor command functions
        chars 3-6 type of data being updated (can also use char 6)
                AREA - Maintain Areas
                USER - Maintain users
                TYPE - Maintain Stax Types
                STAX - Maintain Stax
                PARM - Parameter values
    """
    #areas
    commands['ADAREA'] = 'Area.adarea(input_data)\n'
    commands['CHAREA'] = 'Area.charea(input_data)\n'
    commands['DXAREA'] = 'Area.dxarea(input_data)\n'
    commands['LIAREA'] = 'Area.liarea(input_data)\n'
    commands['LXAREA'] = 'Area.dump_to_screen()\n'
    commands['PRAREA'] = 'Area.prarea(input_data, Params)\n'
    commands['PXAREA'] = 'Area.extract_to_file(Params)\n'
    #calendar
    commands['HOLIDX'] = 'Calendar.holidx(input_data)\n'
    commands['LICALX'] = 'Calendar.licalx(input_data)\n'
    #car
    commands['ADCARX'] = 'Car.adcarx(input_data)\n'
    commands['ACARXB'] = 'Car.acarxb(input_data)\n'
    commands['ACARXS'] = 'Car.acarxs(input_data)\n'
    commands['CARXAT'] = 'Car.carxat(input_data)\n'
    commands['CHCARX'] = 'Car.chcarx(input_data)\n'
    commands['CLEANX'] = 'Car.cleanx(input_data)\n'
    commands['MAINTC'] = 'Car.maintc(input_data)\n'
    commands['CXCARS'] = 'Car.cxcars(input_data)\n'
    commands['DXCARX'] = 'Car.dxcarx(input_data)\n'
    commands['LACARS'] = 'Car.lacars(input_data)\n'
    commands['LICARS'] = 'Car.licars(input_data)\n'
    commands['LMTCAR'] = 'Car.lmtcar(input_data)\n'
    commands['LONWAY'] = 'Car.lonway(input_data)\n'
    commands['LXCARS'] = 'Car.dump_to_screen()\n'
    commands['MTYORD'] = 'Car.mtyord(input_data)\n'
    commands['PRCARS'] = 'Car.prcars(input_data, Params)\n'
    commands['PXCARS'] = 'Car.extract_to_file(Params)\n'
    commands['CARXSP'] = 'Car.carxsp(input_data)\n'
    commands['XCARXB'] = 'Car.xcarxb(input_data)\n'
    commands['XCARXS'] = 'Car.xcarxs(input_data)\n'
    #carclass
    commands['ADCLAS'] = 'CarClass.adclas(input_data)\n'
    commands['CHCLAS'] = 'CarClass.chclas(input_data)\n'
    commands['DXCLAS'] = 'CarClass.dxclas(input_data)\n'
    commands['LICLAS'] = 'CarClass.liclas(input_data)\n'
    commands['LXCLAS'] = 'CarClass.dump_to_screen()\n'
    commands['PRCLAS'] = 'CarClass.prclas(input_data, Params)\n'
    commands['PXCLAS'] = 'CarClass.extract_to_file(Params)\n'
    #cartype
    commands['ADCART'] = 'CarType.adcart(input_data)\n'
    commands['CHCART'] = 'CarType.chcart(input_data)\n'
    commands['DXCART'] = 'CarType.dxcart(input_data)\n'
    commands['LICART'] = 'CarType.licart(input_data)\n'
    commands['LXCART'] = 'CarType.dump_to_screen()\n'
    commands['PRCART'] = 'CarType.prcart(input_data, Params,)\n'
    commands['PXCART'] = 'CarType.extract_to_file(Params)\n'
    #commodities
    commands['ADCOMM'] = 'Commodity.adcomm(input_data)\n'
    commands['CHCOMM'] = 'Commodity.chcomm(input_data)\n'
    commands['DXCOMM'] = 'Commodity.dxcomm(input_data)\n'
    commands['LICOMM'] = 'Commodity.licomm(input_data)\n'
    commands['LXCOMM'] = 'Commodity.dump_to_screen()\n'
    commands['PRCOMM'] = 'Commodity.prcomm(input_data, Params)\n'
    commands['PXCOMM'] = 'Commodity.extract_to_file(Params)\n'
    #flash
    commands['FLASHX'] = 'Flash.flashx(input_data, Params)\n'
    #help
    commands['ABOUT']  = 'MOPS_Help.about()\n'
    commands['HELP']   = 'MOPS_Help.help()\n'
    commands['ASSIST'] = 'MOPS_Commands.assist()\n'
    #instruction
    commands['ADINST'] = 'Instruction.adinst(input_data)\n'
    commands['DXINST'] = 'Instruction.dxinst(input_data)\n'
    #loading
    commands['ADLOAD'] = 'Loading.adload(input_data)\n'
    commands['CHLOAD'] = 'Loading.chload(input_data)\n'
    commands['DXLOAD'] = 'Loading.dxload(input_data)\n'
    commands['LILOAD'] = 'Loading.liload(input_data)\n'
    commands['LXLOAD'] = 'Loading.dump_to_screen()\n'
    commands['PRLOAD'] = 'Loading.prload(input_data, Params)\n'
    commands['PXLOAD'] = 'Loading.extract_to_file(Params)\n'
    #loco
    commands['ADLOCO'] = 'Loco.adloco(input_data)\n'
    commands['FUELXX'] = 'Loco.fuelxx(input_data)\n'
    commands['CHLOCO'] = 'Loco.chloco(input_data)\n'
    commands['MAINTL'] = 'Loco.maintl(input_data)\n'
    commands['POWERX'] = 'Loco.powerx(input_data)\n'
    commands['DXLOCO'] = 'Loco.dxloco(input_data)\n'
    commands['LOCOAT'] = 'Loco.locoat(input_data)\n'
    commands['LOCOSP'] = 'Loco.locosp(input_data)\n'
    commands['LILOCO'] = 'Loco.liloco(input_data)\n'
    commands['LSLOCO'] = 'Loco.lsloco(input_data)\n'
    commands['LXLOCO'] = 'Loco.dump_to_screen()\n'
    commands['PRLOCO'] = 'Loco.prloco(input_data, Params)\n'
    commands['PSLOCO'] = 'Loco.psloco(input_data, Params)\n'
    commands['PXLOCO'] = 'Loco.extract_to_file(Params)\n'
    #loco type
    commands['ADLOCT'] = 'LocoType.adloct(input_data)\n'
    commands['CHLOCT'] = 'LocoType.chloct(input_data)\n'
    commands['DXLOCT'] = 'LocoType.dxloct(input_data)\n'
    commands['LILOCT'] = 'LocoType.liloct(input_data)'
    commands['LXLOCT'] = 'LocoType.dump_to_screen()\n'
    commands['PRLOCT'] = 'LocoType.prloct(input_data, Params)\n'
    commands['PXLOCT'] = 'LocoType.extract_to_file(Params)\n'
    #order
    commands['LEMPTY'] = 'Order.lempty(input_data)'
    commands['LORDER'] = 'Order.lorder(input_data)'
    commands['LXORDR'] = 'Order.dump_to_screen()\n'
    commands['DEMPTY'] = 'Order.dempty(input_data)'
    commands['PEMPTY'] = 'Order.pempty(input_data, Params)\n'
    commands['PXORDR'] = 'Order.extract_to_file(Params)\n'
    #parameter
    commands['CHPARM'] = 'Params.chparm(input_data)\n'
    commands['CSPEED'] = 'Params.cspeed(input_data)\n'
    commands['LIPARM'] = 'Params.liparm(input_data)\n'
    commands['PRPARM'] = 'Params.prparm(input_data, Params)\n'
    commands['LXPARM'] = 'Params.dump_to_screen()\n'
    commands['PXPARM'] = 'Params.extract_to_file(Params)\n'
    commands['SETTIM'] = 'Params.settim(input_data)\n'
    commands['XXSTOP'] = 'Params.xxstop()\n'
    #place
    commands['ADPLAX'] = 'Place.adplax(input_data)\n'
    commands['ADINDY'] = 'Place.adindy(input_data)\n'
    commands['CHPLAX'] = 'Place.chplax(input_data)\n'
    commands['CHINDY'] = 'Place.chindy(input_data)\n'
    commands['DXPLAX'] = 'Place.dxplax(input_data)\n'
    commands['DXINDY'] = 'Place.dxindy(input_data)\n'
    commands['LIPLAX'] = 'Place.liplax(input_data)\n'
    commands['LIGEOG'] = 'Place.ligeog(input_data)\n'
    commands['LXPLAX'] = 'Place.dump_to_screen()\n'
    commands['PRPLAX'] = 'Place.prplax(input_data, Params)\n'
    commands['PRGEOG'] = 'Place.prgeog(input_data, Params)\n'
    commands['PXPLAX'] = 'Place.extract_to_file(Params)\n'
    #railroad
    commands['ADRAIL'] = 'Railroad.adrail(input_data)\n'
    commands['CHRAIL'] = 'Railroad.chrail(input_data)\n'
    commands['DXRAIL'] = 'Railroad.dxrail(input_data)\n'
    commands['LIRAIL'] = 'Railroad.lirail(input_data)\n'
    commands['LXRAIL'] = 'Railroad.dump_to_screen()\n'
    commands['PRRAIL'] = 'Railroad.prrail(input_data, Params)\n'
    commands['PXRAIL'] = 'Railroad.extract_to_file(Params)\n'
    #route
    commands['ADROUT'] = 'Route.adrout(input_data, Params)\n'                   #Rev 1
    commands['CHROUT'] = 'Route.chrout(input_data)\n'
    commands['DXROUT'] = 'Route.dxrout(input_data)\n'
    commands['LIROUT'] = 'Route.lirout(input_data)\n'
    commands['LXROUT'] = 'Route.dump_to_screen()\n'
    commands['PRROUT'] = 'Route.prrout(input_data, Params)\n'
    commands['UNPUBL'] = 'Route.unpubl(input_data)\n'
    commands['PUBLSH'] = 'Route.publsh(input_data)\n'
    commands['PXROUT'] = 'Route.extract_to_file(Params)\n'
    commands['VALIDR'] = 'Route.validr(input_data)\n'
    #routing code
    commands['ADCURO'] = 'Routing.adcuro(input_data)\n'
    commands['CHCURO'] = 'Routing.chcuro(input_data)\n'
    commands['DXCURO'] = 'Routing.dxcuro(input_data)\n'
    commands['LICURO'] = 'Routing.licuro(input_data)\n'
    commands['LXCURO'] = 'Routing.dump_to_screen()\n'
    commands['PRCURO'] = 'Routing.prcuro(input_data, Params)\n'
    commands['PXCURO'] = 'Routing.extract_to_file(Params)\n'
    #schedule
    commands['ADSCHD'] = 'Schedule.adschd(input_data)\n'
    commands['CHSCHD'] = 'Schedule.chschd(input_data)\n'
    commands['CPSCHD'] = 'Schedule.cpschd(input_data)\n'
    commands['DXSCHD'] = 'Schedule.dxschd(input_data)\n'
    commands['CXSCHD'] = 'Schedule.cxschd(input_data, Params)\n'
    commands['XCTIVE'] = 'Schedule.xctive(input_data)\n'
    commands['LISCHD'] = 'Schedule.lischd(input_data)\n'
    commands['LSSCHD'] = 'Schedule.lsschd(input_data)\n'
    commands['LXSCHD'] = 'Schedule.dump_to_screen()\n'
    commands['ACTIVE'] = 'Schedule.active(input_data)\n'
    commands['PRSCHD'] = 'Schedule.prschd(input_data, Params)\n'
    commands['PXSCHD'] = 'Schedule.extract_to_file(Params)\n'
    commands['PRTABL'] = 'Schedule.prtabl(input_data, user_type, user_id)\n'
    commands['PXTABL'] = 'Schedule.pxtabl(input_data, user_type, user_id)\n'
    #section
    commands['ADSECT'] = 'Section.adsect(input_data)\n'
    commands['DXSECT'] = 'Section.dxsect(input_data)\n'
    commands['LXSECT'] = 'Section.dump_to_screen()\n'
    commands['LSROUT'] = 'Section.lsrout(input_data)\n'
    commands['LDROUT'] = 'Section.ldrout(input_data)\n'
    commands['PDROUT'] = 'Section.pdrout(input_data, Params)\n'
    commands['PXSECT'] = 'Section.extract_to_file(Params)\n'
    #stations
    commands['ADSTAX'] = 'Station.adstax(input_data, Params)\n'
    commands['CHSTAX'] = 'Station.chstax(input_data, Params)\n'
    commands['DXSTAX'] = 'Station.dxstax(input_data)\n'
    commands['LISTAX'] = 'Station.listax(input_data)\n'
    commands['LXSTAX'] = 'Station.dump_to_screen()\n'
    commands['PRSTAX'] = 'Station.prstax(input_data, Params)\n'
    commands['PXSTAX'] = 'Station.extract_to_file(Params)\n'
    #station types
    commands['ADSTAT'] = 'StationType.adstat(input_data)\n'
    commands['CHSTAT'] = 'StationType.chstat(input_data)\n'
    commands['DXSTAT'] = 'StationType.dxstat(input_data)\n'
    commands['LISTAT'] = 'StationType.listat(input_data)\n'
    commands['LXSTAT'] = 'StationType.dump_to_screen()\n'
    commands['PRSTAT'] = 'StationType.prstat(input_data, Params)\n'
    commands['PXSTAT'] = 'StationType.extract_to_file(Params)\n'
    #timings
    commands['ADTIMS'] = 'Timings.adtims(input_data)\n'
    commands['CHTIMS'] = 'Timings.chtims(input_data)\n'
    commands['TIMING'] = 'Timings.timing(input_data)\n'
    commands['LDTIMS'] = 'Timings.ldtims(input_data)\n'
    commands['PRTIMS'] = 'Timings.prtims(input_data, Params)\n'
    commands['PXTIMS'] = 'Timings.extract_to_file(Params)\n'
    #train
    commands['UTRAIN'] = 'Train.utrain(input_data, Params)\n'
    commands['STRAIN'] = 'Train.strain(input_data, Params)\n'
    commands['ETRAIN'] = 'Train.etrain(input_data, Params)\n'
    commands['ALOCOT'] = 'Train.alocot(input_data)\n'
    commands['ACARXT'] = 'Train.acarxt(input_data)\n'
    commands['LTRAIN'] = 'Train.ltrain(input_data, Flash, Params)\n'
    commands['LINEUP'] = 'Train.lineup(input_data, Params)\n'                        #Rev 1
    commands['REPORT'] = 'Train.report(input_data, Params)\n'
    commands['TTRAIN'] = 'Train.ttrain(input_data, Flash, Params)\n'
    commands['XLOCOT'] = 'Train.xlocot(input_data)\n'
    commands['XCARXT'] = 'Train.xcarxt(input_data)\n'
    commands['TRAINS'] = 'Train.trains(input_data)\n'
    commands['LICONS'] = 'Train.licons(input_data, Params)\n'                        #Rev 1
    commands['PRCONS'] = 'Train.prcons(input_data, Params)\n' 
    #users
    commands['ADUSER'] = 'User.aduser(input_data)\n'
    commands['CHPASS'] = 'User.chpass(uid)\n'
    commands['CHUSER'] = 'User.chuser(input_data)\n'
    commands['DXUSER'] = 'User.dxuser(input_data)\n'
    commands['EDUSER'] = 'User.eduser(input_data)\n'
    commands['LIUSER'] = 'User.liuser(input_data)\n'
    commands['LXUSER'] = 'User.dump_to_screen()\n'
    commands['PRUSER'] = 'User.pruser(input_data, Params)\n'
    commands['PXUSER'] = 'User.extract_to_file(Params)\n'
    commands['RESETP'] = 'User.resetp(input_data)\n'
    #warehouses    
    commands['ADWARE'] = 'Warehouse.adware(input_data)\n'
    commands['CHWARE'] = 'Warehouse.chware(input_data)\n'
    commands['CPWARE'] = 'Warehouse.cpware(input_data)\n'
    commands['DXWARE'] = 'Warehouse.dxware(input_data)\n'
    commands['LIWARE'] = 'Warehouse.liware(input_data)\n'
    commands['LDWARE'] = 'Warehouse.ldware(input_data)\n'
    commands['LSWARE'] = 'Warehouse.lsware(input_data)\n'
    commands['LXWARE'] = 'Warehouse.dump_to_screen()\n'
    commands['PRWARE'] = 'Warehouse.prware(input_data, Params)\n'
    commands['PXWARE'] = 'Warehouse.extract_to_file(Params)\n'
    return commands


def load_helper(helper):
    """Loads short descriptions about commands into an array
    """
    #areas
    helper['ADAREA'] = 'ADD AREA'
    helper['CHAREA'] = 'CHANGE AREA'
    helper['DXAREA'] = 'DELETE AREA'
    helper['LIAREA'] = 'LIST AREAS'
    helper['LXAREA'] = 'SHOW AREAS FILE'
    helper['PRAREA'] = 'PRINT AREAS'
    helper['PXAREA'] = 'EXPORT AREAS'
    #calendar
    helper['HOLIDX'] = 'SET HOLIDAY'
    helper['LICALX'] = 'LIST NEXT 10 DAYS'
    #car
    helper['ADCARX'] = 'ADD CAR DETAIL'
    helper['ACARXB'] = 'ALLOCATE CAR TO BLOCK'
    helper['ACARXS'] = 'ALLOCATE CAR TO SET'
    helper['CARXAT'] = 'LOCATE CAR AT STATION'
    helper['CHCARX'] = 'CHANGE CAR DETAILS'
    helper['CLEANX'] = 'SET CAR TO EMPTY/CLEAN'
    helper['MAINTC'] = 'CHANGE CAR MAINTENANCE STATE'
    helper['CXCARS'] = 'CHANGE CAR LOCATION'
    helper['DXCARX'] = 'DELETE CAR'
    helper['LICARS'] = 'LIST CARS'
    helper['LACARS'] = 'REPORT CARS BY STATUS'
    helper['LMTCAR'] = 'REPORT UNALLOCATED EMPTY CARS'
    helper['LONWAY'] = 'REPORT EMPTIES EN ROUTE'
    helper['LXCARS'] = 'SHOW CARS FILE'
    helper['MTYORD'] = 'ALLOCATE EMPTY TO ORDER'
    helper['PRCARS'] = 'PRINT CARS'
    helper['PXCARS'] = 'EXPORT CARS'
    helper['CARXSP'] = 'SPOT CAR'
    helper['XCARXB'] = 'REMOVE CAR FROM BLOCK'
    helper['XCARXS'] = 'REMOVE CAR FROM SET'
    #carclass
    helper['ADCLAS'] = 'ADD CAR CLASSIFICATION'
    helper['CHCLAS'] = 'CHANGE CAR CLASSSIFICATION'
    helper['DXCLAS'] = 'DELETE CAR CLASSIFICATION'
    helper['LICLAS'] = 'LIST CAR CLASSIFICATIONS'
    helper['LXCLAS'] = 'SHOW CAR CLASSIFICATIONS FILE'
    helper['PRCLAS'] = 'PRINT CAR CLASSIFICATIONS'
    helper['PXCLAS'] = 'EXPORT CAR CLASSIFICATIONS'
    #carbuild
    helper['ADCART'] = 'ADD CAR TYPE'
    helper['CHCART'] = 'CHANGE CAR TYPE'
    helper['DXCART'] = 'DELETE CAR TYPE'
    helper['LICART'] = 'LIST CAR TYPES'
    helper['LXCART'] = 'SHOW CAR TYPES FILE'
    helper['PRCART'] = 'PRINT CAR TYPES'
    helper['PXCART'] = 'EXPORT CAR TYPES'
    #commodities
    helper['ADCOMM'] = 'ADD COMMODITY'
    helper['CHCOMM'] = 'CHANGE COMMODITY'
    helper['DXCOMM'] = 'DELETE COMMODITY'
    helper['LICOMM'] = 'LIST COMMODITIES'
    helper['LXCOMM'] = 'SHOW COMMODITIES FILE'
    helper['PRCOMM'] = 'PRINT COMMODITIES'
    helper['PXCOMM'] = 'EXPORT COMMODITIES'
    #flash
    helper['FLASHX'] = 'FLASH MESSAGE'
    #help
    helper['HELP']   = 'GENERAL HELP'
    helper['ABOUT']  = 'ABOUT MOPS'
    helper['ASSIST'] = 'LIST AVAILABLE COMMANDS'
    #instruction
    helper['ADINST'] = 'ADD INSTRUCTION'
    helper['DXINST'] = 'DELETE INSTRUCTION'
    #loading
    helper['ADLOAD'] = 'ADD LOADING DEFINITIONS'
    helper['CHLOAD'] = 'CHANGE LOADING DEFINITIONS'
    helper['DXLOAD'] = 'DELETE LOADING DEFINITION'
    helper['LILOAD'] = 'LIST LOADING DEFINITIONS'
    helper['LXLOAD'] = 'SHOW LOADING DEFINITIONS'
    helper['PRLOAD'] = 'PRINT LOADING DEFINITIONS'
    helper['PXLOAD'] = 'EXPORT LOADING DEFINITIONS'
    #loco
    helper['ADLOCO'] = 'ADD LOCOMOTIVE'
    helper['FUELXX'] = 'CHANGE LOCO FUEL STATE'
    helper['CHLOCO'] = 'CHANGE LOCOMOTIVE'
    helper['MAINTL'] = 'CHANGE LOCO MAINTENANCE STATE'
    helper['POWERX'] = 'CHANGE LOCO POWER STATE'
    helper['DXLOCO'] = 'DELETE LOCOMOTIVE'
    helper['LILOCO'] = 'LIST LOCOMOTIVES'
    helper['LOCOAT'] = 'LOCATE LOCO AT STATION'
    helper['LXLOCO'] = 'SHOW LOCOMOTIVE FILE'
    helper['PRLOCO'] = 'PRINT LOCOMOTIVES'
    helper['PXLOCO'] = 'EXPORT LOCOMOTIVES'
    helper['LOCOSP'] = 'SPOT LOCO'
    helper['LSLOCO'] = 'LIST LOCOMOTIVE DETAILS'
    helper['PSLOCO'] = 'PRINT LOCOMOTIVE DETAILS'
    #loco type
    helper['ADLOCT'] = 'ADD LOCOMOTIVE TYPE'
    helper['CHLOCT'] = 'CHANGE LOCOMOTIVE TYPE'
    helper['DXLOCT'] = 'DELETE LOCOMOTVE TYPE'
    helper['LILOCT'] = 'LIST LOCOMOTIVE TYPES'
    helper['LXLOCT'] = 'SHOW LOCOMOTIVE TYPES'
    helper['PRLOCT'] = 'PRINT LOCOMOTIVE TYPES'
    helper['PXLOCT'] = 'EXPORT LOCOMOTIVE TYPES'
    #order
    helper['LEMPTY'] = 'LIST EMPTY CAR REQUESTS'
    helper['LORDER'] = 'LIST EMPTY AND WAYBILL REQUESTS'
    helper['DEMPTY'] = 'DETAIL EMPTY CAR REQUESTS'
    helper['LXORDR'] = 'SHOW ORDERS FILE'
    helper['PEMPTY'] = 'REPORT EMPTY CAR REQUESTS'
    helper['PXORDR'] = 'EXPORT ORDERS FILE'
    #parameter
    helper['CHPARM'] = 'CHANGE PARAMETER'
    helper['CSPEED'] = 'SET MOPS CLOCK SPEED'
    helper['LIPARM'] = 'LIST PARAMETERS'
    helper['PRPARM'] = 'REPORT PARAMETERS'
    helper['LXPARM'] = 'SHOW PARAMETERS'
    helper['PXPARM'] = 'EXPORT PARAMETERS'
    helper['SETTIM'] = 'SET MOPS DATE AND TIME'
    helper['XXSTOP'] = 'STOP MOPS'
    #place
    helper['ADPLAX'] = 'ADD PLACE'
    helper['CHPLAX'] = 'CHANGE PLACE'
    helper['DXPLAX'] = 'DELETE PLACE'
    helper['ADINDY'] = 'ADD INDUSTRY'
    helper['CHINDY'] = 'CHANGE INDUSTRY'
    helper['DXINDY'] = 'DELETE INDUSTRY'
    helper['LIPLAX'] = 'LIST PLACES'
    helper['LXPLAX'] = 'SHOW PLACES FILE'
    helper['PRPLAX'] = 'PRINT PLACES'
    helper['PRGEOG'] = 'PRINT GEOGRAPHY'
    helper['LIGEOG'] = 'PRINT GEOGRAPHY'
    helper['PXPLAX'] = 'EXPORT PLACES'
    #railroad
    helper['ADRAIL'] = 'ADD RAILROAD'
    helper['CHRAIL'] = 'CHANGE RAILROAD'
    helper['DXRAIL'] = 'DELETE RAILROAD'
    helper['LIRAIL'] = 'LIST RAILROADS'
    helper['LXRAIL'] = 'SHOW RAILROAD FILE'
    helper['PRRAIL'] = 'PRINT RAILROADS'
    helper['PXRAIL'] = 'EXPORT RAILROADS'
    #route
    helper['ADROUT'] = 'ADD ROUTE'
    helper['CHROUT'] = 'CHANGE ROUTE NAME'
    helper['DXROUT'] = 'DELETE ROUTE'
    helper['LIROUT'] = 'LIST ALL ROUTES'
    helper['LXROUT'] = 'SHOW ROUTES FILE'
    helper['PRROUT'] = 'PRINT ALL ROUTES'
    helper['UNPUBL'] = 'SET PUBLISHED ROUTE TO DRAFT'
    helper['PUBLSH'] = 'PUBLISH ROUTE'
    helper['PXROUT'] = 'EXPORT ALL ROUTES'
    helper['VALIDR'] = 'VALIDATE ROUTE'
    #routing code
    helper['ADCURO'] = 'ADD CUSTOMER ROUTING INFORMATION'
    helper['CHCURO'] = 'CHANGE CUSTOMER ROUTING INFORMATION'
    helper['DXCURO'] = 'DELETE CUSTOMER ROUTING INFORMATION'
    helper['LICURO'] = 'LIST CUSTOMER ROUTING INFORMATION'
    helper['LXCURO'] = 'SHOW CUSTOMER ROUTINGS FILE'
    helper['PRCURO'] = 'PRINT CUSTOMER ROUTING INFORMATION'
    helper['PXCURO'] = 'EXPORT ROUTINGS'
    #schedule
    helper['ADSCHD'] = 'ADD SCHEDULE'
    helper['CHSCHD'] = 'CHANGE SCHEDULE'
    helper['CPSCHD'] = 'COPY SCHEDULE'
    helper['DXSCHD'] = 'DELETE SCHEDULE'
    helper['CXSCHD'] = 'CANCEL SCHEDULE'
    helper['ACTIVE'] = 'ACTIVATE SCHEDULE'
    helper['XCTIVE'] = 'SET SCHEDULE INACTIVE'
    helper['LISCHD'] = 'LIST ALL SCHEDULES'
    helper['LSSCHD'] = 'LIST ACTIVE/RUNNING SCHEDULES'
    helper['LXSCHD'] = 'SHOW SCHEDULES FILE'
    helper['PRSCHD'] = 'PRINT ALL SCHEDULES'
    helper['PRTABL'] = 'PRINT TIMETABLE'
    helper['PUBLIS'] = 'PUBLISH SCHEDULE'
    helper['PXSCHD'] = 'EXPORT ALL SCHEDULES'
    helper['PXTABL'] = 'EXPORT TIMETABLE'
    #section
    helper['ADSECT'] = 'ADD ROUTE SECTION'
    helper['DXSECT'] = 'DELETE ROUTE SECTION'
    helper['LDROUT'] = 'LIST DETAIL FOR SELECTED ROUTE'
    helper['LSROUT'] = 'LIST SECTIONS FOR ROUTE'
    helper['LXSECT'] = 'SHOW ALL SECTIONS'
    helper['PDROUT'] = 'PRINT DETAIL FOR SELECTED ROUTE'
    helper['PXSECT'] = 'EXPORT SECTIONS FOR ALL ROUTES'
    #stations
    helper['ADSTAX'] = 'ADD STATION'
    helper['CHSTAX'] = 'CHANGE STATION'
    helper['DXSTAX'] = 'DELETE STATION'
    helper['LISTAX'] = 'LIST STATIONS'
    helper['LXSTAX'] = 'SHOW STATIONS DATA'
    helper['PRSTAX'] = 'PRINT STATIONS'
    helper['PXSTAX'] = 'EXPORT STATIONS'
    #station types
    helper['ADSTAT'] = 'ADD STATION TYPE'
    helper['CHSTAT'] = 'CHANGE STATION TYPE'
    helper['DXSTAT'] = 'DELETE STATION TYPE'
    helper['LISTAT'] = 'LIST STATION TYPES'
    helper['PXSTAT'] = 'EXPORT STATION TYPES'
    helper['LXSTAT'] = 'SHOW STATION TYPE DATA'
    helper['PRSTAT'] = 'PRINT STATION TYPES'
    #timings
    helper['ADTIMS'] = 'ADD SCHEDULE TIMINGS'
    helper['CHTIMS'] = 'CHANGE SCHEDULE TIMINGS'
    helper['TIMING'] = 'LIST TIMINGS FOR SELECTED SCHEDULE'
    helper['LDTIMS'] = 'LIST TIMING RECORD DETAILS FOR SELECTED SCHEDULE'
    helper['PRTIMS'] = 'PRINT TIMINGS FOR SELECTED SCHEDULE'
    helper['PXTIMS'] = 'EXPORT TIMINGS FOR ALL SCHEDULES'
    #train
    helper['UTRAIN'] = 'SET UNSCHEDULED TRAIN'
    helper['STRAIN'] = 'SET SCHEDULED TRAIN'
    helper['ETRAIN'] = 'SET EXTRA TRAIN'
    helper['ACARXT'] = 'ALLOCATE CAR TO TRAIN'
    helper['ALOCOT'] = 'ALLOCATE LOCO TO TRAIN'
    helper['LTRAIN'] = 'START TRAIN AT LATER ORIGIN'
    helper['LINEUP'] = 'REPORT LINE-UP'
    helper['REPORT'] = 'REPORT TRAIN'
    helper['TTRAIN'] = 'TERMINATE TRAIN'
    helper['XLOCOT'] = 'REMOVE LOCO FROM TRAIN'
    helper['XCARXT'] = 'REMOVE CAR FROM TRAIN'
    helper['TRAINS'] = 'LIST RUNNING TRAINS'
    helper['LICONS'] = 'REPORT CONSIST'
    helper['PRCONS'] = 'PRINT CONSIST'
    #users
    helper['ADUSER'] = 'ADD USER'
    helper['CHPASS'] = 'CHANGE PASSWORD'
    helper['CHUSER'] = 'CHANGE USER'
    helper['DXUSER'] = 'DELETE USER'
    helper['EDUSER'] = 'ENABLE/DISABLE USER'
    helper['LIUSER'] = 'LIST USERS'
    helper['LXUSER'] = 'SHOW USER DATA'
    helper['PRUSER'] = 'PRINT USERS'
    helper['PXUSER'] = 'EXPORT USER DATA'
    helper['RESETP'] = 'RESET PASSWORD'
    #warehouses    
    helper['ADWARE'] = 'ADD WAREHOUSE'
    helper['CHWARE'] = 'CHANGE WAREHOUSE DETAILS'
    helper['CPWARE'] = 'CHANGE PRODUCTION AT WAREHOUSE'
    helper['DXWARE'] = 'DELETE WAREHOUSE'
    helper['LIWARE'] = 'LIST WAREHOUSES'
    helper['LDWARE'] = 'LIST WAREHOUSE DETAILS'
    helper['LSWARE'] = 'WAREHOUSES AT STATIONS'
    helper['LXWARE'] = 'SHOW WAREHOUSE DATA'
    helper['PRWARE'] = 'PRINT WAREHOUSES'
    helper['PXWARE'] = 'EXPORT WAREHOUSES'
    #action
    helper['QUIT']   = 'EXIT MOPS'
    helper['EXIT']   = 'EXIT MOPS'
    return helper


def assist():
    """Provides a sorted list (by command name) of all the commands on the system
    with a short description of what the command does
    """
    i = 0
    commands = {}
    helpers = {}
    commands = load_commands(commands)
    helpers = load_helper(helpers)
    listed = list(commands.keys())
    listed.sort()
    for entry in listed:
        i = i + 1
        if i > 23:
            dummy = raw_input(' ... HIT ENTER TO CONTINUE')
            i = 0
        try:
            print(entry + ' ' + helpers[entry])
        except:
            print(entry)
    print(' ... END OF LIST ...')
    

def get_helper(command):
    """Gets the helper (short description) information for a given command
    """
    desc = ''
    helpers = {}
    helpers = load_helper(helpers)
    try:
        desc = helpers[command]
    except:
        desc = 'NOT FOUND'
    return desc    
