# -*- coding: utf-8 -*-
"""
Created on Sat Dec 11 23:50:48 2021

@author: Tomasz
"""


#Define Functions  
def check_password(pswd):
    '''Check, if the password meets security criteria: length, minor/major, number, symbol
    Args:
        string - input password
    Return:
        Boolean - True or False
    '''
    #Import regex library
    import re
    #Set the password security criteria
    password_restrictions = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"    
    #Compile regex
    password_compiled = re.compile(password_restrictions)
    #Search regex and password                
    password_check = re.search(password_compiled, pswd)
    #Validate conditions
    if password_check:
        return True
    else:
        return False

def sign_up():
    '''Create new user. Check user and password validity. Story username and password in a .csv file
    Args:
        none
    Return:
        Store username and password in database.csv file
    '''
    #Import libraries
    import pandas as pd
    import getpass
    from argon2 import PasswordHasher
    #Read user database
    db_users = pd.read_csv('001database.csv', header=0, index_col=0)
    username = '0'
    
    #Loop to input username and check username validity
    while len(username) < 2 or username in db_users['user'].values:
        username = input('Create username: ')
        if len(username) < 2:
            print('The username should be at least 2 characters long!')
        elif username in db_users['user'].values:
            print('The username already exists')
    
    #Input password and check 
    password1 = getpass.getpass('Create password: ')
    password2 = getpass.getpass('Confirm password: ')
    
    if check_password(pswd=password1) == False:
        #Check password meets security criteria
        print('The password should be at least 6 characters long contain minor / major letter, sign and a number')
        return sign_up()
    elif password1 != password2:
        #Check, if password is confirmed
        print('Password does not match')
        return sign_up()
    else:
        #Password validate. Encrypt and store username and password
        ph = PasswordHasher()
        hash = ph.hash(password1)
        db_users = db_users.append({'user':username, 'password':hash}, ignore_index=True)
        db_users.to_csv('001database.csv')
        print('OK. Account created')

def login():
    '''Login user.
    Args:
        none
    Return:
        boolean - True or False
    '''
    #Import libraries
    import pandas as pd
    import getpass
    from argon2 import PasswordHasher
    ph = PasswordHasher()
    
    username = input('Input username: ')
    password1 = getpass.getpass('Input password: ')
    
    db_users = pd.read_csv('001database.csv', header=0, index_col=0)
    
    if username not in db_users['user'].values:
        print('The username does not exist.')
        return login()
    else:
        try:
            if ph.verify(db_users[db_users['user'] == username]['password'].item(), password1) == True:
                print('Login successful')
        except:
            print('Incorrect password !')
            return login()
        
def delete_user(username):
    '''Remove user from the user database
    Args:
        username - user
    Return:
        none - save updated user database
    '''
    #Import libraries
    import pandas as pd
    
    db_users = pd.read_csv('001database.csv', header=0, index_col=0)
    db_users.drop(db_users[db_users['user'] == username].index, inplace = True)
    db_users.to_csv('001database.csv')

start = ''
while start not in ['1', '2']:
    start = input('Make your choice [1 - Login, 2 - Signup]: ')

if start == '1':
    login()
else:
    sign_up()


