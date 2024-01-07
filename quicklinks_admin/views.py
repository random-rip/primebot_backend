from django import forms
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView

from app_prime_league.models import Team
from bots.messages import NotificationToTeamMessage


class MessageForm(forms.Form):
    message = forms.CharField(label='Message', max_length=5000, widget=forms.Textarea)

    def clean_message(self):
        msg = self.cleaned_data['message']
        team = Team(name="Test Team", language="de")
        try:
            rendered_message = NotificationToTeamMessage(custom_message=msg, team=team).generate_message()
        except Exception as e:
            print(e)
            raise ValidationError("Could not render message")
        else:
            self.cleaned_data['message'] = rendered_message
        raise ValidationError("Message is not valid")

    def enqueue_messages(self):
        msg = self.cleaned_data['message']
        print(msg)
        # teams = Team.objects.get_registered_teams()
        # for team in teams:
        #     try:
        #         print(team)
        #         collector = MessageCollector(team)
        #         collector.dispatch(msg_class=NotificationToTeamMessage, custom_message=message)
        #     except Exception as e:
        #         print(e)


# TODO Verification Form
# TODO Enqueue


@method_decorator(staff_member_required, name='dispatch')
class TeamsMessageView(FormView):
    template_name = "teams_message.html"
    form_class = MessageForm
    success_url = reverse_lazy("admin:teams-message")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        admin_site_context = admin.site.each_context(self.request)
        context.update(admin_site_context)
        return context

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        messages.add_message(self.request, messages.INFO, 'Car has been sold')
        form.send_email()
        return super().form_valid(form)
