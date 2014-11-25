'''
Database  Unit used to create database and calendar.  

Model Operations Processing System. Copyright Brian Fairbairn 2009-2010.  Licenced under the EUPL.  
You may not use this work except in compliance with the Licence.  You may obtain a copy of the
Licence at http://ec.europa.eu/idabc/eupl or as attached with this application (see Licence file).  
Unless required by applicable law or agreed to in writing, software distributed under the Licence 
is distributed on an 'AS IS' basis WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressed 
or implied. See the Licence governing permissions and limitations under the Licence.
'''

import sqlite3


def create_database(mops_directory):
    """connects to a database if the database exists.  If a database does not exist at that
    location then it creates it.  Database name is fixed as mops.db
    """
    cxn = sqlite3.connect(mops_directory + 'mops.db')
    c = cxn.cursor()

    #--------------------------------------------------------------------------------------------
    #determine whether the database needs to be seeing whether a link succeeds
    try:
        sql = 'select id from railroad'
        c.execute(sql, '')
        c.close()
    except:
        sql = '''create table locotype    (id integer primary key autoincrement,
                                           locotype text,
                                           name text,
                                           power_type text,
                                           haulage integer,
                                           fuel_capacity integer,
                                           fuel_rate integer,
                                           maint_interval integer,
                                           works_time integer,
                                           weight integer,
                                           length integer,
                                           oper_mode text)'''
        c.execute(sql)
        sql = '''create table locomotive  (id integer primary key autoincrement,
                                           loco text,
                                           locotype text,
                                           fuel integer,
                                           weight integer,
                                           time_to_maint integer,
                                           time_in_maint integer,
                                           is_powered text,
                                           railroad text,
                                           home_station text,
                                           station text,
                                           place_id integer,
                                           train text)'''
        c.execute(sql)
        sql = '''create table railroad    (id integer primary key autoincrement,
                                           railroad text,
                                           name text)'''
        c.execute(sql)
        sql = '''create table loading     (id integer primary key autoincrement,
                                           loading text,
                                           desc text,
                                           can_load text,
                                           can_unload text)'''
        c.execute(sql)
        sql = '''create table carclass    (id integer primary key autoincrement,
                                           carclass text,
                                           name text)'''
        c.execute(sql)
        sql = '''create table cartype     (id integer primary key autoincrement,
                                           cartype text,
                                           name text,
                                           length integer,
                                           oper_mode text,
                                           capacity integer,
                                           unladen_weight integer,
                                           loading text,
                                           unloading text,
                                           carclass text)'''
        c.execute(sql)
        sql = '''create table commodity   (id integer primary key autoincrement,
                                           commodity text,
                                           name text,
                                           loading text,
                                           loading_rate integer,
                                           unloading_rate integer,
                                           clean_cars text)'''
        c.execute(sql)
        sql = '''create table area        (id integer primary key autoincrement,
                                           area text,
                                           name text,
                                           railroad text)'''
        c.execute(sql)
        sql = '''create table stationtype (id integer primary key autoincrement,
                                           stationtype text,
                                           desc text)'''
        c.execute(sql)
        sql = '''create table car         (id integer primary key autoincrement,
                                           car text,
                                           cartype text,
                                           time_to_maint integer,
                                           time_in_maint integer,
                                           carclass text,
                                           railroad text,
                                           commodity text,
                                           home_station text,
                                           station text,
                                           place_id integer,
                                           train text,
                                           block text,
                                           weight_loaded integer,
                                           is_attached_set text,
                                           clean_dirty text,
                                           carorder integer)'''
        c.execute(sql)
        sql = '''create table station     (id integer primary key autoincrement,
                                           station text,
                                           short_name text,
                                           long_name text,
                                           area text,
                                           stationtype text,
                                           alias text)'''
        c.execute(sql)
        sql = '''create table place       (id integer primary key autoincrement,
                                           name text,
                                           station text,
                                           code text,
                                           track_length integer,
                                           industry text,
                                           place_type text,
                                           loading text,
                                           unloading text,
                                           car_id text)'''
        c.execute(sql)
        sql = '''create table route       (id integer primary key autoincrement,
                                           route text,
                                           name text,
                                           status text,
                                           default_direction text)'''
        c.execute(sql)
        sql = '''create table section     (id integer primary key autoincrement,
                                           route text,
                                           section integer,
                                           depart_station text,
                                           arrive_station text)'''
        c.execute(sql)
        sql = '''create table schedule    (id integer primary key autoincrement,
                                           schedule text,
                                           route text,
                                           name text,
                                           class text,
                                           status text,
                                           run_days text,
                                           orig_station text,
                                           dest_station text,
                                           direction text)'''
        c.execute(sql)
        sql = '''create table timings     (id integer primary key autoincrement,
                                           section text,
                                           schedule text,
                                           depart_station text,
                                           arrive_station text,
                                           planned_depart text,
                                           planned_arrive text)'''
        c.execute(sql)
        sql = '''create table instructions(id integer primary key autoincrement,
                                           route text,
                                           schedule text,
                                           station text,
                                           instruction text)'''
        c.execute(sql)
        sql = '''create table train       (id integer primary key autoincrement,
                                           train text,
                                           type text,
                                           station text,
                                           status text,
                                           schedule text)'''
        c.execute(sql)
        sql = '''create table running     (id integer primary key autoincrement,
                                           train text,
                                           timings integer,
                                           depart_station text,
                                           arrive_station text,
                                           est_depart text,
                                           est_arrive text,
                                           act_depart text,
                                           act_arrive text)'''
        c.execute(sql)
        sql = '''create table warehouse   (id integer primary key autoincrement,
                                           industry text,
                                           commodity text,
                                           destination text,
                                           production integer,
                                           threshold_goods integer,
                                           threshold_cars integer,
                                           threshold_class integer,
                                           max_storage integer,
                                           in_storage integer,
                                           ordered integer,
                                           routing text)'''
        c.execute(sql)
        sql = '''create table routing     (id integer primary key autoincrement,
                                           routing text,
                                           desc text)'''
        c.execute(sql)
        sql = '''create table waybill     (id integer primary key autoincrement,
                                           warehouse integer,
                                           type text,
                                           requires text,
                                           clean_cars text,
                                           loading text,
                                           unloading text,
                                           commodity text,
                                           origin text,
                                           destination text,
                                           status text,
                                           timestamp text)'''
        c.execute(sql)
        sql = '''create table flash       (id integer primary key autoincrement,
                                           flash integer,
                                           message text,
                                           user text,
                                           timer integer)'''
        c.execute(sql)
        sql = '''create table user        (id integer primary key autoincrement,
                                           user text,
                                           name text,
                                           passcode text,
                                           user_type text,
                                           is_signed_on text,
                                           has_access_disabled text,
                                           get_new_password text)'''
        c.execute(sql)
        sql = '''create table calendar    (id integer primary key autoincrement,
                                           day text,
                                           month text,
                                           year text,
                                           holiday text,
                                           current text,
                                           dow text)'''
        c.execute(sql)
        sql = '''create table parameter   (id integer primary key autoincrement,
                                           name text,
                                           value text)'''
        c.execute(sql)

        cxn.commit()
        print('MOPS DATABASE CREATED')
    cxn.close()
    return



