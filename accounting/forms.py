from django import forms
from django.core.exceptions import ValidationError

class TransactionUploadForm(forms.Form):
    file = forms.FileField(
        label='은행 거래 내역 CSV 파일',
        help_text='CSV 파일을 선택해주세요',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv',
            'required': True
        })
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # 파일 확장자 검증
            if not file.name.endswith('.csv'):
                raise ValidationError('CSV 파일만 업로드 가능합니다.')
            
            # 파일 크기 검증 (10MB 제한)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('파일 크기는 10MB 이하여야 합니다.')
        
        return file 