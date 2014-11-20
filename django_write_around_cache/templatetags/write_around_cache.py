from __future__ import unicode_literals

from django.core.cache import caches, InvalidCacheBackendError
from ..utils import make_template_fragment_key
from django.template import Library, Node, TemplateSyntaxError, VariableDoesNotExist

register = Library()


class CacheNode(Node):
    def __init__(self, nodelist, mode_var, fragment_name, vary_on, cache_name):
        self.nodelist = nodelist
        self.mode_var = mode_var
        self.fragment_name = fragment_name
        self.vary_on = vary_on
        self.cache_name = cache_name

    def get_mode(self, context):
        try:
            mode = self.mode_var.resolve(context)
        except VariableDoesNotExist:
            raise TemplateSyntaxError('"cache" tag got an unknown variable: %r' % self.mode_var.var)

        if mode not in ('standard', 'overwrite'):
            raise TemplateSyntaxError('"cache" tag got an invalid mode value: %r' % mode)

        return mode

    def get_cache(self, context):
        if self.cache_name:
            try:
                cache_name = self.cache_name.resolve(context)
            except VariableDoesNotExist:
                raise TemplateSyntaxError('"cache" tag got an unknown variable: %r' % self.cache_name.var)
            try:
                fragment_cache = caches[cache_name]
            except InvalidCacheBackendError:
                raise TemplateSyntaxError('Invalid cache name specified for cache tag: %r' % cache_name)
        else:
            try:
                fragment_cache = caches['template_fragments']
            except InvalidCacheBackendError:
                fragment_cache = caches['default']

        return fragment_cache

    def render(self, context):
        mode = self.get_mode(context)
        fragment_cache = self.get_cache(context)

        vary_on = [var.resolve(context) for var in self.vary_on]
        cache_key = make_template_fragment_key(self.fragment_name, vary_on)

        if mode == 'standard':
            value = fragment_cache.get(cache_key)
            if value is None:
                value = self.nodelist.render(context)
                fragment_cache.set(cache_key, value)
        elif mode == 'overwrite':
            value = self.nodelist.render(context)
            fragment_cache.set(cache_key, value)

        return value


@register.tag('cache')
def do_cache(parser, token):
    """
    This will cache the contents of a template fragment until called with
    overwrite mode enabled.

    `mode` can be either `standard` or `overwrite`

    Usage::

        {% load cache %}
        {% cache [mode] [fragment_name] %}
            .. some expensive processing ..
        {% endcache %}

    This tag also supports varying by a list of arguments::

        {% load cache %}
        {% cache [mode] [fragment_name] [var1] [var2] .. %}
            .. some expensive processing ..
        {% endcache %}

    Optionally the cache to use may be specified thus::

        {% cache ....  using="cachename" %}

    Each unique set of arguments will result in a unique cache entry.
    """
    nodelist = parser.parse(('endcache',))
    parser.delete_first_token()
    tokens = token.split_contents()

    if len(tokens) < 3:
        raise TemplateSyntaxError("'%r' tag requires at least 2 arguments." % tokens[0])

    if len(tokens) > 3 and tokens[-1].startswith('using='):
        cache_name = parser.compile_filter(tokens[-1][len('using='):])
        tokens = tokens[:-1]
    else:
        cache_name = None
    return CacheNode(nodelist,
        parser.compile_filter(tokens[1]),
        tokens[2],  # fragment_name can't be a variable.
        [parser.compile_filter(t) for t in tokens[3:]],
        cache_name,
    )
