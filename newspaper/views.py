from django.db.models import Count
from django.views import generic
from .models import Topic, Redactor, Newspaper

class IndexView(generic.TemplateView):
    template_name = "newspaper/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["num_topics"] = Topic.objects.count()
        context["num_redactors"] = Redactor.objects.count()
        context["num_newspapers"] = Newspaper.objects.count()

        context["latest_newspapers"] = (
            Newspaper.objects
            .only("title", "published_date")
            .prefetch_related("topics")
            .order_by("-published_date")[:5]
        )
        context["top_redactors"] = (
            Redactor.objects
            .only("username", "first_name", "last_name")
            .annotate(num_papers=Count("newspapers"))
            .order_by("-num_papers")[:3]
        )

        return context
