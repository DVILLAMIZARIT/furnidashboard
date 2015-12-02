"""Common settings and globals."""

from os.path import abspath, basename, dirname, join, normpath
from os import environ
from sys import path

########## PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
########## END PATH CONFIGURATION


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## MANAGER CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
	('Emil Akhmirov', 'akhmirem@gmail.com'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
########## END MANAGER CONFIGURATION


########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.',
		'NAME': '',
		'USER': '',
		'PASSWORD': '',
		'HOST': '',
		'PORT': '',
	}
}
########## END DATABASE CONFIGURATION


########## GENERAL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'America/Los_Angeles'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
########## END GENERAL CONFIGURATION


########## MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = normpath(join(SITE_ROOT, 'media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'
########## END MEDIA CONFIGURATION


########## STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = normpath(join(SITE_ROOT, 'assets'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
	normpath(join(SITE_ROOT, 'static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
########## END STATIC FILE CONFIGURATION


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key should only be used for development and testing.
SECRET_KEY = r"@)jv)^k=1f055u(0b@t$efrdmu(z0#+_z&dp&wkmsu*4*w2xkb"
########## END SECRET CONFIGURATION


########## SITE CONFIGURATION
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
	'.furnitalia.com',
	'.furnitalia.com.'
]
########## END SITE CONFIGURATION


########## FIXTURE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
	normpath(join(SITE_ROOT, 'fixtures')),
)
########## END FIXTURE CONFIGURATION


########## TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
# TEMPLATE_CONTEXT_PROCESSORS = (
#     'django.contrib.auth.context_processors.auth',
#     'django.core.context_processors.debug',
#     'django.core.context_processors.i18n',
#     'django.core.context_processors.media',
#     'django.core.context_processors.static',
#     'django.core.context_processors.tz',
#     'django.contrib.messages.context_processors.messages',
#     'django.core.context_processors.request',
# )

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
# TEMPLATE_LOADERS = (
# 	'django.template.loaders.filesystem.Loader',
# 	'django.template.loaders.app_directories.Loader',
# )

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_DIRS = (
	normpath(join(SITE_ROOT, 'templates')),
)
# Custom Templates
TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': TEMPLATE_DIRS,
        # 'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.contrib.auth.context_processors.auth',
				'django.core.context_processors.debug',
				'django.core.context_processors.i18n',
				'django.core.context_processors.media',
				'django.core.context_processors.static',
				'django.core.context_processors.tz',
				'django.contrib.messages.context_processors.messages',
				'django.core.context_processors.request',
			],
			'loaders': [
				'django.template.loaders.filesystem.Loader',
				'django.template.loaders.app_directories.Loader',
			]
		},
	},
	{
		'BACKEND': 'pdf.pdf.PdftkEngine',
        # 'APP_DIRS': True,
		'DIRS': TEMPLATE_DIRS,
		'OPTIONS': {
			'context_processors': [
				'django.contrib.auth.context_processors.auth',
				'django.core.context_processors.debug',
				'django.core.context_processors.i18n',
				'django.core.context_processors.media',
				'django.core.context_processors.static',
				'django.core.context_processors.tz',
				'django.contrib.messages.context_processors.messages',
				'django.core.context_processors.request',
			],
			'loaders': [
				'django.template.loaders.filesystem.Loader',
				'django.template.loaders.app_directories.Loader',
			]
		}

	},
]

PDFTK_BIN = environ.get('PDFTK_BIN', '/usr/bin/pdftk')  # normpath(join(SITE_ROOT, 'pdf', 'fdfgen'))

########## END TEMPLATE CONFIGURATION


########## MIDDLEWARE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE_CLASSES = (
	# Default Django middleware.
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'audit_log.middleware.UserLoggingMiddleware',
	# 'orders.middleware.SquashInvalidHostMiddleware',
)
########## END MIDDLEWARE CONFIGURATION


########## URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = '%s.urls' % SITE_NAME
########## END URL CONFIGURATION


########## APP CONFIGURATION
DJANGO_APPS = (
	# Default Django apps:
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',

	# Useful template tags:
	# 'django.contrib.humanize',

	# Admin panel and documentation:
	'django.contrib.admin',
	# 'django.contrib.admindocs',
)

THIRD_PARTY_APPS = (
	# Database migration helpers:
	'django_tables2',
	'ajax_select',
	'bootstrap_toolkit',
	'bootstrap3',
	'bootstrap3_datetime',
	'crispy_forms',
	'django_extensions',
	'kronos',
)

