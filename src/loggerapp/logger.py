
LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'verbose': {
            'format': '%(asctime)s - %(levelname)s - %(message)s - %(filename)s - %(funcName)s - %(lineno)s'
		},
		'simple': {
			'format': '%(levelname)s '
		},
	},
	'handlers': {
		'db_log': {
			'level': 'DEBUG',
            'class': 'loggerapp.handlers.DBHandler',
            'model': 'loggerapp.models.GeneralLog',
            'expiry': 86400,
            'formatter': 'verbose',
            
		},
        'sp_log': {
			'level': 'DEBUG',
            'class': 'loggerapp.handlers.DBHandler',
            'model': 'loggerapp.models.SpeicalLog',
            'expiry': 86400,
            'formatter': 'verbose',
            
		},
		'console': {
			'class': 'logging.StreamHandler',
		},
	},
	'loggers': {
		'db': {
			'handlers': ['db_log', 'console'],
			'level': 'DEBUG',
		},
        'sp_db': {
			'handlers': ['sp_log', 'console'],
			'level': 'DEBUG',
		}
	}
}