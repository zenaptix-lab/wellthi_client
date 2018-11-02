# wellthi_client
Wellthi client app

First install virtual env on machine : 
```
$ sudo pip2 install virtualenv
```

To initialize python virtual environment run : 
```
$ virtualenv -p /usr/bin/python2.7 wellthi_client
```

Flask setup after init in virtual env :
```
$ pip install Flask
$ FLASK_APP=wellthi.py flask run --host=0.0.0.0
```

