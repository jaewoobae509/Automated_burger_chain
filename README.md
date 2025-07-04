# csc440-fp-team03
## How to Run
### 1. Clone the Repository
```
git clone https://github.ncsu.edu/engr-csc440-sp25-final-project-repos/csc440-fp-team03
```

### 2. Install Flask
```
pip install Flask flask-cors
```

### 3. Install mysql-connector-python
```
pip install mysql-connector-python
```

### 4. Import burgerchain_db.sql
Open mySQL
Open the server already established  
Under server tab, click data import  
Import from Self-contained file, and select the [burgerchain_db.sql](burgerchain_db.sql) file  

DONT FORGET TO UPDATE YOUR CREDENTIALS IN credentials.py

it should look something like this  
```
DB_HOST = "your_local_host"
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_NAME = "burger_chain"
```

### 5. Run burger_chain_mock.sql in mySQL
Click Open a SQL file in a new query tab from the menu 

Select [burger_chain_mock.sql](burger_chain_mock.sql)

Run the query in sql

### 6. Run the App
```
python backend/app.py
```
Open http://127.0.0.1:5000

## Roles
### **Manager**

- Log in with:
  - `Username: manager_max`
  - `Password: manager789`
- Can view all customer orders
- Can update order statuses (confirm, reject)

### **Customer**

- Create an account by signing in with a unique username and password
- Can browse the menu and place orders

<br>

> **To test Manager and Customer roles at the same time, open one in Incognito and ther other in a normal tab**
