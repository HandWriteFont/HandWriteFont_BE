## π Hand Write Font Back-End

## Set

### Install

#### Git Clone
```
    $ git clone https://github.com/Woo-Yeol/HandWriteFont_BE.git
```

#### Create Venv
```
    $ python -m venv venv
```

#### Activate Venv
```
    Mac
    $ source venv/bin/activate
    
    Window
    $ source venv/Scripts/activate
```

#### Requirements Install
```
    $ pip install -r requirements.txt 
```

#### Settings.py -> secrets.json μμ±
```
    {
    "SECRET_KEY": "*******************"
    }
```


#### Migration
```
    $ sh migrate.sh
```

#### Run Server
```
    $ python manage.py runserver
```

### After Pull

#### Reset Migration
- Error λ°μμ
```
    $ rm ./db.sqlite3
    $ sh reset_migration.sh
    $ sh migrate.sh
```

#### μ’μμ± μλ°μ΄νΈ
```
    $ pip install -r requirements.txt
```

## Sample

### SingIn Sample Data
```
    {
        "email" : "admin@admin.com",
        "password" : "admin"
    }
```

### SignUp Sample Data
```
    {
        "nickname" : "κ΄λ¦¬μ",
        "name" : "νμ€νΈ",
        "email" : "admin@admin.com",
        "password" : "admin"
    }
```

-λ‘κ·ΈμΈ μ€ν¨μμλ token κ°μ NULL κ°μΌλ‘ μ€μ νμ¬ λ³΄λ΄κΈ°-
