usage of Supervisor to run 24/7 the flask app

https://www.digitalocean.com/community/tutorials/how-to-install-and-manage-supervisor-on-ubuntu-and-debian-vps

----------------------------------------------------------------------
1.
apt-get install supervisor

2. copy jass_service.conf to:
/etc/supervisor/conf.d/

3. run:
supervisorctl reread

4. run:
supervisorctl update

5. start/stop or status of program
supervisorctl start jass
supervisorctl stop jass
supervisorctl status