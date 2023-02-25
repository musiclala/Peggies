from django import forms


class ReportsForm(forms.Form):

    date_start = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Дата начала периода')
    date_finish = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Дата конца периода')
