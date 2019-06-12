import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
dev_key = os.urandom(24)


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', dev_key)

    DEBUG_TB_INTERCEPT_REDIRECTS = False  # 是否拦截重定向，默认为TRUE

    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 是否追踪对象的修改
    # SQLALCHEMY_RECORD_QUERIES = True  # 性能测试，是否记录数据库查询，使用DebugToolbar自动开启，此处显示开启

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

    ATTACHMENT_UPLOAD_PATH = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # file size exceed to 10 MB will return a 413 error response.


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(basedir, 'data-dev.db')


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # in-memory database


class ProductionConfig(BaseConfig):
    MARIADB_USER = os.getenv('MARIADB_USER')
    MARIADB_PASSWORD = os.getenv('MARIADB_PASSWORD')
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://' + MARIADB_USER + ':' + MARIADB_PASSWORD + '@localhost/TaskBoard'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
