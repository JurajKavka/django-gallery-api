# -*- coding: utf-8 -*-
import logging
from django import forms
from .models import Image


logger = logging.getLogger(__name__)


class ImageForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = ['gallery', 'file']
