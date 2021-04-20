# -*- coding: utf-8 -*-
# import sys
import requests
from bs4 import BeautifulSoup
import time
import json
from db_actions import insert_input, get_actual_models, insert_new_product, \
	update_model_price, update_model_size, update_model_navidate
# from traceback import print_exc
from datetime import datetime, timedelta
from loguru import logger
import re


logger.add('debug.log', format="{time} {level}: ({file}:{module} - {line}) >> {message}", level="DEBUG")
logger.add('info.log', format="{time} {level}: ({file}:{module} - {line}) >> {message}", level="INFO")
session = requests.session()
session.trust_env = False
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'}


def load_user_data(pagenum_in, session_in):
	# формирование страницы
	url = 'https://www.yoox.com/RU/shoponline?dept=shoesmen&gender=U&page=' + str(pagenum_in) + \
		'&sort=3&clientabt=SmsMultiChannel_ON%2CSizeIsocode_ON%2CNewDelivery_ON%2CFindYourSize_ON%2CNewPayment_' \
		'ON%2Cfitanalytics_OFF'
	response = session_in.get(url)
	# logger.info(
	# 	str(datetime.now())
	# 	+ ' "Request":"create_request_yoox"\n "Headers":'
	# 	+ str(response.headers)
	# 	+ '\n "Response":'
	# 	+ str(response.status_code)
	# )
	result = BeautifulSoup(response.text, 'html.parser')
	return result


def next_page(text):
	# проверка сопоставления текущей страницы и разрешённой последней
	out = text.find('ul', {'class': 'pagination list-inline pull-right text-center js-pagination'})\
		.find('li', {'class': 'selected-bold'}).text
	#logger.debug(out)
	return out


def prod_grid(text):
	# не используется
	out = text.find('div', {'class': 'col-8-24'})
	#logger.debug(out)
	# print('Finded', out.find('div').text)
	return out is not None


def prod_not_none(text):
	# проверка, не продан ли продукт на странице
	# out = text.find('a')['href']
	out = text.find('a', {'class': 'itemlink'}).get('href')
	#logger.debug(out)
	return out is not None


def list_add_to_dict(list_in):
	for value in list_in:
		print(value)


params = '{"yoox_id":1}'
data = json.loads(params)
app_id = data["yoox_id"]
# os.open('./params.txt','r') as parameters

pagenum = 1

# os.remove('./yoox_prod_export.log')
logger.debug('Start models')
all_items = get_actual_models(app_id)
logger.debug('all_items finish')
# получаем список продуктов из БД по текущему приложению, чтобы не было путанницы
while True:
	checker = []  # возможно бесполезно
	# print(all_items['11791485OO'])
	data = load_user_data(pagenum, session)  # загрузка новой страницы
	#logger.debug(data)
	try:
		if int(next_page(data)) == pagenum:  # проверяем наличие новой страницы
			grid = data.find('div', {'id': 'itemsGrid'})  # сетка с продуктами
			item_in_grid = grid.findAll('div', {'class': 'col-8-24'})
			#logger.debug(item_in_grid)
			# поиск на всей странице в инфе о продукте
			for item in item_in_grid:
				# export_line = '' начинаем экспорт файл
				prod_id = (item('div')[0]['data-current-cod10'])
				logger.info(prod_id)
				# код продукта, используется для поиска в словаре
				if prod_not_none(item):
					# если новый prod_id отсутствует в all_items, обрабатываем полностью с нуля
					#all_items[prod_id] = item('a')[0]['href']
					brand = item.find('div', {'class': 'brand font-bold text-uppercase'}).text
					logger.debug(brand)
					# export_line += prod_id + '|' + brand + '|'
					picture = item('img')[0]['data-original']
					if item.find('div', {'class': 'title'}):  # есть ли описание у товара
						model = item('div', {'class': 'title'})[0].text
					else:
						model = prod_id
					# export_line += description + '|'
					logger.debug(model)
					price_find = item.find('div', {'class': 'price'}).findAll('span')
					# выборка цены, если со скидкой, выдаётся обе цены
					if price_find[0]['class'][0] == 'fullprice':
						price = price_find[0].text
					else:
						price = price_find[0].text + ';' + price_find[1].text
					logger.debug(price)
					size_find = item.find('div', {'class': 'size text-light'}).findAll('span')
					# выборка размеров, в конце запятая
					# insert_new_product(app_id, prod_id, brand, model, price, size_find, picture)
					size = ''
					for size_values in size_find:
						size += size_values.text + ';'
					logger.debug(size)
					if prod_id not in all_items:
						sql_result = insert_new_product(app_id, prod_id, brand, model, price, size, picture)
						logger.debug(sql_result)
						logger.info(prod_id + ' if finish')
					else:
						if datetime.now() > datetime.strptime(all_items.get(prod_id).get('navi_date')[:19], "%Y-%m-%d %H:%M:%S"):
							if ''.join([c for c in price if c in '1234567890']) != all_items.get(prod_id).get('price'):
								logger.debug('Update price')
								sql_result = update_model_price(prod_id, app_id, price)
							else:
								sql_result = update_model_navidate(prod_id, app_id)
							logger.debug(sql_result)
							sql_result = update_model_size(prod_id, size, 1)
							logger.debug(sql_result)
							logger.info(prod_id + ' else finish')
						else:
							logger.info(prod_id + ' is too new')
		else:
			logger.info('Finished, restarting')
			pagenum = 1
	except AttributeError as error:
		logger.error(error.args)
	except Exception:
		logger.error(str(pagenum) + ' ' + str(ValueError))
		logger.error(item)
		# print(so_far)
		# error_export.write(time.strftime("%Y%m%d-%H%M%S"))
		# error_export.write(':ERROR:')
		# error_export.write(str(pagenum))
		# error_export.write('/n')
	else:
		logger.info('::PASS::' + str(pagenum))
	finally:
		pagenum += 1

