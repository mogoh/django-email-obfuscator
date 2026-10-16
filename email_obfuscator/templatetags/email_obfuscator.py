from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


def obfuscate_html_entity(value):
    return ''.join(f'&#{ord(c)};' for c in value)

def obfuscate_js_concatenation(value):
    """
    https://spencermortensen.com/articles/email-obfuscation/#link-concatenation
    """
    # todo
    return value


METHODS = {
    'html_entity': obfuscate_html_entity,
    'js_concatenation': obfuscate_js_concatenation
}


def obfuscate_string(value):
    method = getattr(settings, 'EMAIL_OBFUSCATOR_METHOD', 'html_entity')
    func = METHODS.get(method)
    if func is None:
        raise ValueError(f'Unknown EMAIL_OBFUSCATOR_METHOD: {method!r}')
    return func(value)


@register.filter
@stringfilter
def obfuscate(value):
    return mark_safe(obfuscate_string(value))


@register.filter
@stringfilter
def obfuscate_mailto(value, text=False):
    mail = obfuscate_string(value)
    if text:
        link_text = text
        # Detect subject lines
        if ';' in text:
            args = text.split(';')
            link_text = args[0]
            subject = args[1]
            mail = mail + '?subject=' + subject
    else:
        link_text = mail
    return mark_safe('<a href="{0:s}{1:s}">{2:s}</a>'.format(
        obfuscate_string('mailto:'), mail, link_text))
