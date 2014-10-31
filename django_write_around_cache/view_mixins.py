class WriteAroundCacheMixin(object):
    cache_mode = 'standard'

    def get_context_data(self):
        context = super(WriteAroundCacheMixin, self).get_context_data()
        context['cache_mode'] = self.cache_mode
        return context
