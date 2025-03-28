from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import FormView, TemplateView

from app_prime_league.models import Channel
from bots.messages.custom_notification import validate_template
from core.github import GitHub
from quicklinks_admin.send_teams_message.jobs import EnqueueMessagesJob, VersionUpdateMessage


class MessageForm(forms.Form):
    message_template = forms.CharField(widget=forms.Textarea(attrs={'rows': 20, 'cols': 100}))

    def clean_message_template(self):
        message_template = self.cleaned_data['message_template']
        rendered_message = validate_template(
            VersionUpdateMessage,
            message_template,
            github=GitHub.latest_version(),
            website=settings.SITE_ID,
        )
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
        context["example_channel_ids"] = settings.EXAMPLE_CHANNEL_IDS
        return context

    def post(self, request, *args, **kwargs):
        if 'message_template' not in request.session:
            return redirect("admin:send-teams-message:send-teams-message")
        is_test_message = 'channel_ids' in request.POST
        if is_test_message:
            try:
                channel_ids = request.POST['channel_ids']
                channel_ids = [int(x) for x in channel_ids.split(',')]
                channels = Channel.objects.get_channels_by_ids(channel_ids).values_list('id', flat=True)
                if not channels:
                    raise Channel.DoesNotExist
            except (Channel.DoesNotExist, ValueError):
                messages.add_message(self.request, messages.ERROR, "I haven't found any channels with the given IDs.")
                return redirect("admin:send-teams-message:confirm-teams-message")
            else:
                message_template = request.session.get('message_template')
                EnqueueMessagesJob(message_template=message_template, channel_ids=channels).enqueue()
                messages.add_message(self.request, messages.SUCCESS, 'Test messages have been queued')
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
