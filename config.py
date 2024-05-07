class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:password@localhost/bank'
    SECRET_KEY = "bankassignmentforpythonprogrammingwebframeworkcourse"
    SECURITY_REGISTERABLE = True
    SECURITY_PASSWORD_SALT = 'supersecretsalt'

    MAIL_SERVER = '127.0.0.1'
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'email@example.com'  # Byt ut mot din e-post
    MAIL_PASSWORD = 'password'  # Byt ut mot ditt lösenord
    MAIL_DEFAULT_SENDER = 'dittgmail@example.com'  # Byt ut mot din e-post
    SECURITY_EMAIL_SENDER = '"MyApp"<norepyly@example.com>'  # Byt ut mot din e-post
