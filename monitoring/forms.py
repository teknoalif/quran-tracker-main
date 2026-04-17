from django import forms
from .models import LaporanBacaan

class LaporanForm(forms.ModelForm):
    class Meta:
        model = LaporanBacaan
        fields = ['santri', 'halaman_target', 'halaman_awal', 'halaman_akhir', 'durasi_menit', 'catatan']
        widgets = {
            'santri': forms.Select(attrs={'class': 'form-select'}),
            'halaman_target': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Target Hal'}),
            'halaman_awal': forms.NumberInput(attrs={'class': 'form-control'}),
            'halaman_akhir': forms.NumberInput(attrs={'class': 'form-control'}),
            'durasi_menit': forms.NumberInput(attrs={'class': 'form-control'}),
            'catatan': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }
