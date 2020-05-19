# -*- coding: utf-8 -*-
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
# setting session setup
session = requests.session()
session.trust_env = False
headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
      }

def load_all_products (pagenum, headers, session, shoesize):
# Var pagenum
	url = 'https://www.asos.com/ru/men/tufli-botinki-i-kedy/cat/?cid=4209&currentpricerange=290-23890&nlid=mw|%D0%BE%D0%B1%D1%83%D0%B2%D1%8C|%D1%81%D0%BE%D1%80%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D1%82%D1%8C%20%D0%BF%D0%BE%20%D1%82%D0%B8%D0%BF%D1%83%20%D0%BF%D1%80%D0%BE%D0%B4%D1%83%D0%BA%D1%82%D0%B0&page=' + str(pagenum) + '&refine=size:' + shoesize + '&sort=priceasc'
	request = session.get(url, headers = headers)
	#print(request)
	return request.text

def check_for_products(text):
	soup = BeautifulSoup(text, 'html.parser')
	#search in meta tag, по content in double quotes
	all_products = soup.find('div', {'data-auto-id': 'productList'}, 'section')
	return all_products is not None

def write_link (to_out, link):
	link = 'https://www.asos.com' + urlparse(link)[2]
	to_out.write (link)
	to_out.write ('\n')

	#before start deleting old export as CASCHE
os.remove('./asos_page_export.log')
shoesize = '2323,2034'
pagenum = 1
currpage = 1
links_exp = {}
with open('./asos_page_export.log', 'a', encoding='utf-8') as output_file:
	while True:
		try:
			data = load_all_products(pagenum, headers, session, shoesize) #loading all pages, if this not last
			if check_for_products(data):
				soup = BeautifulSoup(data, 'html.parser') 		#search in main section with products
				product_list = soup.find('div', {'data-auto-id': 'productList'}, 'section')
				products = product_list.find_all('article') 	#searching of exact products, in tag 'article' with saving product ID
				for prod in products:
					link_prod = prod.find('a').get('href')
					id_prod = prod.get('id')
					if id_prod not in links_exp:	#add links if they not in links_exp
						links_exp[id_prod] = link_prod
						write_link(output_file, link_prod)
			else:
				with open('./logs/asos_error_export.log', 'r') as error_read: #after reading all pages read of error pages
					errors = error_read.read().split(';')
					print('Deleting from dict:', errors)
					for error in errors:
						links_exp.pop(error, None)
				pagenum = 1
				#ADDING OF SEARCHING SALE LINKS
				sleep(60)
		except Exception:
			print(time.strftime("%Y%m%d-%H%M%S"),":ERROR:")
		else:
			print(time.strftime("%Y%m%d-%H%M%S"), '::PASS::', pagenum)
		finally:
			pagenum += 1
			#print(links_exp)
