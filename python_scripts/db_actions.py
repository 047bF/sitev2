#!/usr/bin/python
# -*- coding: utf-8 -*- 
import psycopg2
from config import config
from sqlalchemy import MetaData, Table, Column, Integer, String, create_engine, insert, text, VARCHAR, exc
import json
# from datetime import datetime
from sqlalchemy.ext.declarative import DeclarativeMeta

metadata = MetaData()
new_products = Table('new_products', metadata,
                               Column('new_prod_id', Integer, primary_key=True),
                               Column('site_site_id', Integer),
                               Column('product_id', VARCHAR),
                               Column('brand', VARCHAR),
                               Column('model', VARCHAR),
                               Column('price', VARCHAR),
                               Column('sizes_array', VARCHAR),
                               Column('picture_link', VARCHAR))


class AlchemyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)  # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)


engine = create_engine('postgresql://db_user:db_pass@localhost/db_v2')  # , echo=True)
engine.connect()
metadata.create_all(engine)

def insert_input(user, raw_str, picture):
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
        cur.execute(sql, (user, raw_str, picture))
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
        cur.execute(sql, (site, raw_str, smst_smst_id, user, sil_unique))
        sil_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return sil_id


def select_site_temp(site, status):
    sql = """SELECT sil_id, sil_link, sil_unique from site_import_links
            WHERE 1=1 
            AND site_site_id = %s
            AND smst_smst_id in %s;"""  # select for dismiss all records for each site and dont add them double
    conn = None
    # sil_id = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # print(sql,(site,status,))
        cur.execute(sql, (site, status, ))
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
            WHERE sil_id = %s;"""  # UPDATE
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(sql, (status, sil_id, ))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return sil_id


def get_actual_models(f_site_id):
    dict_from_query = {}
    with engine.connect() as connection:
        sql = text("SELECT mod_site_uniq, navi_date + '1 hour'::interval as navi_date"
                   ", price, sale_price FROM model_histories "
                   "WHERE site_site_id = :site and avail_avail_id = 1")
        sql_query = connection.execute(sql, site=f_site_id).fetchall()
        for item in [dict(row) for row in sql_query]:
            dict_value = {'price': str(item.get('price')) + str(item.get('sale_price')).replace('None', ''),
                          'navi_date':  str(item.get('navi_date'))}
            dict_from_query[item.get('mod_site_uniq')] = dict_value
    return dict_from_query


def insert_new_product(f_site_id, f_product, f_brand, f_model, f_price, f_size, f_picture):
    connection = engine.connect()
    try:
        insert_query = new_products.insert().values(site_site_id=f_site_id, product_id=f_product, brand=f_brand,
                                                    model=f_model, price=f_price, sizes_array=f_size, picture_link=f_picture)
        result = connection.execute(insert_query)
        return result
    except exc.SQLAlchemyError as e:
        print(type(e))
        print(e)


def update_model_price(f_mod_site_uniq, f_site_id, f_price):
    with engine.begin() as connection:
        sql = text("select model_histories_update_price(:s_mod_site_uniq, :s_site_id ,:s_price)")
        sql_query=connection.execute(sql, s_mod_site_uniq=f_mod_site_uniq, s_site_id=f_site_id, s_price=f_price).fetchall()
        for row in sql_query:
            return (row[0])


    """connection = engine.connect()
    try:
        sql = text("select model_histories_update_price(:s_mod_site_uniq, :s_site_id ,:s_price)")
        result = connection.execute(sql, s_mod_site_uniq=f_mod_site_uniq, s_site_id=f_site_id, s_price=f_price)
    except exc.SQLAlchemyError as e:
        print(type(e))
        return e
    finally:
        for row in result:
            return(row[0])"""


"""
    with engine.connect() as connection:
    print(insert_query)
    print(result)
            sql = text(
                 "INSERT INTO new_products (site_site_id, product_id, brand, model, price, sizes_array, picture_link) "
                 "VALUES (:site_id, :product_id, :brand, :model, :price, :sizes, :picture)")
            result = connection.execute(sql, {"site_id": f_site_id, "product_id": f_product, "brand": f_brand,
                                             "picture": f_picture, "model": f_model, "price": f_price, "sizes": f_size})                                               
"""


def update_one_param(f_product, f_param_name, f_param_value):
    if f_param_name == 'size' or f_param_name == 'price':
        with engine.begin() as connection:
            sql = text(
                "INSERT INTO to_update (mod_site_uniq, param_name, param_value) "
                "VALUES (:product, :param_name, :param_value")
            sql_query = connection.execute(sql, product=f_product, param_name=f_param_name, param_value=f_param_value)
        return sql_query


def update_model_size(f_mod_site_uniq, f_sizes, f_gen_id):
    with engine.begin() as connection:
        sql = text("select many_size_insert_or_update(:s_mod_site_uniq, :s_sizes, :s_gen_id)")
        sql_query = connection.execute(sql, s_mod_site_uniq=f_mod_site_uniq, s_sizes=f_sizes, s_gen_id=f_gen_id).fetchall()
        for row in sql_query:
            return row[0]


def update_model_navidate(f_mod_site_uniq, f_site_id):
    with engine.begin() as connection:
        sql = text("update model_histories set navi_date = current_timestamp where site_site_id = :s_site_id "
                   "and mod_site_uniq = :s_mod_site_uniq and avail_avail_id = 1")
        sql_query = connection.execute(sql, s_mod_site_uniq=f_mod_site_uniq, s_site_id=f_site_id)
        return sql_query

