# from django.db.models.signals import post_save, pre_save
# from django.dispatch import receiver
# from .models import User, UserProfile, LoggedInUser
# from django.contrib.auth import user_logged_in, user_logged_out

# @receiver(post_save, sender=User)    
# def post_save_create_profile_receiver(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)
#     else:
#         try:
#             profile = UserProfile.objects.get(user=instance)
#             profile.save()
#         except:
#             UserProfile.objects.create(user=instance)


# @receiver(pre_save, sender=User)
# def pre_save_profile_receiver(sender, instance, **kwargs):
#     pass

# post_save.connect(post_save_create_profile_receiver, sender=User)

# @receiver(user_logged_in)
# def on_user_logged_in(sender, **kwargs):
#     LoggedInUser.objects.get_or_create(user=kwargs.get('user'))

# @receiver(user_logged_out)
# def on_user_logged_out(sender, **kwargs):
#     LoggedInUser.objects.filter(user=kwargs.get('user')).delete()    