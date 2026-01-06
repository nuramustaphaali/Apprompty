# projects/constants.py

# The strict order of data collection
FLOW_STAGES = [
    'intent',       # What is the app?
    'platform',     # Mobile/Web/Desktop?
    'ui_ux',        # Design preferences
    'tech_stack',   # Preferred technologies
    'quality',      # Testing/Deployment needs
]

# Helper to check valid stages
VALID_STAGES = set(FLOW_STAGES)