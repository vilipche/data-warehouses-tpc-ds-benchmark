EXPLAIN ANALYSE
WITH year_total_store AS (
    SELECT c_customer_id            customer_id
            ,
           c_first_name             customer_first_name
            ,
           c_last_name              customer_last_name
            ,
           d_year AS                year
            ,
           STDDEV_SAMP(ss_net_paid) year_total
            ,
           's'                      sale_type
    FROM customer
       , store_sales
       , date_dim
    WHERE c_customer_sk = ss_customer_sk
      AND ss_sold_date_sk = d_date_sk
      AND d_year IN (1999, 1999 + 1)
    GROUP BY c_customer_id
           , c_first_name
           , c_last_name
           , d_year
),
     year_total_web AS (
         SELECT c_customer_id            customer_id
                 ,
                c_first_name             customer_first_name
                 ,
                c_last_name              customer_last_name
                 ,
                d_year AS                year
                 ,
                STDDEV_SAMP(ws_net_paid) year_total
                 ,
                'w'                      sale_type
         FROM customer
            , web_sales
            , date_dim
         WHERE c_customer_sk = ws_bill_customer_sk
           AND ws_sold_date_sk = d_date_sk
           AND d_year IN (1999, 1999 + 1)
         GROUP BY c_customer_id
                , c_first_name
                , c_last_name
                , d_year
     )
SELECT t_s_secyear.customer_id,
       t_s_secyear.customer_first_name,
       t_s_secyear.customer_last_name
FROM (SELECT * FROM year_total_store WHERE year = 1999) t_s_firstyear
   , (SELECT * FROM year_total_store WHERE year = 1999 + 1) t_s_secyear
   , (SELECT * FROM year_total_web WHERE year = 1999) t_w_firstyear
   , (SELECT * FROM year_total_web WHERE year = 1999 + 1) t_w_secyear
WHERE t_s_secyear.customer_id = t_s_firstyear.customer_id
  AND t_s_firstyear.customer_id = t_w_secyear.customer_id
  AND t_s_firstyear.customer_id = t_w_firstyear.customer_id
  AND t_s_firstyear.year_total > 0
  AND t_w_firstyear.year_total > 0
  AND CASE WHEN t_w_firstyear.year_total > 0 THEN t_w_secyear.year_total / t_w_firstyear.year_total ELSE NULL END
    > CASE WHEN t_s_firstyear.year_total > 0 THEN t_s_secyear.year_total / t_s_firstyear.year_total ELSE NULL END
ORDER BY 2, 1, 3
LIMIT 100;