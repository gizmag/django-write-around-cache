class WriteAroundCacheMixin(object):
    cache_mode = 'standard'

    def get_context_data(self, *args, **kwargs):
        context = super(WriteAroundCacheMixin, self).get_context_data(*args, **kwargs)
        context['cache_mode'] = self.cache_mode
        return context
