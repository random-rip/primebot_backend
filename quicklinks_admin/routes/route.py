from django.views.generic import TemplateView


class QuicklinkView(TemplateView):
    template_name = 'quicklinks_admin/quicklinks.html'


class TeamsMessageRoute(QuicklinkView):
    pass
