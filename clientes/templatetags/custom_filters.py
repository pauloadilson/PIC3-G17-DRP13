from django import template
import re

register = template.Library()
print("Custom filters carregados com sucesso!")


@register.filter
def format_phone(value):
    """Formata o telefone de '18965264938' para '(18) 96526-4938'."""
    pattern = r"(\d{2})(\d{5})(\d{4})"
    result = re.sub(pattern, r"(\1) \2-\3", value)
    return result
