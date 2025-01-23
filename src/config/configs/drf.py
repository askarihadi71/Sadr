
REST_FRAMEWORK = {
	'DEFAULT_PERMISSION_CLASSES': [
		'rest_framework.permissions.IsAuthenticated',
	],
	 'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
	# 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
	# 'DEFAULT_PAGINATION_CLASS': 'Base.api.pagination.StandardPagedResult',
	# 'PAGE_SIZE': 10,
	# 'MAX_PAGE_SIZE': 10,
	'DEFAULT_AUTHENTICATION_CLASSES': [
		# 'rest_framework.authentication.BasicAuthentication',
		'rest_framework.authentication.SessionAuthentication',
		'rest_framework_simplejwt.authentication.JWTAuthentication',
	],
	'EXCEPTION_HANDLER': 'extensions.drf.custom_exception_handler',
}