# -*- coding: utf-8 -*-
import sys
import requests
from bs4 import BeautifulSoup
import os
import datetime
from db_actions import insert_input

session = requests.session()
session.trust_env = False
headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
	}

def load_user_data(pagenum, session):
	#формирование страницы
	url = 'https://www.yoox.com/RU/shoponline?dept=shoesmen&gender=U&page='+ str(pagenum) + '&sort=3&clientabt=SmsMultiChannel_ON%2CSizeIsocode_ON%2CNewDelivery_ON%2CFindYourSize_ON%2CNewPayment_ON%2Cfitanalytics_OFF'
	request = session.get(url).text
	request = BeautifulSoup(request, 'html.parser')
	#print(url)
	return request

def next_page(text):
	#проверка сопоставления текущей страницы и разрешённой последней
	out = text.find('ul', {'class': 'pagination list-inline pull-right text-center js-pagination'}).find('li', {'class':'selected-bold'}).text
	return out

def prod_grid (text):
	#не используется
	out = text.find('div', {'class': 'col-8-24'})
	#print('Finded', out.find('div').text)
	return out is not None

def prod_not_none(text):
	#проверка, не продан ли продукт на странице
	out = text.find('a', {'class':'itemlink'}).find('span')
	return out is not None

os.remove('./yoox_prod_export.log')
pagenum = 1
links_exp = {}
with open('./yoox_error_export.txt', 'a') as error_export: #вывод из else
	with open('./yoox_prod_export.log', 'a') as export_file: #основой вывод всей инфы
		while True:
			checker = []
			data = load_user_data(pagenum, session)
			try:
				if int(next_page(data)) == pagenum:
					items = data.find('div', {'id': 'itemsGrid'})
					so_far = items.findAll('div', {'class': 'col-8-24'})
					#поиск на всей странице в инфе о продукте
					for n in so_far:
						export_line = '' #начинаем экспорт файл
						#код продукта, используется для поиска в словаре
						prod_id = (n('div')[0]['data-current-cod10']) 
						if prod_not_none(n):
							if prod_id not in links_exp:
								#ссылка на продукт
								links_exp[n('div')[0]['data-current-cod10']]=n('a')[0]['href'] 
								#берём бренд
								export_line += prod_id + '|' + n.find('div', {'class':'brand font-bold text-uppercase'}).text + '|'
								if n.find('div', {'class':'title'}):
									description = n.find('div', {'class':'title'}).text
								else:
									description = prod_id
								export_line += description + '|' 
								#выбаорка цены, если со скидкой, выдаётся обе цены
								price = n.find('div', {'class':'price'}).findAll('span')  
								if price[0]['class'][0] == 'fullprice':
									export_line += price[0].text + ':fullprice|'
								else:
									export_line += price[0].text + ':' + price[1].text + '|'
								# выборка размеров, в конце запятая
								size = n.find('div', {'class':'size text-light'}).findAll('span') 
								for n in size:
									export_line += n.text + ';'
								insert_input('yoox_py',export_line)
								export_line += '/n '
								export_file.write(export_line)
						else:
							checker.append(n('div')[0]['data-current-cod10'])
				else:
					print('cya')
					pagenum = 1
			except Exception:
				print(datetime.datetime.now()," :ERROR: ", pagenum)
				print(items)
				error_export.write(datetime.datetime.now())
				error_export.write(':ERROR:')
				error_export.write(page)
				error_export.write('/n')
			else:
				print(datetime.datetime.now(), '::PASS::', pagenum)
				pagenum += 1
				#print(links_exp)
				