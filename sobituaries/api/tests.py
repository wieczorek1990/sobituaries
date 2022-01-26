import mock
from datetime import datetime

from django import test
from django import urls
from django.utils import timezone
from rest_framework import status

from api import models


FAKE_DATETIME_NOW = timezone.now().replace(year=2022, month=1, day=17, hour=12, minute=0, second=0, microsecond=0)


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


class SlugsMixin:
    def setUp(self):
        self.cemetery_register_slug = 'parafia-sw-wawrzynca'
        self.obituary_notice_slug = 'radosaw-nowak-mgrr'


@mock.patch('django.utils.timezone.now', return_value=FAKE_DATETIME_NOW)
class ObituaryNoticeTestCase(SlugsMixin, test.TransactionTestCase):
    fixtures = ('CemeteryRegister', 'ObituaryNotice')

    def setUp(self):
        super().setUp()
        self.cemetery_register = models.CemeteryRegister.objects.get(slug=self.cemetery_register_slug)

    def test_list(self, mock_now):
        response = self.client.get(urls.reverse('obituary-notices', kwargs={
            'slug': self.cemetery_register_slug,
        }))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_create(self, mock_now):
        self.assertEqual(models.ObituaryNotice.objects.count(), 2)
        response = self.client.post(urls.reverse('obituary-notices', kwargs={
            'slug': self.cemetery_register_slug,
        }), data={
            # 'cemetery_register': self.cemetery_register.id,

            'death_date': '2022-01-17',
            'titles': 'kochany Mąż, nasz Ojciec, Syn, Brat, Szwagier i Wujek',
            'first_name': 'Jan',
            'last_name': 'Nowak',
            'years_lived': 84,
            'holy_mass_datetime': FAKE_DATETIME_NOW.replace(day=21),
            'holy_mass_place': 'kościele Św. Wawrzyńca w Pniewach',
            'rosary_time': '11:30',
            'rosary_place': 'w kościele',
            'body_or_ashes': 'body',
            'funeral_place': 'cmentarzu parafialnym',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.ObituaryNotice.objects.count(), 2 + 1)

    def test_retrieve(self, mock_now):
        response = self.client.get(urls.reverse('obituary-notice-retrieve', kwargs={
            'cemetery_register_slug': self.cemetery_register_slug,
            'obituary_notice_slug': self.obituary_notice_slug,
        }))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_sample(self, mock_now):
        response = self.client.get(urls.reverse('obituary-notice-retrieve-sample', kwargs={
            'cemetery_register_slug': 'sample',
            'obituary_notice_slug': 'sample',
        }))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ReportTestCase(SlugsMixin, test.TransactionTestCase):
    fixtures = ('CemeteryRegister', 'ObituaryNotice')

    def test_create(self):
        self.assertEqual(models.Report.objects.count(), 0)
        response = self.client.post(urls.reverse('report-create'), data={
            'category': models.Report.Category.CEMETERY_REGISTER,
            'slug': self.cemetery_register_slug,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Report.objects.count(), 1)
        response = self.client.post(urls.reverse('report-create'), data={
            'category': models.Report.Category.OBITUARY_NOTICE,
            'slug': self.obituary_notice_slug,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Report.objects.count(), 2)


class PaymentTestCase(SlugsMixin, test.TransactionTestCase):
    fixtures = ('CemeteryRegister', 'ObituaryNotice')

    @staticmethod
    def assertEndswith(hay, needle):
        return hay.endswith(needle)

    def test_payment(self):
        # Already paid
        response = self.client.get(urls.reverse('obituary-notice-stripe-payment', kwargs={
            'cemetery_register_slug': self.cemetery_register_slug,
            'obituary_notice_slug': self.obituary_notice_slug,
        }))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Mark as unpaid and create payment
        obituary_notice = models.ObituaryNotice.objects.get(slug=self.obituary_notice_slug)
        obituary_notice.paid_on = None
        obituary_notice.save()
        response = self.client.get(urls.reverse('obituary-notice-stripe-payment', kwargs={
            'cemetery_register_slug': self.cemetery_register_slug,
            'obituary_notice_slug': self.obituary_notice_slug,
        }))
        self.assertEqual(response.status_code, status.HTTP_303_SEE_OTHER)
        self.assertTrue(models.ObituaryNoticePayment.objects.filter(obituary_notice=obituary_notice).exists())

        # Bad token
        response = self.client.get(urls.reverse('obituary-notice-stripe-payment-success', kwargs={
            'cemetery_register_slug': self.cemetery_register_slug,
            'obituary_notice_slug': self.obituary_notice_slug,
            'token': 'bad_token',
        }))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEndswith(response.url, '#/stripe/cancel/')

        # Correct token and unpaid
        payment = models.ObituaryNoticePayment.objects.get(obituary_notice=obituary_notice)
        response = self.client.get(urls.reverse('obituary-notice-stripe-payment-success', kwargs={
            'cemetery_register_slug': self.cemetery_register_slug,
            'obituary_notice_slug': self.obituary_notice_slug,
            'token': payment.token,
        }))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEndswith(response.url, '#/stripe/success/')
        obituary_notice.refresh_from_db()
        self.assertIsInstance(obituary_notice.paid_on, datetime)

        # Correct token and paid
        response = self.client.get(urls.reverse('obituary-notice-stripe-payment-success', kwargs={
            'cemetery_register_slug': self.cemetery_register_slug,
            'obituary_notice_slug': self.obituary_notice_slug,
            'token': payment.token,
        }))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEndswith(response.url, '#/stripe/cancel/')
