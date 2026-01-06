import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project
from .forms import ProjectForm
from .engine import FlowEngine
from .questions import QUESTION_BANK
from .ai_service import AIService
from django.views.decorators.http import require_POST

# --- HELPER FUNCTION ---
def get_next_action(project):
    """
    Determines the next button/action for the dashboard.
    ALWAYS returns a dictionary with 'url', 'label', and 'class'.
    """
    phase = project.current_phase
    
    # Defaults (Safety Net)
    action = {
        'label': 'Open Details',
        'url': 'project_detail',
        'class': 'bg-gray-600 hover:bg-gray-700'
    }

    # Phase 0-3: Setup -> Start Wizard
    if phase < 4:
        action = {
            'label': 'Start Planning', 
            'url': 'project_wizard', 
            'class': 'bg-blue-600 hover:bg-blue-700'
        }
    
    # Phase 4: Data Collection -> Continue Wizard
    elif phase == 4:
        action = {
            'label': 'Resume Questions', 
            'url': 'project_wizard', 
            'class': 'bg-blue-600 hover:bg-blue-700'
        }
    
    # Phase 5: Validation -> Review Summary
    elif phase == 5:
        action = {
            'label': 'Review & Lock', 
            'url': 'project_summary', 
            'class': 'bg-yellow-600 hover:bg-yellow-700'
        }
    
    # Phase 6: AI Generation -> Trigger AI
    elif phase == 6:
        action = {
            'label': 'Generate Blueprint', 
            'url': 'project_generate', 
            'class': 'bg-purple-600 hover:bg-purple-700'
        }
    
    # Phase 7+: Blueprint Ready -> View Result
    elif phase >= 7:
        action = {
            'label': 'View Blueprint', 
            'url': 'project_blueprint', 
            'class': 'bg-green-600 hover:bg-green-700'
        }
        
    return action

# --- VIEWS ---

@login_required
def dashboard(request):
    projects = Project.objects.filter(user=request.user)
    
    # IMPORTANT: Manually attach the action dict to each object
    for p in projects:
        p.action = get_next_action(p)
        
    return render(request, 'projects/dashboard.html', {'projects': projects})

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect('dashboard')
    else:
        form = ProjectForm()
    return render(request, 'projects/create.html', {'form': form})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    action = get_next_action(project)
    return render(request, 'projects/detail.html', {'project': project, 'action': action})

@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, "Project deleted.")
        return redirect('dashboard')
    return render(request, 'projects/delete.html', {'project': project})

@login_required
def duplicate_project_view(request, pk):
    original = get_object_or_404(Project, pk=pk, user=request.user)
    original.pk = None
    original.id = uuid.uuid4()
    original.name = f"Copy of {original.name}"
    original.status = 'draft'
    original.current_phase = 0
    original.save()
    messages.success(request, "Project duplicated.")
    return redirect('dashboard')

