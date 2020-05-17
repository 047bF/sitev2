# -*- coding: utf-8 -*-
import sys
import datetime
import requests
from bs4 import BeautifulSoup
import os
from db_actions import  insert_input

def load_all_products (link):
	# Var numpage
	session = requests.session()
	session.trust_env = False
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'}
	request = session.get(link, headers = headers)
	#print(request)
	return request.text

def check_for_products(text):
	soup = BeautifulSoup(text, 'html.parser')
	#поиск в теге meta, по content = который в двойных ковычках
	all_products = soup.find('div', {'id': 'asos-product'})
	return all_products is not None

def check_for_sizes(text):
	print(text)
	#поиск в теге meta, по content = который в двойных ковычках
	avalible = text.find('div', {'class'})
	print(avalible)
	return avalible is not None

#перед стартом удаляем старый файл с экспортом
os.remove('./asos_prod_export.log')
os.remove('./asos_error_export.txt')
checker = []
with open('./asos_error_export.txt', 'a') as error_export: #вывод из else
	with open('./asos_prod_export.log', 'a') as export_file: #основой вывод всей инфы
		while True:
			with open('./asos_page_export.log', 'r') as input_file: #чтение из base всех ссылок
				try:
					for link in input_file.read().split():
						page = load_all_products(link)
						if check_for_products(page):
							soup = BeautifulSoup(page, 'html.parser') 		#поиск основной секции с продуктами
							prod_hero = soup.find('div', {'class' :'schema-org'})	#укорачиваем объект поиска, чтобы дальше искать быстрее
							prod_id = prod_hero.find('span', {'itemprop': 'productID'}).text #выборка ID продукта
							if prod_id not in checker:
								print(datetime.datetime.now(), '::PASS::', prod_id)
								checker.append(prod_id)
								prod_brand = prod_hero.find('span', {'itemprop': 'brand'}).find('span').text	#выборка бренда продукта
								prod_price = prod_hero.find('span', {'itemprop': 'price'}).text	#выборка цены продукта
							#добавить проверку на цену со скидкой
								prod_desc = prod_hero.find_all('span', {'itemprop': 'name'})[1].text	#выборка описания продукта (find_all), и показываем второй текст из списка
							#размеры не ищутся( if check_for_sizes(soup):
								export_line = prod_id+'|'+prod_brand.encode().decode('utf-8', 'ignore')+'|'+prod_desc.encode().decode('utf-8','ignore')+'|'+prod_price+'|size'
								insert_input('asos_read',export_line)
								export_line += '/n '
								export_file.write(export_line)
						else:
							print('page missing')
							error_export.write('product-')
							error_export.write(prod_id)
							error_export.write(';')
				except Exception:
					print(datetime.datetime.now(),":ERROR:", link)
					error_export.write(datetime.datetime.now())
					error_export.write(':ERROR:')
					error_export.write(page)
					error_export.write('/n')
				else:
					print(datetime.datetime.now(),'::PASS::All pages read')