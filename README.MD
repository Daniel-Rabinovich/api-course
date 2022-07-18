 
#MySQL database

```cd mysql
docker run --name data -e MYSQL_ROOT_PASSWORD=123 -d -p 3306:3306 mysql
docker exec -i data sh -c 'exec mysql -uroot -p123' < create.sql
```
#Redis
```
docker run --name cache -d -p 6379:6379 redis
```
