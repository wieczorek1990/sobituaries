from django import test
from django import urls
from rest_framework import status

from api import models


class CemeteryRegisterTestCase(test.TransactionTestCase):
    fixtures = ('CemeteryRegister',)

    def test_list(self):
        response = self.client.get(urls.reverse('cemetery-registers'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_create(self):
        self.assertEqual(models.CemeteryRegister.objects.count(), 3)
        response = self.client.post(urls.reverse('cemetery-registers'),
                                    data={
                                        'title': 'Test cemetery register',
                                        'description': 'This is a test cemetery register.'
                                    })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.CemeteryRegister.objects.count(), 3 + 1)

    def test_search(self):
        search = 'Poznań'
        response = self.client.get(urls.reverse('cemetery-registers') + f'?search={search}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_retrieve(self):
        cemetery_register = models.CemeteryRegister.objects.first()
        slug = cemetery_register.slug
        response = self.client.get(urls.reverse('cemetery-register-retrieve', kwargs={'slug': slug}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['slug'], slug)
