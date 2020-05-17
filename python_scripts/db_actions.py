#!/usr/bin/python
# -*- coding: utf-8 -*- 
import psycopg2
from config import config
from datetime import datetime 

def insert_input(user,raw_str,picture):
    """ insert a new vendor into the vendors table """
    sql = """INSERT INTO input(navi_date,navi_user,in_raw,in_pic)
             VALUES(current_timestamp, %s, %s, %s) RETURNING in_id;"""
    conn = None
    in_id = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql,(user,raw_str,picture))
        # get the generated id back
        in_id = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
 
    return in_id

def insert_site_temp(site, user, raw_str, sil_unique):
    sql = """INSERT INTO site_import_links(site_site_id,sil_link,smst_smst_id,navi_user, sil_unique)
             VALUES(%s, %s, %s, %s, %s) RETURNING sil_id;"""
    conn = None
    sil_id = None
    smst_smst_id = 1
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(sql,(site, raw_str, smst_smst_id,user,sil_unique))
        sil_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return sil_id

def select_site_temp(site,status):
    sql = """SELECT sil_id, sil_link, sil_unique from site_import_links
            WHERE 1=1 
            AND site_site_id = %s
            AND smst_smst_id in %s;""" #select for dismiss all records for each site and dont add them double
    conn = None
    sil_id = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        #print(sql,(site,status,))
        cur.execute(sql,(site,status,))
        select_records = cur.fetchall()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return select_records

def update_site_temp(sil_id, status):
    sql = """UPDATE site_import_links
            SET smst_smst_id = %s
            WHERE sil_id = %s;""" #UPDATE
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(sql,(status,sil_id,))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return sil_id