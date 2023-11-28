import os, re

from django import template

register = template.Library()

@register.filter
def basename(value):
    return os.path.basename(value.file.name)

@register.filter
def replace_spaces(value):
    return value.replace(" ", "")


@register.filter
def update_variable(new_value):
    return new_value

@register.filter(name='is_image')
def is_image(value):
    # Extract the file extension from the file name
    file_extension = value.split('.')[-1].lower()
    
    # Check if it's a JPG or PNG
    return file_extension in ['jpg', 'jpeg', 'png']


@register.filter
def filename(value):
    return os.path.basename(value)

@register.filter(name='has_role')
def has_role(user, role_name):
    return user.roles.filter(name=role_name).exists()


@register.filter
def revision_number(value):
    # Use regular expression to find the numeric part after '_R' at the end
    match = re.search(r'_R(\d+)$', value)

    # If a numeric part is found, convert it to an integer; otherwise, return 0
    return int(match.group(1)) if match else 0

@register.filter
def original_journal_id(input_string):
    # Use regular expression to find the prefix before '_R' at the end
    match = re.search(r'^(.*?)(?:_R\d+)?$', input_string)

    # If a prefix is found, return it; otherwise, return the entire string
    return match.group(1) if match else input_string


@register.filter
def previous_journal_id(input_string):
    # Use regular expression to find the prefix and '_R' part with digits
    match = re.search(r'^(.*?)(_R(\d+))?$', input_string)

    # If '_R' part is found, decrement the number; otherwise, return the entire string
    if match.group(2):
        number = int(match.group(3)) - 1
        return f"{match.group(1)}_R{number}" if number > 0 else match.group(1)
    else:
        return input_string
    
@register.filter(name='length')
def length(list):
    return len(list)    