def make_template_fragment_key(fragment_name, vary_on):
	key = 'template_cache:{}'.format(fragment_name)
	for var in vary_on:
		key += ':{}'.format(var)

	return key