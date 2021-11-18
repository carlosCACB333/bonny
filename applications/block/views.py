from .serializers import ProfileSerializer
from .models import User
from rest_framework import viewsets

# Create your views here.
class EmployeUserViewset(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = User.objects.all()
