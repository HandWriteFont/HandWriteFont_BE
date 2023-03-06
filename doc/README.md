
## 📝 Hand Write Font Back-End

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

#### Settings.py -> secrets.json 생성
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
- Error 발생시
```
    $ rm ./db.sqlite3
    $ sh reset_migration.sh
    $ sh migrate.sh
```

#### 종속성 업데이트
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
        "nickname" : "관리자",
        "name" : "테스트",
        "email" : "admin@admin.com",
        "password" : "admin"
    }
```

-로그인 실패시에는 token 값을 NULL 값으로 설정하여 보내기-
