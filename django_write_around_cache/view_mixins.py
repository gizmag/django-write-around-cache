class WriteAroundCacheMixin(object):
    cache_modes = {'*': 'standard'}

    def get_context_data(self, *args, **kwargs):
        context = super(WriteAroundCacheMixin, self).get_context_data(*args, **kwargs)
        context['cache_modes'] = self.cache_modes
        return context
