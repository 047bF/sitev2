CREATE TABLE public.brands
(
    brand_id serial NOT NULL,
    brand_name varchar(20) NOT NULL,
    main_brand integer,
    is_collab boolean,
    brand_collab_id integer REFERENCES brand(brand_id),
    PRIMARY KEY (brand_id),
    CONSTRAINT brand_name_uniq UNIQUE (brand_name)
);

CREATE TABLE public.models
(
    mod_id serial NOT NULL,
    mod_name varchar(30),
    brand_brand_id integer REFERENCES brands(brand_id),
    mod_input varchar(30),
    PRIMARY KEY (mod_id)
);

CREATE TABLE public.valuta
(
    val_id serial NOT NULL,
    val_name varchar(30),
    exchange_rate money,
    PRIMARY KEY (val_id)
);
INSERT INTO valuta (val_name)
values 	('RUB'),
		('USD'),
		('EUR'),
		('GPB');
COMMIT;

CREATE TABLE public.sites
(
    site_id serial NOT NULL,
    site_name varchar(30),
    val_val_id integer REFERENCES valuta(val_id),
    site_user varchar(30) NOT NULL,
    site_link varchar(100) NOT NULL,
    site_piclink varchar(100),
    PRIMARY KEY (site_id),
	CONSTRAINT site_name__val_uniq UNIQUE (site_name,val_val_id)
);
INSERT INTO sites (site_name,val_val_id,site_user,site_link)
values 	('YOOX',1,'yoox_py','https://www.yoox.com/ru/'),
		('ASOS',1,'asos_read','https://www.asos.com/ru/');
COMMIT;

CREATE TABLE public.languages
(	lang_id serial,
	lang_name varchar(15) NOT NULL,
	PRIMARY KEY (lang_id),
	CONSTRAINT lang_name_uniq UNIQUE (lang_name)
);
INSERT INTO public.languages (lang_name)
values	('english'),
		('русский'); 
COMMIT;

CREATE TABLE public.available
(	avail_id serial,
	avail_name varchar(20) NOT NULL,
	lang_lang_id integer REFERENCES languages(lang_id) DEFAULT 1,
	PRIMARY KEY (avail_id),
	CONSTRAINT avail_name_uniq UNIQUE (avail_name)
);
INSERT INTO public.available (avail_name)
values	('in stock'),
		('not in stock');
COMMIT;

CREATE TABLE public.model_histories
(   mod_site_uniq integer NOT NULL,
	mod_mod_id integer NOT NULL REFERENCES models(mod_id),
    brand_brand_id integer NOT NULL REFERENCES brands(brand_id),
	number_history integer DEFAULT 1,
 	navi_date date DEFAULT current_timestamp,
 	insert_date date NOT NULL,
 	avail_avail_id integer DEFAULT 1 REFERENCES available(avail_id),
 	site_site_id integer NOT NULL REFERENCES sites(site_id),
    price numeric(6,2) NOT NULL,
    sale_price numeric(6,2),
 	val_val_id integer NOT NULL REFERENCES valuta(val_id),
    PRIMARY KEY (mod_site_uniq)
);

CREATE TABLE public.gender
(	gen_gen_id serial,
	gen_name varchar(15),
	lang_lang_id integer DEFAULT 1 REFERENCES languages(lang_id),
	PRIMARY KEY (gen_gen_id),
	CONSTRAINT gen_name_uniq UNIQUE (gen_name)
);
INSERT INTO public.gender (gen_name)
values	('male'),
		('female'),
		('kids');
COMMIT;

CREATE TABLE public.sizes
(	size_id serial,
	size_value decimal,
	size_label varchar(2),
	gen_gen_id integer DEFAULT 1 REFERENCES gender(gen_id),
	PRIMARY KEY (size_id)	
);
INSERT INTO sizes (size_value,size_label)
SELECT  generate_series(35, 47,0.5), 'EU';
COMMIT;

CREATE TABLE public.size_histories
(	mod_mod_id integer NOT NULL REFERENCES models(mod_id),
	size_size_id integer NOT NULL REFERENCES sizes(size_id),
	site_site_id integer NOT NULL REFERENCES sites(site_id),
	avail_avail_id integer DEFAULT 1 REFERENCES available(avail_id),
	navi_date date DEFAULT current_timestamp,
	CONSTRAINT mod_size_site_uniq UNIQUE (mod_mod_id,size_size_id,site_site_id)
);

CREATE TABLE public.statuses
(	smst_id integer,
	smst_name varchar(20),
	PRIMARY KEY (smst_id)
);
INSERT INTO public.statuses (smst_id,smst_name)
values 	(1,'passed'),
		(2,'unique error'),
		(3,'complete'),
		(0,'in progress'),
		(999,'unexpect error');
COMMIT;

CREATE TABLE public.site_import_links
(	sil_id bigserial,
	sil_unique varchar(100) NOT NULL,
	sil_link varchar(100) NOT NULL,
	site_site_id integer NOT NULL REFERENCES sites(site_id),
	smst_smst_id integer REFERENCES statuses(smst_id),
	PRIMARY KEY (sil_id)
);

CREATE TABLE public.input
(	in_id bigserial,
	in_raw varchar(500) NOT NULL,
	navi_date date DEFAULT current_timestamp,
	navi_user varchar(20) NOT NULL,
	in_pic varchar(100),
	smst_smst_id integer REFERENCES statuses(smst_id),
	brand_scan integer REFERENCES statuses(smst_id),
	mod_scan integer REFERENCES statuses(smst_id),
	PRIMARY KEY (in_id)
);