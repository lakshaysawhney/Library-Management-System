from django import forms
from .models import Book, UserProfile
from django.contrib.auth.forms import UserCreationForm

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'available']

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'autocomplete': 'tel'}))
    user_type = forms.ChoiceField(choices=[('librarian', 'Librarian'), ('student', 'Student')])

    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'phone_number', 'password1', 'password2', 'user_type')
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'username'}),
            'password1': forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
            'password2': forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.startswith('+'):
            phone_number = '+91' + phone_number  # Assuming the default country code is +91 for India
        if UserProfile.objects.filter(phone_number=phone_number).exists():  # Directly query UserProfile
            raise forms.ValidationError("User with this Phone number already exists.")
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']

        # Ensure phone number is in the correct format
        if not user.phone_number.startswith('+'):
            user.phone_number = '+91' + user.phone_number  # Assuming the default country code is +91 for India

        if commit:
            user.save()

            # Handle the user_type field
            if self.cleaned_data['user_type'] == 'librarian':
                user.is_librarian = True
            else:
                user.is_student = True

            user.save()

        return user