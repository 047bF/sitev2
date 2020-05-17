		--**--
		/*Добавить список сайтов, ссылки на сайты, ссылки на картинки, стоимость доставки*/
		--**--
		ссылки на картинки
		сделать автоматический скрипт - не скоро

ALTER SEQUENCE models_mod_id_seq START 1;


	--**--
		/* Обновить справочник моделей, привязать к брендам, description yoox common
		select * from select_insert_mods(999999);

		select b.brand_name,m.mod_name,b.brand_collab_id1,b.brand_collab_id2 from models m
		left join brands b on b.brand_id=m.brand_brand_id
		where m.mod_name != 'description';
		
		insert into models (brand_brand_id,mod_name) 
		select distinct b.brand_id,SPLIT_PART(i.in_raw,'|',3) from input i
		join brands b on b.brand_name = SPLIT_PART(i.in_raw,'|',2);
		
		select * from input where complete!=1;
		*/
	--**--

do $$
declare 
	brnd_name varchar(50);
	id integer;
	begin
	for id in select m.mod_id from models m 
	loop
	select b.brand_name into brnd_name from models m 
	join brands b on b.brand_id = m.brand_brand_id
	where m.mod_id=id;	
execute ('UPDATE models SET mod_name = regexp_replace(mod_name, $replace$ '|| brnd_name ||' $replace$, '''', '''')');
	end loop;
	end $$

	--**--
		/*Обновить бренды, сменить название у колобораций, добавить 2 столбца как альтернативные бренды
		select brand_collab_set(brand_id) from brands where is_collab=TRUE;
		select b.brand_id, b.brand_name, b.is_collab, b1.brand_name, b2.brand_name from brands b
		left join brands b1 on b.brand_collab_id1=b1.brand_id
		left join brands b2 on b.brand_collab_id2=b2.brand_id
		order by b.brand_name;*/
	--**--

	--**--
	/*скрипт обработки input 
	добавляет id товара, с выбором модели, бренда, выборка цены, выбор размера. если ошибок нет добавляем дату вставки.
	смотрим на пользователя из скрипта, привязываем запись к этому сайту
	Если id уже есть, проверяем верная ли модель. Если да, проверяем цену/размер. Всё сходится, пропускаем запись.
	ID есть, но модель другая - exception и запись в лог. Если изменилась цена или размер обновляем информацию и указываем дату обновления - функиця NOW()

	после завершения обработки у записи указываем флаг complete, ограничение в 1000 строк за раз. повторяем выборку для записи без флага.
	*/
	--**--

select b.brand_name,m.mod_name,s.site_name, sale_price from model_histories mh
join brands b on b.brand_id=mh.brand_brand_id
join models m on m.mod_id=mh.mod_mod_id and m.brand_brand_id=b.brand_id
join sites s on s.site_id=mh.site_site_id
order by b.brand_name, m.mod_name

Если id уже есть, проверяем верная ли модель. Если да, проверяем цену/размер. Всё сходится, пропускаем запись.
ID есть, но модель другая - exception и запись в лог. Если изменилась цена или размер обновляем информацию и указываем дату обновления - функиця NOW()

проверить генерацию картинок по id товара. 

логгирование изменений

--**-- 
/* обновить скрипт выборки на yyoox, добавить информацию о модели, как видел с егором
обновить оба скрипта, переделать в try: 
сменить расположение стоимостей fullprice-sale_price
*/
--**--

/*update brands
set main_brand = qur.brand_set
from (
	select b.brand_id as brand_update,b1.brand_id brand_set  ,b.brand_name,b1.brand_name from brands b
	join brands b1 on b.brand_id != b1.brand_id
	where 1=1
	and (b.brand_name like '% '|| b1.brand_name ||'%' or b.brand_name like '%'|| b1.brand_name ||' %')
	and b.is_collab=FALSE
	and b.main_brand is null
	and b1.brand_id not in (54330,55917,54201,60970,51655,62428,50853,58961,74341,54325,53499,51326,51756,64704,63468,52618,64079,52162,64446,59134,53764,51817,65072,65072,70180,59882,51326,52162)
	order by b.brand_name, b1.brand_name) as qur
	where qur.brand_update = brands.brand_id*/
	
	
при наличии ошибки запись в лог файл на примере модуля записи в бд


добавить размерные сетки обуви + картинки с сеткой для каждого бренда
попробовать запуск скриптов из БД с выводом ошибок, возможно хранение скрипта в БД

/*АПДЕЙТ текущей информации в БД*/

прописать параметры available/complete 1,2,3,999


create or replace FUNCTION brand_collab_set(p_collab_brand_id in brands.brand_id%TYPE) RETURNS void
AS $$
DECLARE 
	p_rec RECORD;
BEGIN
	create temporary table temp_brand_collab_set 
	AS 
	select b.brand_id as p_brand_id,b.brand_name,b1.brand_id
		from brands b
		join (
			select 	case 
				when split_part(upper(BRAND_NAME),' WITH ',2) !='' then split_part(upper(BRAND_NAME),' WITH ',1)
				when split_part(upper(BRAND_NAME),' BY ',2) !='' then split_part(upper(BRAND_NAME),' BY ',1)
				when split_part(upper(BRAND_NAME),' X ',2) !='' then split_part(upper(BRAND_NAME),' X ',1)
				when split_part(BRAND_NAME,' + ',2) !='' then split_part(BRAND_NAME,' + ',1)
			end as brands, brand_id
			from brands
			union select case 
				when split_part(upper(BRAND_NAME),' WITH ',2) !='' then split_part(upper(BRAND_NAME),' WITH ',2)
				when split_part(upper(BRAND_NAME),' BY ',2) !='' then split_part(upper(BRAND_NAME),' BY ',2)
				when split_part(upper(BRAND_NAME),' X ',2) !='' then split_part(upper(BRAND_NAME),' X ',2)
				when split_part(BRAND_NAME,' + ',2) !='' then split_part(BRAND_NAME,' + ',1)
			end as brands, brand_id
			from brands) b1 
				on b1.brands is not null and b1.brands=b.brand_name
		where b1.brand_id=p_collab_brand_id;
	for p_rec in select t.*, ROW_NUMBER () OVER (ORDER BY p_brand_id) as t_count from temp_brand_collab_set t
		loop
			EXECUTE 'update brands set brand_collab_id' ||p_rec.t_count || ' = '|| p_rec.p_brand_id ||' where '|| p_rec.brand_id|| '=brand_id';
		end loop;
	update brands set is_collab=TRUE where p_collab_brand_id = brand_id and brand_collab_id1 is not null;
	DROP table temp_brand_collab_set;
end;
$$ LANGUAGE plpgsql;

--****----****----**-*-*---

create or replace FUNCTION select_insert_mods (f_limit integer)
	RETURNS integer AS $$
BEGIN 
if f_limit < 1 or f_limit > 10000 then
			f_limit := 10000;
end if;			
for row in 1..f_limit loop
	update input
	set mod_scan = insert_fun.result
	from (
		select i.in_id,get_mod_from_input(i.in_id) as result
		from input i 
		where i.mod_scan = 0
		limit 1
		) as insert_fun
		where input.in_id=insert_fun.in_id;
		END LOOP;
			RETURN 1;
	EXCEPTION	WHEN OTHERS THEN RETURN 999;	
end
$$ LANGUAGE plpgsql;

create or replace FUNCTION get_mod_from_input(f_in_id in input.in_id%TYPE) 
		RETURNS integer AS $$
BEGIN 
	insert into models (brand_brand_id,mod_input,mod_name) 
		select b.brand_id,
		SPLIT_PART(i.in_raw,'|',3) as mod_input,
		replace(replace(SPLIT_PART(i.in_raw,'|',3),
						SPLIT_PART(i.in_raw,'|',2),
						''),
						'  ',' '
			   )  as mod_name
		from input i
		join brands b on b.brand_name = upper(SPLIT_PART(i.in_raw,'|',2))
		where i.in_id = f_in_id;
		RETURN 1;
	EXCEPTION WHEN unique_violation THEN RETURN 2;	
end
$$ LANGUAGE plpgsql;


--**---***--*---



create or replace FUNCTION select_insert_mod_histories(f_limit integer)
	RETURNS integer AS $$
BEGIN 
if f_limit < 1 or f_limit > 10000 then
			f_limit := 10000;
end if;
for row in 1..f_limit loop
	update input
	set complete = insert_fun.result
	from (
		select i.in_id,insert_mod_histories(i.in_id) as result
		from input i 
		where i.complete = 0 or i.complete is NULL
		limit 1 
		) as insert_fun
	where input.in_id=insert_fun.in_id;
	end loop;
RETURN 1;
	EXCEPTION	WHEN OTHERS THEN RETURN 999;

end
$$ LANGUAGE plpgsql;

	create or replace FUNCTION insert_mod_histories(f_in_id in input.in_id%TYPE) --под вопросом
		RETURNS integer AS $$
BEGIN 
insert into model_histories (mod_site_uniq,brand_brand_id,mod_mod_id, price,sale_price,sizess,site_site_id,val_val_id,insert_date,avail_avail_id)
select	SPLIT_PART(i.in_raw,'|',1) as mod_uniq,
		b.brand_id,
		m.mod_id,
		NULLIF(regexp_replace(SPLIT_PART(SPLIT_PART(i.in_raw,'|',4),':',2), '\D','','g'), '')::numeric AS price,
		(CASE when SPLIT_PART(i.in_raw,'|',4) like 'fullprice%' then 0 else
		NULLIF(regexp_replace(SPLIT_PART(SPLIT_PART(i.in_raw,'|',4),':',1), '\D','','g'), '')::numeric end) AS sale_price,
		SPLIT_PART(i.in_raw,'|',5) as size,
		s.site_id as site,
		s.val_val_id as valuta,
		i.navi_date as insert_date,
		1 as available
from input i 
	join brands b on b.brand_name = SPLIT_PART(i.in_raw,'|',2)
	join models m on m.mod_input = SPLIT_PART(i.in_raw,'|',3) and m.brand_brand_id=b.brand_id
	join sites s on s.site_user = i.navi_user
	where i.in_id = f_in_id;
		RETURN 1;
	EXCEPTION WHEN unique_violation THEN RETURN 2;
end
$$ LANGUAGE plpgsql;

--***---***---**--

create or replace FUNCTION select_insert_brands(f_limit integer)
	RETURNS integer AS $$
BEGIN 
if f_limit < 1 or f_limit > 10000 then
			f_limit := 10000;
end if;
for row in 1..f_limit loop
	update input
	set brand_smst_id = insert_fun.result
	from (
		select i.in_id,get_brand_from_input(i.in_id) as result
		from input i 
		where i.brand_smst_id = 0
		limit 1 
		) as insert_fun
	where input.in_id=insert_fun.in_id;
	end loop;
RETURN 1;
	EXCEPTION	WHEN OTHERS THEN RETURN 999;
end
$$ LANGUAGE plpgsql;

create or replace FUNCTION get_brand_from_input(f_in_id in input.in_id%TYPE) 
		RETURNS integer AS $$
BEGIN 
	insert into brands (brand_name) 
		select upper(SPLIT_PART(i.in_raw,'|',2)) as brand
		from input i where i.in_id = f_in_id;
		RETURN 1;
	EXCEPTION WHEN unique_violation THEN RETURN 2;	
end
$$ LANGUAGE plpgsql;

----****-----*****----****