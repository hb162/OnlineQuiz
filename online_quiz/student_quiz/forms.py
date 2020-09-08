from django import forms


class StudentSignIn(forms.Form):
    room_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'fadeIn third zero-raduis', 'type': 'text', 'name': 'email', 'id': 'room'}),
        label="ROOM NAME",
    )
