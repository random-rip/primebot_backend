from django import forms
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import FormView, TemplateView

from app_prime_league.models import Team
from bots.messages.custom_notification import validate_template
from quicklinks_admin.send_teams_message.jobs import EnqueueMessagesJob, VersionUpdateMessage


class MessageForm(forms.Form):
    message_template = forms.CharField(widget=forms.Textarea(attrs={'rows': 20, 'cols': 100}))

    def clean_message_template(self):
        message_template = self.cleaned_data['message_template']
        rendered_message = validate_template(VersionUpdateMessage, message_template)
        self.cleaned_data['rendered_message'] = rendered_message
        return message_template


@method_decorator(staff_member_required, name='dispatch')
class TeamsMessageView(FormView):
    template_name = "send_teams_message/send_teams_message.html"
    form_class = MessageForm
    success_url = reverse_lazy("admin:send-teams-message:confirm-teams-message")

    def get_initial(self):
        message_template = self.request.session.get('message_template', None)
        if not message_template:
            message_template = VersionUpdateMessage.template
        return {
            'message_template': message_template,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        admin_site_context = admin.site.each_context(self.request)
        context.update(admin_site_context)
        return context

    def form_valid(self, form):
        self.request.session['message_template'] = form.cleaned_data['message_template']
        self.request.session['rendered_message'] = form.cleaned_data['rendered_message']
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class ConfirmTeamsMessageView(TemplateView):
    template_name = "send_teams_message/confirm_teams_message.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        admin_site_context = admin.site.each_context(self.request)
        context.update(admin_site_context)
        context['message_template'] = self.request.session.get('message_template', '')
        context['rendered_message'] = self.request.session.get('rendered_message', '')
        return context

    def post(self, request, *args, **kwargs):
        if 'message_template' not in request.session:
            return redirect("admin:send-teams-message:send-teams-message")
        is_test_message = 'team_id' in request.POST
        if is_test_message:
            try:
                team_id = request.POST['team_id']
                team = Team.objects.get_registered_teams().get(id=int(team_id))
            except (Team.DoesNotExist, ValueError):
                messages.add_message(self.request, messages.ERROR, 'Invalid team_id')
                return redirect("admin:send-teams-message:confirm-teams-message")
            else:
                message_template = request.session.get('message_template')
                EnqueueMessagesJob(message_template=message_template, team_ids=[team.id]).execute()
                messages.add_message(self.request, messages.SUCCESS, 'Test message has been sent')
                return redirect("admin:send-teams-message:confirm-teams-message")

        del request.session['rendered_message']
        message_template = request.session.pop('message_template')
        is_async, _ = EnqueueMessagesJob(message_template=message_template).enqueue()
        if not is_async:
            messages.add_message(self.request, messages.SUCCESS, 'Messages have been sent synchronously')
        else:
            messages.add_message(self.request, messages.SUCCESS, 'Messages have been enqueued')
        return redirect("admin:send-teams-message:send-teams-message")


@method_decorator(staff_member_required, name='dispatch')
class ClearTeamsMessageView(View):
    def post(self, request, *args, **kwargs):
        request.session.pop('message_template', None)
        request.session.pop('rendered_message', None)
        return redirect(reverse('admin:send-teams-message:send-teams-message'))
