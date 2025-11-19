from django.contrib.auth import logout
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template.loader import get_template
from .models import Question, Choice
from django.template import loader, TemplateDoesNotExist
from django.urls import reverse
from django.views import generic
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import ChangeUserInfoForm
from .models import AdvUser
from django.views.generic import UpdateView
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import CreateView
from .forms import RegisterUserForm
from django.views.generic import TemplateView
from django.core.signing import BadSignature
from .utilities import signer
from django.views.generic import DeleteView
from django.contrib import messages

from .forms import CustomAuthenticationForm

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.order_by('-pub_date')


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'вы не сделали выбор'
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

class BBLoginView(LoginView):
    template_name = 'polls/login.html'
    authentication_form = CustomAuthenticationForm

    def form_valid(self, form):
        messages.success(self.request, f'Добро пожаловать, {form.get_user().username}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Неверное имя пользователя или пароль')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('profile')

def index(request):
    return HttpResponse("Главная страничка для опросов")

def other_page(request, page):
    try:
        template = get_template('polls/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))

@login_required
def profile(request):
    return render(request, 'polls/profile.html')

def logout_view(request):
    logout(request)
    return redirect('/')

class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'polls/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('polls:profile')
    success_message ='Личные данные пользователя изменены'

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)
    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)

class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'polls/password_change.html'
    success_url = reverse_lazy('polls:profile')
    success_message ='Пароль пользователя изменен'

class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'polls/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('polls:register_done')


class RegisterDoneView(TemplateView):
    template_name = 'polls/register_done.html'

def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'polls/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'polls/activation_done.html'
        user.is_activated = True
        user.is_active = True
        user.save()
    return render(request, template)

# выход
def user_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('polls:index')
#40 стр
class DeleteUserView (LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'polls/delete_user.html'
    success_url = reverse_lazy('polls:index')

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удален')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)