def create_calendar(mops_directory):
    """creates a calendar from 1 January 1950 to 31 december 2049.  calendar is created in
    five year chunks - avoids making the database too big
    """

    s_start_year = raw_input('Enter start year 1950/1955/1960/../2010 ==> ')
    start_year = int(s_start_year)

    t = (start_year,)
    sql = 'select id from calendar where year = ?'

    cxn = sqlite3.connect(mops_directory + 'mops.db')
    c = cxn.cursor()
    c.execute(sql, t)
    array = c.fetchall()
    c.close
    cxn.close
    if len(array) != 0:
        print('Calendar already created on database for this time period')
        return
    
    yearcount   = 0
    gen_julian = 1
    leap_year = False
    gen_mmm    = 'JAN'
    gen_dd     = 1
    gen_yyyy   = start_year

    
    if start_year == 1950:
        gen_dow = 'SUN'
    elif start_year == 1955:
        gen_dow = 'SAT'
    elif start_year == 1960:
        gen_dow = 'FRI'
    elif start_year == 1965:
        gen_dow = 'FRI'
    elif start_year == 1970:
        gen_dow = 'THU'
    elif start_year == 1975:
        gen_dow = 'WED'
    elif start_year == 1980:
        gen_dow = 'TUE'
    elif start_year == 1985:
        gen_dow = 'TUE'
    elif start_year == 1990:
        gen_dow = 'MON'
    elif start_year == 1995:
        gen_dow = 'SUN'
    elif start_year == 2000:
        gen_dow = 'SUN'
    elif start_year == 2005:
        gen_dow = 'SAT'
    elif start_year == 2010:
        gen_dow = 'FRI'
    else:
        gen_dow = 'THU'
        
    
    while yearcount < 5:
        sgen_dd = str(gen_dd)
        sgen_dd = sgen_dd.rjust(2,'0')

        t = (sgen_dd, gen_mmm, str(gen_yyyy), '', '', gen_dow)
        sql = 'insert into calendar values (null, ?, ?, ?, ?, ?, ?)'
        
        cxn = sqlite3.connect(mops_directory + 'mops.db')
        c = cxn.cursor()
        c.execute(sql, t)
        cxn.commit()
        c.close
        cxn.close
        
        if gen_yyyy % 400 == 0:
            leap_year = True
        elif gen_yyyy % 100 == 0:
            leap_year = False
        elif gen_yyyy % 4 == 0:
            leap_year = True
        else:
            leap_year = False
            
        gen_dd = gen_dd + 1
        gen_julian = gen_julian + 1

        if gen_mmm == 'JAN' and gen_dd > 31:
            gen_mmm = 'FEB'
            gen_dd = 1
        elif gen_mmm == 'FEB' and gen_dd > 28 and not leap_year:
            gen_mmm = 'MAR'
            gen_dd = 1
        elif gen_mmm == 'FEB' and gen_dd > 29 and leap_year:
            gen_mmm = 'MAR'
            gen_dd = 1
        elif gen_mmm == 'MAR' and gen_dd > 31:
            gen_mmm = 'APR'
            gen_dd = 1
        elif gen_mmm == 'APR' and gen_dd > 30:
            gen_mmm = 'MAY'
            gen_dd = 1
        elif gen_mmm == 'MAY' and gen_dd > 31:
            gen_mmm = 'JUN'
            gen_dd = 1
        elif gen_mmm == 'JUN' and gen_dd > 30:
            gen_mmm = 'JUL'
            gen_dd = 1
        elif gen_mmm == 'JUL' and gen_dd > 31:
            gen_mmm = 'AUG'
            gen_dd = 1
        elif gen_mmm == 'AUG' and gen_dd > 31:
            gen_mmm = 'SEP'
            gen_dd = 1
        elif gen_mmm == 'SEP' and gen_dd > 30:
            gen_mmm = 'OCT'
            gen_dd = 1
        elif gen_mmm == 'OCT' and gen_dd > 31:
            gen_mmm = 'NOV'
            gen_dd = 1
        elif gen_mmm == 'NOV' and gen_dd > 30:
            gen_mmm = 'DEC'
            gen_dd = 1
        elif gen_mmm == 'DEC' and gen_dd > 31:
            gen_mmm = 'JAN'
            gen_dd = 1
            print('CALENDAR GENERATED FOR ' + str(gen_yyyy))
            gen_yyyy = gen_yyyy + 1
            gen_julian = 1
            yearcount = yearcount + 1
        else:
            pass

        if gen_dow == 'SUN':
            gen_dow = 'MON'
        elif gen_dow == 'MON':
            gen_dow = 'TUE'
        elif gen_dow == 'TUE':
            gen_dow = 'WED'
        elif gen_dow == 'WED':
            gen_dow = 'THU'
        elif gen_dow == 'THU':
            gen_dow = 'FRI'
        elif gen_dow == 'FRI':
            gen_dow = 'SAT'
        elif gen_dow == 'SAT':
            gen_dow = 'SUN'

    return
