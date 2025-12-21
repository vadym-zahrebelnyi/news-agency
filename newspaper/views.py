from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.views import generic
from django.urls import reverse_lazy

from .models import Topic, Article

from .forms import (
    TopicSearchForm,
    RedactorSearchForm
)


Redactor = get_user_model()

class IndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = "newspaper/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["num_topics"] = Topic.objects.count()
        context["num_redactors"] = Redactor.objects.count()
        context["num_articles"] = Article.objects.count()

        context["latest_articles"] = (
            Article.objects
            .only("title", "published_date")
            .prefetch_related("topics")
            .order_by("-published_date")[:5]
        )
        context["top_redactors"] = (
            Redactor.objects
            .only("username", "first_name", "last_name")
            .annotate(num_papers=Count("articles"))
            .order_by("-num_papers")[:3]
        )

        return context


class TopicListView(LoginRequiredMixin, generic.ListView):
    model = Topic
    paginate_by = 5

    def get_queryset(self):
        queryset = Topic.objects.all()
        form = TopicSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(
                name__icontains=form.cleaned_data["name"]
            )
        return queryset

    def get_context_data(
            self, *, object_list=None, **kwargs
    ):
        context = super(TopicListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = TopicSearchForm(
            initial={"name": name}
        )
        return context


class TopicCreateView(LoginRequiredMixin, generic.CreateView):
    model = Topic
    fields = "__all__"
    success_url = reverse_lazy("newspaper:topic-list")


class TopicUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Topic
    fields = "__all__"
    success_url = reverse_lazy("newspaper:topic-list")


class TopicDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Topic
    success_url = reverse_lazy("newspaper:topic-list")


class RedactorListView(LoginRequiredMixin, generic.ListView):
    model = Redactor
    paginate_by = 5


    def get_queryset(self):
        queryset = Redactor.objects.all()
        username = self.request.GET.get("username")
        if username:
            return queryset.filter(username__icontains=username)
        return queryset.order_by("username")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.request.GET.get("username", "")
        context["search_form"] = RedactorSearchForm(initial={"username": username})
        return context


class RedactorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Redactor
    queryset = Redactor.objects.prefetch_related("articles__topics")