from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.views import generic
from django.urls import reverse_lazy

from .models import Topic, Article

from .forms import (
    TopicSearchForm,
    RedactorSearchForm,
    RedactorCreationForm,
    RedactorUpdateForm,
    ArticleSearchForm,
    ArticleForm,
)


Redactor = get_user_model()


class IndexView(generic.TemplateView):
    template_name = "newspaper/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["num_topics"] = Topic.objects.count()
        context["num_redactors"] = Redactor.objects.count()
        context["num_articles"] = Article.objects.count()

        context["latest_articles"] = Article.objects.prefetch_related(
            "topics", "publishers"
        ).order_by("-published_date")[:5]

        context["top_redactors"] = Redactor.objects.annotate(
            num_papers=Count("articles")
        ).order_by("-num_papers")[:3]

        context["popular_topics"] = Topic.objects.annotate(
            num_articles=Count("articles")
        ).order_by("-num_articles")[:5]

        return context


class TopicListView(LoginRequiredMixin, generic.ListView):
    model = Topic
    paginate_by = 5

    def get_queryset(self):
        queryset = Topic.objects.annotate(num_articles=Count("articles"))
        form = TopicSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TopicListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = TopicSearchForm(initial={"name": name})
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
        queryset = Redactor.objects.annotate(num_articles=Count("articles"))
        form = RedactorSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(
                username__icontains=form.cleaned_data["username"]
            )
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RedactorListView, self).get_context_data(**kwargs)
        username = self.request.GET.get("username", "")
        context["search_form"] = RedactorSearchForm(
            initial={"username": username}
        )
        return context


class RedactorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Redactor
    queryset = Redactor.objects.annotate(
        num_articles=Count("articles")
    ).prefetch_related("articles__topics")


class RedactorCreateView(UserPassesTestMixin, generic.CreateView):
    model = Redactor
    form_class = RedactorCreationForm

    raise_exception = True

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy("newspaper:redactor-list")
        return reverse_lazy("newspaper:index")

    def test_func(self):
        return (
            not self.request.user.is_authenticated
            or self.request.user.is_superuser
        )

    def form_valid(self, form):
        response = super().form_valid(form)

        if not self.request.user.is_authenticated:
            user = form.instance
            login(self.request, user)

        return response


class RedactorUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView
):
    model = Redactor
    form_class = RedactorUpdateForm

    def get_success_url(self):
        return reverse_lazy(
            "newspaper:redactor-detail", kwargs={"pk": self.object.pk}
        )

    def test_func(self):
        return (
            self.request.user.is_superuser
            or self.request.user == self.get_object()
        )


class RedactorDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView
):
    model = Redactor
    template_name = "newspaper/redactor_confirm_delete.html"
    success_url = reverse_lazy("newspaper:redactor-list")

    def test_func(self):
        return (
            self.request.user.is_superuser
            or self.request.user == self.get_object()
        )


class ArticleListView(LoginRequiredMixin, generic.ListView):
    model = Article
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        title = self.request.GET.get("title", "")
        context["search_form"] = ArticleSearchForm(initial={"title": title})
        return context

    def get_queryset(self):
        queryset = Article.objects.prefetch_related("topics", "publishers")
        form = ArticleSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(
                title__icontains=form.cleaned_data["title"]
            )
        return queryset


class ArticleDetailView(LoginRequiredMixin, generic.DetailView):
    model = Article
    queryset = Article.objects.prefetch_related("topics", "publishers")


class ArticleCreateView(LoginRequiredMixin, generic.CreateView):
    model = Article
    form_class = ArticleForm
    success_url = reverse_lazy("newspaper:article-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        article = form.save()
        article.publishers.add(self.request.user)
        return super(ArticleCreateView, self).form_valid(form)


class ArticleUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView
):
    model = Article
    form_class = ArticleForm
    success_url = reverse_lazy("newspaper:article-list")

    def test_func(self):
        cached_article = self.get_object()
        return (
            self.request.user.is_superuser
            or self.request.user in cached_article.publishers.all()
        )

    def get_object(self, queryset=None):
        if hasattr(self, 'cached_obj'):
            return self.cached_obj
        return super().get_object(queryset)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)


class ArticleDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView
):
    model = Article
    success_url = reverse_lazy("newspaper:article-list")

    def test_func(self):
        return (
            self.request.user.is_superuser
            or self.request.user in self.get_object().publishers.all()
        )
