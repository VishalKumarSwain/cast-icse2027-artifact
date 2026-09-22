from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from .models import Fruit


class FruitListView(LoginRequiredMixin, generic.ListView):
    model = Fruit
    template_name = "fruit_list.html"
    context_object_name = "fruits"
    ordering = [
        "-updated_at"
    ]  # Assuming 'updated_at' is the field for last update time


class FruitCreateView(LoginRequiredMixin, generic.CreateView):
    model = Fruit
    template_name = "fruit_form.html"
    fields = ["name", "color", "quantity"]  # Adjust fields as necessary
    success_url = reverse_lazy("fruit_list")


class FruitUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Fruit
    template_name = "fruit_form.html"
    fields = ["name", "color", "quantity"]  # Adjust fields as necessary
    success_url = reverse_lazy("fruit_list")


class FruitDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Fruit
    template_name = "fruit_confirm_delete.html"
    success_url = reverse_lazy("fruit_list")
