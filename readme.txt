1. create venv 
python.exe -m venv venv

2. active venv
& .\venv\Scripts\Activate.ps1

3. install packages
pip install -r .\requirements.txt


to convert Verizon xlsx to json
python verizon.py


git clone https://github.com/chencen2000/aviapy.git

to update model
1. ssh to 10.1.1.79
2. cd to /home/qa/projects/aviapy
3. sudo systemctl stop sga.service 
4. git pull
5. sudo systemctl start sga.service 
6. check service running
sudo systemctl status sga.service 