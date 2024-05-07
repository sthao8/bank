# Bank App

## Description:

### Purpose

Bank App is a simple web app that simulates an internal banking application used by bank employees.

### Features
<ul>
<li>On initial run, the database seeds dummy customer and user accounts, including configurable localized customer information limited to countries supported by Faker.</li>
<li>App supports withdraw, deposit, and transfer transactions.</li>
<li>A simple search bar is always visible on the navbar that allows search via customer id.</li>
<li>If a simple search fails to find any results, user is redirected to advanced search to filter customers by name or city.</li>
<li>Admin users have ability to CRUD users: add users, change password, and set roles.</li>
<li>Users can add new customers.</li>
<li>Often there is front-end validation of input fields with dynamic error messages and backend validation before writing to database.</li>
<li>Console app requires manual run to audit for suspicious transactions and accounts, emailing results through email.</li>
<li>API-querying allows for returning sorted and limited search results without refreshing.</li>
</ul>

### Technologies
<ul>
<li>Python 3.11.5</li>
<li>Database with MySQL, implemented in python with SQLAlchem 3.1.1</li>
<li>Frontend development using Bootstrap 5.3</li>
<li>Flask 2.3.3 for web framework</li>
<li>Login and security via Flask Security Too 5.3.3</li>
<li>Input validation using Flask-WTF 1.2.1</li>
<li>Seeding of data using Faker 22.5.0</li>
</ul>

### How to install:
<ol>
<li>Create a MySql database according to this line: SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:password@localhost/bank, or alternatively change this line to fit your database type, name, and password</li>
<li>Download or clone this repo onto your computer.</li>
<li>Navigate to downloaded/cloned folder in the development environment of your choice, like VS Code, and open the folder</li>
<li>Run `pip install -r requirements.txt'</li>
<li>Run `flask run` in the terminal to start the Flask application.</li>
<li>CTRL-click the generated link from step 4 to open Bank App in a browser.</li>
<li>You should now see the login page of Bank app in the browser.</li>
</ol>

## How to use:
<ol>
<li>Log in to Bank App using your provided credentials.</li>
<li>Explore the application!</li>
</ol>

## Notable files

### /constants/constants.py
In class TelephoneCountryCodes, add a country's country code and phone code to be able to seed customers from that country. This will seed localized data, including national ids, names, postal codes, and cities.

Other constants can be changed here, such as the types of accounts, user roles, and min/max age used in the birthday validator when creating new customers, etc.

### seed.py

Here, you can change how many accounts are seeded and the max transaction amount. Changing the latter will affect the console app's results. You can also determine which user accounts to seed. Remember to empty your database if you have made changes and want to redo the seeding process.

## API urls:
<ul>
<li>/api/<int: customer_id></li>
<li>/api/accounts/<int: account_id></li>
</ul>
