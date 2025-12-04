import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import Choice
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django.views import generic
from django.shortcuts import render
from django.template.loader import get_template
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from .forms import ChangeUserInfoForm, ChoiceFormSet
from .models import AdvUser, Question
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import CreateView
from .forms import RegisterUserForm
from django.views.generic.base import TemplateView
from django.views.generic import DeleteView
from django.contrib import messages
from .forms import QuestionForm
from django.utils import timezone


class LoginView(LoginView):
    template_name = 'polls/login.html'
    success_url = reverse_lazy('polls:profile')


@login_required
def profile(request):
    user_questions = request.user.authored_questions.all()
    return render(request, 'polls/profile.html', {
        'user': request.user,
        'questions': user_questions
    })


def logout_view(request):
    logout(request)
    return redirect('/')


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'polls/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('polls:profile')
    success_message = 'Личные данные пользователя изменены'

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class PasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'polls/password_change.html'
    success_url = reverse_lazy('polls:profile')
    success_message = 'Пароль пользователя изменен'


class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'polls/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('polls:index')


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'polls/delete_user.html'
    success_url = reverse_lazy('polls:index')

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        recent_date = timezone.now() - datetime.timedelta(minutes=5)
        if self.request.user.is_superuser:
            return Question.objects.order_by('-pub_date')
        else:
            return Question.objects.order_by('-pub_date').filter(pub_date__gte=recent_date)


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    context_object_name = 'question'

    def dispatch(self, request, *args, **kwargs):
        question_id = kwargs['pk']
        user_has_voted = request.session.get(f'voted_{question_id}')

        if user_has_voted:
            return redirect('polls:results', pk=question_id)

        return super().dispatch(request, *args, **kwargs)


@login_required
def create_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        formset = ChoiceFormSet(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.pub_date = timezone.now()
            question.save()
            formset.instance = question
            formset.save()
            return redirect('polls:index')
    else:
        form = QuestionForm()
        formset = ChoiceFormSet()
    return render(request, 'polls/create_question.html', {'form': form, 'formset': formset})


@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'Вы не сделали выбор'
        })
    else:
        user_has_voted = request.session.get(f'voted_{question.id}')
        if user_has_voted:
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
        else:
            selected_choice.votes += 1
            selected_choice.save()
            request.session[f'voted_{question.id}'] = True
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.object
        total_votes = sum(choice.votes for choice in question.choice_set.all())
        choices_percent = []
        for choice in question.choice_set.all():
            if total_votes > 0:
                percent = (choice.votes / total_votes) * 100
            else:
                percent = 0.0
            choices_percent.append({
            'choice': choice,
            'percent': round(percent, 1)
            })

        context['choices_percent'] = choices_percent
        return context