# Apps specific for this project go here.
LOCAL_APPS = (
	'associates',
	'customers',
	'stores',
	'orders',
	'commissions',
	'claims',
	'pdf',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
########## END APP CONFIGURATION

# specifying which model is used for auth model
AUTH_USER_MODEL = "auth.User"
LOGIN_REDIRECT_URL = "/"

########## LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# LOGGING = {
# 	'version': 1,
# 	'disable_existing_loggers': False,
# 	'filters': {
# 		'require_debug_false': {
# 			'()': 'django.utils.log.RequireDebugFalse'
# 		}
# 	},
# 	'handlers': {
# 		'mail_admins': {
# 			'level': 'ERROR',
# 			'filters': ['require_debug_false'],
# 			'class': 'django.utils.log.AdminEmailHandler'
# 		},
# 		'null': {
# 			'level': 'ERROR',
# 			'class': 'logging.NullHandler',
# 		},
# 		'applogfile': {
# 			'level': 'DEBUG',
# 			'class': 'logging.handlers.RotatingFileHandler',
# 			'filename': normpath(join(SITE_ROOT, 'logs/error.log')),
# 			'maxBytes': 1024 * 1024 * 15,  # 15MB
# 			'backupCount': 10,
# 		},
# 	},
# 	'loggers': {
# 		'django.request': {
# 			'handlers': ['mail_admins', 'applogfile'],
# 			'level': 'DEBUG',
# 			'propagate': True,
# 		},
# 		'django.security.DisallowedHost': {
# 			'handlers': ['null'],
# 			'level': 'ERROR',
# 			'propagate': False,
# 		},
# 	}
# }
LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'filters': {
		'require_debug_false': {
			'()': 'django.utils.log.RequireDebugFalse'
		}
	},
	'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
	'handlers': {
		'mail_admins': {
			'level': 'ERROR',
			'filters': ['require_debug_false'],
			'class': 'django.utils.log.AdminEmailHandler'
		},
		'null': {
			'level': 'ERROR',
			'class': 'logging.NullHandler',
		},
		'applogfile': {
			'level': 'DEBUG',
			'class': 'logging.handlers.RotatingFileHandler',
			'filename': normpath(join(SITE_ROOT, 'logs/error.log')),
			'maxBytes': 1024 * 1024 * 15,  # 15MB
			'backupCount': 10,
			'formatter': 'verbose',
		},
	},
	'loggers': {
		'django.request': {
			'handlers': ['mail_admins', 'applogfile'],
			'level': 'ERROR',
			'propagate': True,
		},
		'django.security.DisallowedHost': {
			'handlers': ['null'],
			'level': 'ERROR',
			'propagate': False,
		},
		'furnicloud': {
			'handlers': ['applogfile'],
			'level': 'DEBUG',
			'propagate': True,
		},
	}
}
########## END LOGGING CONFIGURATION


########## WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = '%s.wsgi.application' % SITE_NAME
########## END WSGI CONFIGURATION

AJAX_LOOKUP_CHANNELS = {
	# the simplest case, pass a DICT with the model and field to search against :
	'customer': ('customers.lookups', 'CustomerLookup'),  # dict(model='customers.customer', search_field='first_name'),
	'order': ('orders.lookups', 'OrderLookup'),

	# or write a custom search channel and specify that using a TUPLE
	# 'contact' : ('peoplez.lookups', 'ContactLookup'),
	# this specifies to look for the class `ContactLookup` in the `peoplez.lookups` module
}

CRISPY_TEMPLATE_PACK = 'bootstrap3'  # django crispy forms

CRON_EMAIL_NOTIFICATION_LIST = [
	'emil@furnitalia.com',
	'lana@furnitalia.com',
	'd.aks@furnitalia.com',
	'pearl@furnitalia.com',
	'ruth@furnitalia.com',
	'jenn@furnitalia.com',
]

KRONOS_POSTFIX = '> /dev/null 2>&1'

# Default settings
BOOTSTRAP3 = {

	# The URL to the jQuery JavaScript file
	'jquery_url': '//code.jquery.com/jquery.min.js',

	# The Bootstrap base URL
	'base_url': '//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/',

	# The complete URL to the Bootstrap CSS file (None means derive it from base_url)
	'css_url': None,

	# The complete URL to the Bootstrap CSS file (None means no theme)
	'theme_url': None,

	# The complete URL to the Bootstrap JavaScript file (None means derive it from base_url)
	'javascript_url': None,

	# Put JavaScript in the HEAD section of the HTML document (only relevant if you use bootstrap3.html)
	'javascript_in_head': False,

	# Include jQuery with Bootstrap JavaScript (affects django-bootstrap3 template tags)
	'include_jquery': False,

	# Label class to use in horizontal forms
	'horizontal_label_class': 'col-md-3',

	# Field class to use in horizontal forms
	'horizontal_field_class': 'col-md-9',

	# Set HTML required attribute on required fields
	'set_required': True,

	# Set HTML disabled attribute on disabled fields
	'set_disabled': False,

	# Set placeholder attributes to label if no placeholder is provided
	'set_placeholder': True,

	# Class to indicate required (better to set this in your Django form)
	'required_css_class': '',

	# Class to indicate error (better to set this in your Django form)
	'error_css_class': 'has-error',

	# Class to indicate success, meaning the field has valid input (better to set this in your Django form)
	'success_css_class': 'has-success',

	# Renderers (only set these if you have studied the source and understand the inner workings)
	'formset_renderers': {
		'default': 'bootstrap3.renderers.FormsetRenderer',
	},
	'form_renderers': {
		'default': 'bootstrap3.renderers.FormRenderer',
	},
	'field_renderers': {
		'default': 'bootstrap3.renderers.FieldRenderer',
		'inline': 'bootstrap3.renderers.InlineFieldRenderer',
	},
}

### FINANCIAL SETTINGS ###
COMMISSION_PERCENT = 0.025

ORDER_FORMAT_REGEX = '(SO|SR|DR)-([0-9]{5})'
ORDER_FORMAT_DESC = '<"SO" or "SR" or "DR">-<5 digits>. Examples: SO-10009 or SR-31000 or DR-10005'

# Date FOrmat
DATE_FORMAT_SHORT = 'j F, Y'
DATE_FORMAT_STANDARD = 'm/d/Y'
