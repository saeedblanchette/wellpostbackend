from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.conf import settings 
class DefaultAccountAdapterCustom(DefaultAccountAdapter):

    def get_email_confirmation_url(self, request, emailconfirmation):
    
        return settings.URL_FRONT+'/verify-email/'+emailconfirmation.key
    # def send_mail(self, template_prefix, email, context):
    #     # print(' template_prefix ---',context)
    #     # print(' template_prefix ---',self.request)
    #     # if(context['activate_url'].index('registration/account-confirm-email')>0):
    #         # context['activate_url']=context['activate_url'].replace()
    #     msg = self.render_mail(template_prefix, email, context)
    #     msg.send()