# --- WIZARD & AI VIEWS ---
@login_required
def project_wizard(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    engine = FlowEngine(project)
    state = engine.get_current_state()

    if state['is_completed']:
        return redirect('project_summary', pk=pk)

    current_stage = state['current_stage']
    stage_data = QUESTION_BANK.get(current_stage)

    if request.method == 'POST':
        answers = {}
        for q in stage_data['questions']:
            qid = q['id']
            # Handle different input types
            if q['type'] == 'checkbox':
                val = request.POST.getlist(qid)
            elif q['type'] == 'boolean':
                val = request.POST.get(qid) == 'on'
            else:
                val = request.POST.get(qid)
            
            answers[qid] = val
        
        # --- DEBUG PRINT ---
        # Look at your terminal when you click Next. It should show the data.
        print(f"DEBUG: Saving Stage: {current_stage}")
        print(f"DEBUG: Data Received: {answers}")
        # -------------------

        try:
            engine.submit_answer(current_stage, answers)
            messages.success(request, f"Saved {current_stage}!") # Visual feedback
            return redirect('project_wizard', pk=pk)
        except ValueError as e:
            messages.error(request, str(e))

    return render(request, 'projects/wizard.html', {
        'project': project,
        'stage': stage_data,
        'progress': state['progress_percent']
    })

@login_required
def project_summary(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    engine = FlowEngine(project)
    
    if request.method == 'POST':
        try:
            engine.lock_requirements()
            messages.success(request, "Locked. Ready for AI.")
            return redirect('project_generate', pk=pk) # Direct to AI page
        except ValueError as e:
            messages.error(request, str(e))
    
    return render(request, 'projects/summary.html', {'project': project, 'summary': engine.get_summary()})

# ... (Keep existing imports)
from .ai_service import AIService

@login_required
def project_generate(request, pk):
    """
    Phase 6: The AI Trigger
    """
    project = get_object_or_404(Project, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # 1. Initialize Service
        ai = AIService()
        
        # 2. Get User Answers
        requirements = project.requirements_data.get('answers', {})
        
        # 3. Call DeepSeek (Synchronous)
        blueprint = ai.generate_blueprint(requirements)
        
        if 'error' in blueprint:
            messages.error(request, f"AI Error: {blueprint['raw']}")
            return redirect('project_generate', pk=pk)

        # 4. Save Result
        project.blueprint_data = blueprint
        project.status = 'blueprint_ready'
        project.current_phase = 7
        project.save()
        
        messages.success(request, "Blueprint Architected Successfully!")
        return redirect('project_blueprint', pk=pk)
        
    return render(request, 'projects/generate.html', {'project': project})
    
@login_required
def project_blueprint(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    return render(request, 'projects/blueprint.html', {'project': project, 'bp': project.blueprint_data})

@login_required
def flow_debug(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    engine = FlowEngine(project)
    state = engine.get_current_state()
    return render(request, 'projects/flow_debug.html', {'project': project, 'state': state, 'stages': ['intent', 'platform', 'ui_ux', 'tech_stack', 'quality']})


# projects/views.py

@login_required
def project_implementation(request, pk):
    """
    Phase 7: The Task Board
    Parses the JSON blueprint and displays phases as a checklist.
    """
    project = get_object_or_404(Project, pk=pk, user=request.user)
    
    # Extract phases from the saved blueprint
    # Structure expected: { "phases": [ { "title": "...", "tasks": ["..."] } ] }
    blueprint = project.blueprint_data or {}
    phases = blueprint.get('phases', [])
    
    return render(request, 'projects/implementation.html', {
        'project': project,
        'phases': phases
    })

import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Project
from .ai_service import AIService

logger = logging.getLogger(__name__)

@login_required
@require_POST
def get_task_help(request, pk):
    """
    AJAX Endpoint: Returns AI code for a specific task.
    """
    try:
        project = get_object_or_404(Project, pk=pk, user=request.user)
        
        # 1. Parse Request Body
        try:
            data = json.loads(request.body)
            task_name = data.get('task')
        except json.JSONDecodeError:
            return JsonResponse({'content': 'Error: Invalid JSON body'}, status=400)

        # 2. Prepare Context (Handle missing keys gracefully)
        blueprint = project.blueprint_data or {}
        backend = blueprint.get('backend', {})
        
        # Force SQLite3 context if missing, since you explicitly requested it
        if not backend.get('database'):
            backend['database'] = "SQLite3"

        project_context = {
            'architecture': blueprint.get('architecture', {}),
            'frontend': blueprint.get('frontend', {}),
            'backend': backend,
        }

        # 3. Call AI
        ai = AIService()
        help_content = ai.generate_task_guide(
            project_context=project_context,
            current_task=task_name
        )

        return JsonResponse({'content': help_content})

    except Exception as e:
        # Log the full error to your terminal for debugging
        logger.error(f"Task Generation Error: {str(e)}")
        print(f"❌ SERVER ERROR: {str(e)}") # Print to terminal
        
        # Return a clean JSON error to the frontend
        return JsonResponse({
            'content': f"## System Error\n\nThe server encountered an error while contacting DeepSeek:\n\n`{str(e)}`\n\nPlease check your terminal for more details."
        }, status=500)

# ... imports ...
import markdown

@login_required
def project_docs(request, pk):
    """
    Phase 7: Strategic Documentation.
    Checks DB first. If empty, generates via AI and saves.
    """
    project = get_object_or_404(Project, pk=pk, user=request.user)
    
    # 1. Check if user requested a FORCE REGENERATE (via button)
    force_regen = request.POST.get('regenerate') == 'true'

    # 2. If docs exist and we aren't forcing, LOAD from DB
    if project.documentation_md and not force_regen:
        html_content = markdown.markdown(project.documentation_md, extensions=['fenced_code', 'tables'])
        return render(request, 'projects/docs.html', {
            'project': project,
            'html_content': html_content,
            'raw_markdown': project.documentation_md
        })

    # 3. Otherwise, GENERATE new docs
    if request.method == 'POST':
        ai = AIService()
        
        # Merge context
        blueprint = project.blueprint_data or {}
        full_context = {
            'blueprint': blueprint,
            'original_requirements': project.requirements_data.get('answers', {})
        }
        
        # Call AI
        md_content = ai.generate_project_docs(full_context)
        
        # SAVE to Database
        project.documentation_md = md_content
        project.save()
        
        # Render
        html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
        return render(request, 'projects/docs.html', {
            'project': project,
            'html_content': html_content,
            'raw_markdown': md_content
        })
        
    # 4. If GET and no docs exist, show "Ready to Generate" screen
    return render(request, 'projects/docs_start.html', {'project': project})


# ... imports ...
import markdown

@login_required
@require_POST
def get_doc_section(request, pk):
    """
    AJAX: Fetches or Generates a specific documentation section.
    """
    project = get_object_or_404(Project, pk=pk, user=request.user)
    
    try:
        data = json.loads(request.body)
        section_key = data.get('section') # e.g., 'intro', 'setup'
        force_regen = data.get('regenerate', False)
        
        # 1. Load existing docs
        current_docs = project.docs_data or {}
        
        # 2. If exists and not forcing regen, return saved data
        if section_key in current_docs and not force_regen:
            md_content = current_docs[section_key]
            return JsonResponse({
                'markdown': md_content, 
                'html': markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
            })

        # 3. Generate New Content
        ai = AIService()
        context = {
            'blueprint': project.blueprint_data,
            'requirements': project.requirements_data.get('answers', {})
        }
        
        new_md = ai.generate_doc_section(context, section_key)
        
        # 4. Save to DB (Update only this key)
        current_docs[section_key] = new_md
        project.docs_data = current_docs
        project.save()
        
        return JsonResponse({
            'markdown': new_md,
            'html': markdown.markdown(new_md, extensions=['fenced_code', 'tables'])
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def project_docs_shell(request, pk):
    """
    Renders the main Docs Container (The Tabs).
    """
    project = get_object_or_404(Project, pk=pk, user=request.user)
    return render(request, 'projects/docs_tabs.html', {'project': project})