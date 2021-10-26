# # # # $1 -> absolute path of the tpc-ds benchmark folder
# # # # $2 -> size of the data (GB)

PATH_BENCH="$1"
dir_pwd=$(pwd)
cd "$1/tools"
chmod 777 dsqgen dsdgen


# # # create the queries
# # # if you run this, the script will overwrite the queries in the repository -> queries/queries_i
# # echo "Generating $2 GB of queries. The queries are in the /queries/queries_$2 folder"
# # # in order to avoid error:
echo 'define _END = ";"' >> "$1/query_templates/netezza.tpl"

for i in {1..99}; do
    ./dsqgen -template "query${i}.tpl" -directory ../query_templates/ -dialect netezza -scale $2 
    mv query_0.sql "$dir_pwd/queries/queries_${2}/query_${i}.sql"
done

# # # create the values
echo "Generating $2 GB of data"
`"$PATH_BENCH/tools/dsdgen" -dir /tmp –scale $2 -force Y` # only works like this lol

# # # create the database
sudo -u postgres psql -c "create database tpcds"
sudo -u postgres psql tpcds -f 'tpcds.sql'
sudo -u postgres psql tpcds -f 'tpcds_ri.sql'
sudo -u postgres psql tpcds -c "SET CLIENT_ENCODING TO 'latin1'" #bugs


# # load the values
cd /tmp
for i in `ls *.dat`; 
do table=${i/.dat/}; 
echo "Loading $table..."; 
sed -i 's/|$//' /tmp/$i; 
sudo -u postgres psql tpcds -q -c "TRUNCATE $table"; 
sudo -u postgres psql tpcds -c "\\copy $table FROM '/tmp/$i' CSV DELIMITER '|'"; done


# in case customer does not load try this:
#sudo -u postgres psql tpcds -c "SET CLIENT_ENCODING TO 'latin1;'"
#sudo -u postgres psql tpcds -c "\\copy customer FROM '/tmp/customer.dat' CSV DELIMITER '|'";
# in case this still doesn't work open the databse from terminal and add both commands

# run the queries

cd "${dir_pwd}"
# please make sure that you change the database, username and password.
# this example creates a database called "tpcds"
python3 query_executor.py
