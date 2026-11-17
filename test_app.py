"""
test_app.py
Comprehensive test suite verifying all routes, CRUD, safety checker, and APIs.
"""

import unittest
from datetime import date, timedelta
from app import create_app
from models import db, Medicine, DoseLog


class MediTrackTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            med = Medicine(
                name="TestAmoxicillin",
                generic_name="Amoxicillin Trihydrate",
                strength="500 mg",
                form="Capsule",
                purpose="Infection",
                instructions="Take with water",
                frequency="Once Daily",
                reminder_time="09:00",
                quantity=10,
                low_stock_threshold=5,
                start_date=date.today(),
                end_date=None,
                expiry_date=date.today() + timedelta(days=100)
            )
            db.session.add(med)
            db.session.commit()
            self.sample_med_id = med.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_dashboard(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Dashboard', res.data)
        self.assertIn(b'TestAmoxicillin', res.data)

    def test_medicines_list(self):
        res = self.client.get('/medicines')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'TestAmoxicillin', res.data)

    def test_medicine_detail(self):
        res = self.client.get(f'/medicines/{self.sample_med_id}')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'TestAmoxicillin', res.data)

    def test_medicine_add(self):
        res = self.client.post('/medicines/add', data={
            'name': 'NewUniqueMedicine',
            'generic_name': 'GenericNew',
            'strength': '10 mg',
            'form': 'Tablet',
            'purpose': 'Pain',
            'instructions': 'After food',
            'frequency': 'Once Daily',
            'reminder_time': '08:00',
            'quantity': '20',
            'low_stock_threshold': '5',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'expiry_date': (date.today() + timedelta(days=200)).strftime('%Y-%m-%d'),
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'NewUniqueMedicine', res.data)

    def test_medicine_edit(self):
        res = self.client.post(f'/medicines/{self.sample_med_id}/edit', data={
            'name': 'UpdatedAmoxicillinName',
            'generic_name': 'Amoxicillin',
            'strength': '250 mg',
            'form': 'Capsule',
            'purpose': 'Infection',
            'instructions': 'With food',
            'frequency': 'Twice Daily',
            'reminder_time': '09:00, 21:00',
            'quantity': '15',
            'low_stock_threshold': '5',
            'start_date': date.today().strftime('%Y-%m-%d'),
            'expiry_date': (date.today() + timedelta(days=100)).strftime('%Y-%m-%d'),
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'UpdatedAmoxicillinName', res.data)

    def test_medicine_delete(self):
        res = self.client.post(f'/medicines/{self.sample_med_id}/delete', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'have been removed', res.data)

    def test_reminders(self):
        res = self.client.get('/reminders')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Reminders', res.data)

    def test_reminders_mark(self):
        res = self.client.post('/reminders/mark', json={
            'medicine_id': self.sample_med_id,
            'scheduled_time': '09:00',
            'status': 'Taken'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])

    def test_safety_page(self):
        res = self.client.get('/safety')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Safety', res.data)

    def test_safety_check_json(self):
        res = self.client.post('/safety/check', json={
            'drug1': 'Warfarin',
            'drug2': 'Aspirin'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['interaction'])
        self.assertEqual(data['severity'], 'high')

    def test_safety_check_form(self):
        res = self.client.post('/safety', data={
            'custom_medicines': 'Warfarin, Aspirin'
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Analysis Results', res.data)

    def test_analytics(self):
        res = self.client.get('/analytics')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Analytics', res.data)

    def test_analytics_data(self):
        res = self.client.get('/analytics/data')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('doses_per_day', data)
        self.assertIn('medicine_by_form', data)
        self.assertIn('adherence_rate', data)
        self.assertIn('taken_vs_missed', data)

    def test_biology(self):
        res = self.client.get('/biology')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Biology', res.data)

    def test_about(self):
        res = self.client.get('/about')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'About', res.data)

    def test_api_medicines(self):
        res = self.client.get('/api/medicines')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_api_dashboard_stats(self):
        res = self.client.get('/api/dashboard-stats')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('total', data)
        self.assertIn('active', data)


if __name__ == '__main__':
    unittest.main()
