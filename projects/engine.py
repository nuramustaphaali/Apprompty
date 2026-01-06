from .constants import FLOW_STAGES
from .questions import QUESTION_BANK

class FlowEngine:
    def __init__(self, project):
        self.project = project
        # Ensure the structure exists in memory
        if 'answers' not in self.project.requirements_data:
            self.project.requirements_data['answers'] = {}

    def get_current_state(self):
        """
        Determines exactly where the user is in the flow.
        """
        # 1. Force a fresh read of the answers
        answers = self.project.requirements_data.get('answers', {})
        
        completed_stages = 0
        current_stage = None
        
        # 2. Iterate strictly through the defined flow
        for stage in FLOW_STAGES:
            if stage in answers:
                completed_stages += 1
            else:
                current_stage = stage
                break
        
        is_completed = (completed_stages == len(FLOW_STAGES))
        progress_percent = int((completed_stages / len(FLOW_STAGES)) * 100)
        
        return {
            'current_stage': current_stage,
            'next_stage_index': completed_stages,
            'total_stages': len(FLOW_STAGES),
            'progress_percent': progress_percent,
            'is_completed': is_completed,
            'answers_so_far': answers
        }

    def submit_answer(self, stage, data):
        """
        Validates and saves an answer. 
        """
        state = self.get_current_state()
        
        # 1. Strict Validation
        if stage != state['current_stage'] and not state['is_completed']:
            # Allow editing old answers, but block skipping ahead
            if stage not in self.project.requirements_data.get('answers', {}):
                 raise ValueError(f"Sequence Violation: You must complete '{state['current_stage']}' before '{stage}'.")

        # 2. ROBUST SAVE MECHANISM (The Fix)
        # We assume the current data, modify it, and RE-ASSIGN it.
        # This forces Django to recognize the field as "dirty" (changed).
        current_data = self.project.requirements_data
        
        if 'answers' not in current_data:
            current_data['answers'] = {}
            
        current_data['answers'][stage] = data
        
        # Explicit assignment triggers the update flag
        self.project.requirements_data = current_data
        
        # Force save
        self.project.save()
        
        return self.get_current_state()

    def get_current_questions(self):
        state = self.get_current_state()
        if state['is_completed']:
            return None
        return QUESTION_BANK.get(state['current_stage'])
    
    def get_summary(self):
        # (Keep your existing get_summary code here)
        answers = self.project.requirements_data.get('answers', {})
        summary = []
        for stage_key in FLOW_STAGES:
            stage_def = QUESTION_BANK.get(stage_key)
            stage_summary = {'title': stage_def['title'], 'key': stage_key, 'items': []}
            stage_answers = answers.get(stage_key, {})
            for q in stage_def['questions']:
                val = stage_answers.get(q['id'], '—')
                if isinstance(val, list): val = ", ".join(val)
                if val is True: val = "Yes"
                if val is False: val = "No"
                stage_summary['items'].append({'label': q['text'], 'value': val})
            summary.append(stage_summary)
        return summary

    def lock_requirements(self):
        # (Keep your existing lock code here)
        state = self.get_current_state()
        if not state['is_completed']:
            raise ValueError("Cannot lock requirements: Questions are incomplete.")
        self.project.status = 'architecting'
        self.project.current_phase = 6
        self.project.save()
        return True