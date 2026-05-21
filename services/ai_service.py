class AIService:
    """
    A stateless AI service that performs LLM analysis of visit notes.
    """

    HIGH_RISK_WORDS = ['angry', 'escalate', 'broken', 'refused', 'cancel', 'unsafe', 'terrible', 'fraud']
    MEDIUM_RISK_WORDS = ['delayed', 'reschedule', 'confused', 'missing', 'issue', 'complain', 'late']

    @classmethod
    def generate_insights(cls, notes: str) -> dict:
        """
        Analyzes visit notes and returns a dictionary with summary, 
        recommendation, and a risk flag.
        """
        if not notes:
            return {
                'summary': 'No notes provided.',
                'recommendation': 'Follow up to get more details.',
                'risk_flag': 'Low'
            }

        notes_lower = notes.lower()

        # Check for high risk
        if any(word in notes_lower for word in cls.HIGH_RISK_WORDS):
            return {
                'summary': 'The visit highlighted severe issues or an extremely dissatisfied customer.',
                'recommendation': 'Immediate escalation to Regional Manager required.',
                'risk_flag': 'High'
            }

        # Check for medium risk
        if any(word in notes_lower for word in cls.MEDIUM_RISK_WORDS):
            return {
                'summary': 'The visit had some minor issues or delays.',
                'recommendation': 'Follow up within 48 hours to ensure resolution.',
                'risk_flag': 'Medium'
            }

        # Default low risk
        return {
            'summary': 'The visit was routine and successful with no major issues reported.',
            'recommendation': 'Proceed with standard timeline.',
            'risk_flag': 'Low'
        }
