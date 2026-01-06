# projects/questions.py

QUESTION_BANK = {
    'intent': {
        'title': 'App Intent',
        'description': 'Let’s define the core purpose of your application.',
        'questions': [
            {'id': 'app_type', 'text': 'What type of application do you want to build?', 'type': 'text'},
            {'id': 'problem', 'text': 'What problem does this app solve?', 'type': 'textarea'},
            {'id': 'target_user', 'text': 'Who is the target user?', 'type': 'text'},
            {'id': 'scope', 'text': 'Is this an MVP or full production app?', 'type': 'select', 'options': ['MVP', 'Full Production', 'Prototype']},
            {'id': 'purpose', 'text': 'Is this for learning, business, or internal use?', 'type': 'select', 'options': ['Learning', 'Business', 'Internal Tool']}
        ]
    },
    'platform': {
        'title': 'Platform & Devices',
        'description': 'Where will your users access this application?',
        'questions': [
            {'id': 'platforms', 'text': 'Which platforms should this app support?', 'type': 'checkbox', 'options': ['Web', 'Mobile', 'Desktop']},
            {'id': 'priority', 'text': 'Mobile-first or desktop-first?', 'type': 'select', 'options': ['Mobile-First', 'Desktop-First', 'Responsive']},
            {'id': 'offline', 'text': 'Offline support needed?', 'type': 'boolean'},
            {'id': 'performance', 'text': 'Performance priority level?', 'type': 'select', 'options': ['Standard', 'High', 'Critical (Real-time)']}
        ]
    },
    'ui_ux': {
        'title': 'UI / UX Preferences',
        'description': 'How should the application look and feel?',
        'questions': [
            {'id': 'navigation', 'text': 'Preferred navigation style?', 'type': 'select', 'options': ['Sidebar', 'Top Navbar', 'Bottom Tab Bar']},
            {'id': 'dark_mode', 'text': 'Dark mode required?', 'type': 'boolean'},
            {'id': 'style', 'text': 'UI style preference?', 'type': 'select', 'options': ['Minimal', 'Dashboard', 'Content-Heavy', 'Corporate']},
            {'id': 'inspiration', 'text': 'Any reference apps or style inspirations?', 'type': 'text'}
        ]
    },
    'tech_stack': {
        'title': 'Technical Decisions',
        'description': 'Let’s lock in the engineering constraints.',
        'questions': [
            {
                'id': 'backend_style', 
                'text': 'Preferred backend style?', 
                'type': 'select', 
                'options': [
                    'Python (Django Monolith)', 
                    'Python (Django + Ninja/DRF)', 
                    'Python (FastAPI)',
                    'Node.js (Express/NestJS)',
                    'PHP (Laravel)',
                    'Go (Gin/Echo)',
                    'Java (Spring Boot)',
                    'No Preference (AI Recommend)'
                ]
            },
            {'id': 'auth', 'text': 'Authentication needed?', 'type': 'boolean'},
            {'id': 'roles', 'text': 'User roles required?', 'type': 'text', 'placeholder': 'e.g., Admin, Editor, Viewer'},
            {'id': 'integrations', 'text': 'External integrations needed?', 'type': 'text', 'placeholder': 'e.g., Stripe, AWS, Twilio'}
        ]
    },
    'quality': {
        'title': 'Quality & Delivery',
        'description': 'Final checks before architecture generation.',
        'questions': [
            {'id': 'tests', 'text': 'Do you want tests included?', 'type': 'boolean'},
            {'id': 'debugging', 'text': 'Debugging guidance needed?', 'type': 'boolean'},
            {'id': 'deployment', 'text': 'Deployment guidance needed?', 'type': 'boolean'},
            {'id': 'hosting', 'text': 'Target hosting type?', 'type': 'select', 'options': ['Shared Hosting', 'VPS (DigitalOcean/Linode)', 'Cloud (AWS/GCP/Azure)', 'Heroku/Railway']}
        ]
    }
}