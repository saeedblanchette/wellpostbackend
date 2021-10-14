from django.apps import AppConfig

class WillpostConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'willpost'
    def ready(self):
        from django_q.tasks import schedule
        from model_bakery import baker
        from django.contrib.auth import get_user_model

        from datetime import timedelta
        from django.utils import timezone
        schedule('willpost.service.tasks', schedule_type='D')
        # baker.make('willpost.User',last_existence_confirmation=(timezone.now()+timedelta(days=-1)),is_active=True,_quantity=5)
       

        # print(' user count =>',get_user_model().objects.all())
        # get_user_model().objects.create(email='said23@mail.com',username='mqld65q4ds64',is_active=True,last_existence_confirmation=(timezone.now()+timedelta(days=-1)))
        
