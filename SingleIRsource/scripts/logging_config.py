from datetime import datetime
date = datetime.now().strftime("%m-%d-%Y")

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s.%(msecs)03d - %(name)s - %(funcName)s - %(levelname)s - %(message)s',
            'datefmt': '%H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'logs/session_' + date + '.log',
            'mode': 'a',
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        '__main__': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'PXIe_5170R': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'FSW_0010': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'utils': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        }
    }
}