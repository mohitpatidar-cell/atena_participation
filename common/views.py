
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import ProviderSummaryUploadForm
from .tasks import process_provider_pdf


class ProviderSummaryUploadView(View):
    template_name = 'provider_summary_upload.html'
    success_url = reverse_lazy('provider_summary_upload')

    def get(self, request, *args, **kwargs):
        form = ProviderSummaryUploadForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ProviderSummaryUploadForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=True)

            # Celery task trigger
            process_provider_pdf.delay(instance.id)

            # Pass a status message to template
            status_message = "Data is extracting... Automation will start after extraction."

            return render(request, self.template_name, {
                'form': form,
                'status_message': status_message
            })

        return render(request, self.template_name, {'form': form})

# Create your views here.
class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')
    

