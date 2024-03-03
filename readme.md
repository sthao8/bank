# Notes since meeting
I tried to follow PEP-8 and made lines shorter than 79 to 99 characters (most of them, anyways). I find it less readable. Maybe you can tell me if you think it's better!

### Unittest:
I couldn't resolve the module not found error when test_transactions.py was in a separate tests folder, so I was forced to move it out into root folder. Either press play to run tests or run py -m unittest to run!

### Transactions Page:
There is now a separate transactions page that shows frontend balance of accounts. Validation is of course handled serverside as well. It is now possible to transfer money from any account to any other account, except the same account, of course.

### Console app
The console app now deduplicates any transactions/accounts/customers that are flagged in both the first and second checks, returning a single table in mail. To test, simply uncomment the function in console_app.py.

As mentioned during meeting, there is not way to keep track of where you left off (checked column in transactions) since the program is made to run at midnight the next day. So we always check and get all of yesterday's transactions. 

### Search
Try searching for first name "maria" in order to get more than 50 results.

### Account transactions
Due to the seeding limitation of only one transaction seeded for today's date, there may not be more than 20 transactions. I would suggest making a bunch of transactions for one account if you would like to test the fetch feature.

### Base.html
Some syntax errors are showing up in base.html, but I believe that is because I am using Jinja inside of Javascript, which should be ok since Jinja renders before any Javascript does.

### Money input
Money, when shown, is in swedish locale, but needs to use decimal point when inputted

### API urls:
/api/<int: customer_id>
/api/accounts/<int: account_id>