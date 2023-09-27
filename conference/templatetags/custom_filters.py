import os

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
