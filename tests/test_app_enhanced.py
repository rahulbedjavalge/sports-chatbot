import unittest
import json
from backend.app_enhanced import app

class SportsChatbotTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def post_chat(self, message):
        return self.client.post('/chat',
            data=json.dumps({'message': message}),
            content_type='application/json')

    def test_score_intent(self):
        resp = self.post_chat('What was the score of Alpha FC vs Beta United?')
        data = resp.get_json()
        self.assertEqual(data['intent'], 'score')
        self.assertIn('Alpha FC', data['response'])
        self.assertIn('Beta United', data['response'])

    def test_stadium_intent(self):
        resp = self.post_chat('Where was Alpha FC vs Beta United played?')
        data = resp.get_json()
        self.assertEqual(data['intent'], 'stadium')
        self.assertIn('Alpha Stadium', data['response'])

    def test_scorers_intent(self):
        resp = self.post_chat('Who scored in Alpha FC vs Beta United?')
        data = resp.get_json()
        self.assertEqual(data['intent'], 'scorers')
        self.assertIn('Scorers:', data['response'])

    def test_date_intent(self):
        resp = self.post_chat('When did Alpha FC play Beta United?')
        data = resp.get_json()
        self.assertEqual(data['intent'], 'date')
        self.assertIn('2024-11-01', data['response'])

    def test_tournament_intent(self):
        resp = self.post_chat('What tournament was Alpha FC vs Beta United?')
        data = resp.get_json()
        self.assertEqual(data['intent'], 'tournament')
        self.assertIn('City Cup', data['response'])

    def test_player_stats_intent(self):
        resp = self.post_chat('How many goals has Rodriguez scored?')
        data = resp.get_json()
        self.assertEqual(data['intent'], 'player_stats')
        self.assertIn('Rodriguez', data['response'])

    def test_team_ranking_intent(self):
        resp = self.post_chat('What position is Alpha FC in the league?')
        data = resp.get_json()
        self.assertEqual(data['intent'], 'team_ranking')
        self.assertIn('Alpha FC', data['response'])
        self.assertIn('Premier League', data['response'])

    def test_head_to_head_intent(self):
        resp = self.post_chat('Head to head record Alpha FC vs Beta United?')
        data = resp.get_json()
        self.assertEqual(data['intent'], 'head_to_head')
        self.assertIn('Head-to-head:', data['response'])

    def test_league_top_scorer_intent(self):
        resp = self.post_chat('Who is the top scorer in the league?')
        data = resp.get_json()
        self.assertEqual(data['intent'], 'league_top_scorer')
        self.assertIn('top scorer', data['response'])

    def test_llm_fallback(self):
        resp = self.post_chat('Tell me about football history.')
        data = resp.get_json()
        self.assertEqual(data['method'], 'llm')
        self.assertTrue(len(data['response']) > 0)

if __name__ == '__main__':
    unittest.main()
