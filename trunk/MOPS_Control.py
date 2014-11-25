'''
Control: contains the main running routine for MOPS

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.

Changes:
Rev 1.  Added extract to TriMOPS in background section (start/stop extract)
        Removed duplicate definition of MOPS_Param
        Removed unused variables
        Added 2 menu options for backing up database and removing old prints
        Batch command processing re-installed
        Renamed Z008 to show schedules being cancelled
        Added MOPS Help into the list of included modules
        Changed Z005 to handle both Empty and Waybill Orders, removed Z007
'''
def MOPS():
    """MOPS  
    Main control loop - startup and handles input commands
    1.  Print copyright; locate the file that contains the data directory 
    2.  Load Command lists
    3.  Sign-on user
    4.  Load parameter data
    5.  If MOPS in maintenance mode, then only let supervisors in
    6.  Load the data objects
    7.  Check status of MOPS, determine startup or background console
        - if MOPS is started
            Normal User Mode 
        - if MOPS is not started (selection menu)
            Background Mode (starts MOPS console runs background tasks)
            or Maintenance Mode (runs with no background mode)
            or Validate and check databases
    8.  Main command loop
    9.  Terminate on completion
    """
    import time
    import sys
    import platform
    import shutil                                                         #Rev 1
    import os                                                             #Rev 1
    
    import MOPS_Commands
    import MOPS_Misc
    import MOPS_Param
    import MOPS_Database
    import MOPS_Area
    import MOPS_Calendar
    import MOPS_CarClass
    import MOPS_CarType
    import MOPS_Car
    import MOPS_Commodity
    import MOPS_Flash
    import MOPS_Help                                                      #Rev 1
    import MOPS_Instruction
    import MOPS_Loading
    import MOPS_Loco
    import MOPS_LocoType
    import MOPS_Order
    import MOPS_Place
    import MOPS_Railroad
    import MOPS_Route
    import MOPS_Routing
    import MOPS_Schedule
    import MOPS_Section
    import MOPS_Station
    import MOPS_StationType
    import MOPS_Timings
    import MOPS_Train
    import MOPS_User
    import MOPS_Warehouse


    #STEP 1 Print copyright; locate the file that contains the data directory
    version_details  = str(sys.version_info[0]) + '.' + str(sys.version_info[1])
    print('  ------------------------------------------------------------------------------')
    print('> MOPS v1.01 Copyright Brian Fairbairn 2009/2010           ')
    print('> Licensed under the EUPL.  See Licence file for details  ')
    print('> Python version details: v' + version_details + ' on ' + platform.system())
    command = 'xxxxxx'
    mops_directory = MOPS_Misc.directory_location()
    if mops_directory == '*****':
        return
    print('> Location of data files: ' + mops_directory)
    print('  ------------------------------------------------------------------------------')
    MOPS_Database.create_database(mops_directory)


    #STEP 2 Load Command lists
    commands = {}
    commands = MOPS_Commands.load_commands(commands)


    #STEP 3 Sign-on user.  need the users object to sign on
    User = MOPS_User.cUsers (mops_directory)
    uid, access = User.Z028_sign_on()
    User.uid    = uid
    User.access = access
    if uid == '********':
        print('INVALID SIGNON; LOGON ABANDONED')
        return

    #STEP 4 Load parameter data
    #Create and load the parameter object - we need to see if MOPS is started.
    #Some of the key data is held in the PARAM file so load this early
    Params  = MOPS_Param.cParams(uid, access, mops_directory)
    User.rr = Params.get_rr_name()
    print('* SYSTEM STATUS: ' + str(Params.get_mops_status()) + ' *')


    #STEP 5 if mops is in maintenance mode then only supervisors can get in
    if Params.get_mops_status() == 'STOPPED':
        print('****************************************************************************')
        print('* MOPS running in Maintenance Mode.  No background tasks are running.      *')
        if access != 'S':
            print('*    >>> MOPS HAS BEEN DISABLED WHILE MAINTENANCE TAKES PLACE <<<          *')
            print('****************************************************************************')
            command = 'QUIT'
            User.Z029_sign_off()
            print('MOPS AUTOMATICALLY SIGNING OFF')
            return
        else:
            print('****************************************************************************') 


    #STEP 6 Create and load the data objects
    Area         = MOPS_Area.cAreas                  (Params, uid, access, mops_directory)
    Calendar     = MOPS_Calendar.cCalendars          (Params, uid, access, mops_directory)
    CarType      = MOPS_CarType.cCarTypes            (Params, uid, access, mops_directory)
    CarClass     = MOPS_CarClass.cCarClasses         (Params, uid, access, mops_directory)
    Car          = MOPS_Car.cCars                    (Params, uid, access, mops_directory)
    Commodity    = MOPS_Commodity.cCommodities       (Params, uid, access, mops_directory)
    Flash        = MOPS_Flash.cFlashes               (Params, uid, access, mops_directory)
    Instruction  = MOPS_Instruction.cInstructions    (Params, uid, access, mops_directory)
    Loading      = MOPS_Loading.cLoading             (Params, uid, access, mops_directory)
    Loco         = MOPS_Loco.cLoco                   (Params, uid, access, mops_directory)
    LocoType     = MOPS_LocoType.cLocoTypes          (Params, uid, access, mops_directory)
    Order        = MOPS_Order.cOrders                (Params, uid, access, mops_directory)
    Place        = MOPS_Place.cPlaces                (Params, uid, access, mops_directory)
    Railroad     = MOPS_Railroad.cRailroads          (Params, uid, access, mops_directory)
    Route        = MOPS_Route.cRoutes                (Params, uid, access, mops_directory)
    Routing      = MOPS_Routing.cRoutings            (Params, uid, access, mops_directory)
    Schedule     = MOPS_Schedule.cSchedules          (Params, uid, access, mops_directory)
    Section      = MOPS_Section.cSections            (Params, uid, access, mops_directory)
    Station      = MOPS_Station.cStations            (Params, uid, access, mops_directory)
    StationType  = MOPS_StationType.cStationTypes    (Params, uid, access, mops_directory)
    Timings      = MOPS_Timings.cTimings             (Params, uid, access, mops_directory)
    Train        = MOPS_Train.cTrains                (Params, uid, access, mops_directory)
    Warehouse    = MOPS_Warehouse.cWarehouses        (Params, uid, access, mops_directory)

    #STEP 7 Check status of MOPS, determine startup or background console
    #This section checks that MOPS is up and running.  If not, then there are 
    #choices to be made - see menu below for details 
    choice = '0'
    
    if Params.get_mops_status() == 'STOPPED':
        while choice != '2':
            print('')
            print('MOPS NOT STARTED.  PLEASE SELECT:')
            print('    1 Start Background tasks for MOPS on this console')
            print('    2 Enter MOPS in Maintenance Mode (no background tasks)')
            print('    3 Run batch file load (.TXT from data directory')
            print('    4 Create Calendar for 5-year period (1950/1955/1960.../2010)')
            print('    5 Create back-up of database called MOPS.bak')             #Rev 1
            print('    6 Purge old MOPS print output files')                      #Rev 1
            print('    9 Quit (this will terminate this session)')
            choice = raw_input('==> ') #deprecated in Python 3, use input()

            if choice == '1':  #Run background tasks on this console
                Params.start_mops()
                print('... background task running on this console ...')
                print('this session will stop when MOPS  is terminated ')
                print('')
                
                print(Params.get_date() + ' ' + Params.get_time())
                Train.Z040_trimop(Params)                                          #Rev 1
                while Params.get_mops_status() == 'STARTED':
                    event = Params.Z000_clock_advance()
                    if event == 'minute' or event == 'hour' or event == 'day':
                        print("running car loading")
                        Car.Z015_car_loading(Flash, Params)
                        print("running car loading selection")
                        Car.Z013_select_car_for_loading(Params)
                        print("running E waybills")
                        Car.Z005_waybill(Flash, Params, 'E')
                        print("running W waybills")
                        Car.Z005_waybill(Flash, Params, 'W')
                        print("running loco fuel usage")
                        Loco.Z014_set_loco_fuel_usage(Params)
                    if event == 'hour' or event == 'day':
                        print("running time")
                        print(Params.get_date() + ' ' + Params.get_time())
                        Warehouse.Z001_generation_production(Flash, Params)
                        print("running flash expiry")
                        Flash.Z006_expire_flash_messages()
                        print("running loco refuleing")   
                        Loco.Z022_refuel_loco(Params)
                        print("running car works")   
                        Car.Z012_works_cars(Flash, Params)
                        print("running loco works")
                        Loco.Z023_works_locos(Flash, Params)
                    if event == 'day':
                        print("re-activating schedules")
                        Schedule.Z018_set_schedules_to_active(Flash, Params)
                        print("canceling schedules")  
                        Schedule.Z008_set_schedules_to_cancel(Flash, Params)         #Rev 1
                        print("running loco countdown")
                        Loco.Z002_maintain_loco_countdown(Flash, Params)
                        print("running car countdown")  
                        Car.Z011_maintain_car_countdown(Flash, Params)  
                    time.sleep(5)

                Train.Z041_trimop_shutdown(Params)                                    #Rev 1
                print('MOPS Background task terminated')
                User.Z029_sign_off()
                return

            if choice == '2':  #Enter Maintenance Mode - no background tasks
                print('***********************************************************************')
                print('* MOPS running in Maintenance Mode.  No background tasks are running. *')
                print('***********************************************************************')
                
            if choice == '3':  #Load Batch File
                file = raw_input('ENTER FILENAME > ')
                filename = mops_directory + file + '.txt'
                try:
                    f = open(filename, 'r')
                    for line in f:
                        input_text = ''
                        line = line.upper()   #convert all to upper case
                        line = line.strip()
                        command = line[0:6]      #get the command
                        if len(line) > 6:
                            s = len(line)            #we need the data part of the string
                            s = (s - 7) * -1         #so ignore the first seven characters
                            input_data = line[s:]    #remainder is the data
                            input_data = input_data.strip()
                        else:
                            input_data = ''
                        try:
                            print('>>>')
                            print('>>> ' + line)
                            exec(commands[command])
                        except KeyError:
                            if not (command == '----->' or command.strip() == ''):
                                print(command + ': ERROR PROCESSING COMMAND IN BATCH ***************************')
                    f.close
                except IOError:
                    print('No such file exists...')
                except:
                    print('Error processing command in batch.  Load terminated.')                  #Ver 1

            if choice == '4':  #create calendar
                MOPS_Database.create_calendar(mops_directory)
                
            if choice == '5':  #create backup of database                       #Rev 1
                current_database = mops_directory + 'MOPS.db'
                backup_database = mops_directory + 'backup_database_MOPS.db'
                shutil.copy(current_database, backup_database)
                print('MOPS database copied to: backup_database_MOPS.db')
                print('')
                
            if choice == '6':  #purge old print files                           #Rev 1
                print('Deleting old MOPS Print extract files')
                file_names = os.listdir(mops_directory)
                for old_file in file_names:
                    if old_file[0:13] == 'MOPS_EXTRACT_':
                        print('--->', old_file)
                        os.remove(mops_directory + old_file)

            if choice == '9':  #Quit MOPS
                User.Z029_sign_off()
                print('MOPS SESSION TERMINATED BY USER')
                return                

    print(str(Params.get_rr_name()) + ': WELCOME TO MOPS')
    print(' ')
    print('SIGN-ON IS COMPLETE: TYPE <QUIT> OR <EXIT> TO END SESSION')


    #STEP 8 Main command loop
    while command != 'QUIT':           #until the user quits
        print(' ')   

        #look up any message for the user that have not yet been displayed
        Flash.Z004_check_flash_required()

        input_text = raw_input('>')    #deprecated in Python 3, use input()
        input_text = str.upper(input_text) #like mainframes use upper case only
        input_text = input_text.strip()
        command = input_text[0:6]          #the command is the first 6 chars
        if len(input_text) > 6:
            s = len(input_text)            #we need the data part of the string
            s = (s - 7) * -1               #so ignore the first seven characters
            input_data = input_text[s:]
        else:
            input_data  = ''

        print(Params.get_time() + ' ' + MOPS_Commands.get_helper(command) + ' BY ' + uid.strip() + ' ON ' + Params.get_date())

        if (command == 'QUIT' or command == 'EXIT' or command == 'STOP'):
            User.Z029_sign_off()
            print('MOPS EXIT COMMAND RECEIVED FOR SESSION')
            return
        
        #check that MOPS is still available prior to the command
        if Params.get_mops_status() != 'STARTED':
            if access != 'S':
                print('MOPS HAS BEEN SHUT DOWN.  YOUR SESSION WILL NOW TERMINATE')
                break
            else:
                print('* MOPS running in Maintenance Mode.  No background tasks are running. *')
        
        #execute the command from the command list
        try:
            exec(commands[command])
        except KeyError:
            pass

            
    #STEP 9 Terminate on completion
    User.Z029_sign_off()
    print('MOPS SESSION TERMINATED BY USER')
    return
