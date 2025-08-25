# import random
# import string
# from django.utils.text import slugify
#
#
# def random_string_generator(size=4, chars=string.ascii_lowercase + string.digits):
#     """1 usage new"""
#     return ''.join(random.choice(chars) for _ in range(size))
#
#
# def unique_slug_generator_employee(instance, new_slug=None):
#     """1 usage new"""
#     if new_slug is not None:
#         slug = new_slug
#     else:
#         full_name = f"{instance.first_name} {instance.last_name}"
#         slug = slugify(full_name)
#
#     Klass = instance.__class__
#     qs_exists = Klass.objects.filter(slug=slug).exists()
#
#     if qs_exists:
#         new_slug = f"{slug}-{random_string_generator(size=4)}"
#         return unique_slug_generator_employee(instance, new_slug=new_slug)
#
#     return slug