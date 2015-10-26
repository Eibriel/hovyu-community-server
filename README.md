# hovyu-community-server
Hovyu Community Server

docker run -d -p 27017:27017 --name some-mongo mongo

Development
==========

docker start some-mongo

docker build -t widudev_devmain:latest .
docker create --link=mongodockercompose_db_1:mongodockercompose_db_1 -l widudev_devmain_1 --name=widudev_devmain_1 widudev_devmain:latest
docker start widudev_devmain_1

docker build -t widudev_devweb:latest .
docker create --link=widudev_devmain_1:widudev_devmain_1 -l widudev_devweb_1 --name=widudev_devweb_1 -p=8080:80 widudev_devweb:latest
docker start widudev_devweb_1

Production
=========

docker build -t widu_web:latest .
docker create --link=widu_main_1:widu_main_1 -l widu_web_1 --name=widu_web_1 -p=80:80 widu_web:latest
docker start widu_web_1
