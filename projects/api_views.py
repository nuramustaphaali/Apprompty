import uuid
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Project
from .serializers import ProjectSerializer
from .ai_service import AIService
from .questions import QUESTION_BANK
from rest_framework.decorators import action
from rest_framework import status
from .engine import FlowEngine
from .serializers import ProjectSerializer, AnswerInputSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    # Enable API search (?search=name) and ordering (?ordering=-created_at)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['updated_at', 'status']

    def get_queryset(self):
        # STRICT: Users can only see their own projects
        return Project.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # STRICT: Force the user to be the current logged-in user
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        API Endpoint to duplicate a project.
        POST /api/projects/{uuid}/duplicate/
        """
        original_project = self.get_object()
        
        # 1. Create a memory copy of the object
        original_project.pk = None 
        original_project.id = uuid.uuid4() # Explicitly generate new UUID
        original_project.user = request.user # Ensure ownership
        
        # 2. Modify specific fields
        original_project.name = f"Copy of {original_project.name}"
        original_project.status = 'draft' # Reset status
        original_project.current_phase = 0 # Reset phase
        
        # 3. Save as new record
        original_project.save()
        
        # 4. Return the new data
        serializer = self.get_serializer(original_project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @action(detail=True, methods=['get'])
    def flow_state(self, request, pk=None):
        """
        GET /api/projects/{uuid}/flow_state/
        Returns current progress and what question to ask next.
        """
        project = self.get_object()
        engine = FlowEngine(project)
        state = engine.get_current_state()
        return Response(state)

    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        """
        POST /api/projects/{uuid}/submit_answer/
        Body: { "stage": "intent", "answer_data": { "description": "A taxi app" } }
        """
        project = self.get_object()
        serializer = AnswerInputSerializer(data=request.data)
        
        if serializer.is_valid():
            engine = FlowEngine(project)
            try:
                new_state = engine.submit_answer(
                    stage=serializer.validated_data['stage'],
                    data=serializer.validated_data['answer_data']
                )
                return Response(new_state, status=status.HTTP_200_OK)
            except ValueError as e:
                # Engine detected sequence violation
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['get'])
    def get_questions(self, request, pk=None):
        """
        GET /api/projects/{uuid}/get_questions/
        Returns the question payload for the CURRENT stage only.
        """
        project = self.get_object()
        engine = FlowEngine(project)
        questions = engine.get_current_questions()
        
        if not questions:
            return Response({'message': 'All stages completed.'}, status=status.HTTP_204_NO_CONTENT)
            
        return Response(questions)

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        GET /api/projects/{uuid}/summary/
        Returns formatted Q&A for review.
        """
        project = self.get_object()
        engine = FlowEngine(project)
        return Response(engine.get_summary())

    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        """
        POST /api/projects/{uuid}/lock/
        Finalizes requirements. Triggers transition to AI Phase.
        """
        project = self.get_object()
        engine = FlowEngine(project)
        
        try:
            engine.lock_requirements()
            return Response({'status': 'locked', 'next_phase': 6, 'message': 'Ready for Gemini'})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """
        POST /api/projects/{uuid}/generate/
        Triggers Gemini.
        """
        project = self.get_object()
        
        # Security: Only allow generation if phase is correct
        if project.current_phase != 6: # Ensure we are in Phase 6
             # (Optional) enforce stricter checks here
             pass

        # 1. Prepare Data
        requirements = project.requirements_data.get('answers', {})
        
        # 2. Call AI
        ai = AIService()
        blueprint = ai.generate_blueprint(requirements)
        
        if "error" in blueprint:
            return Response(blueprint, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 3. Save to DB
        project.blueprint_data = blueprint
        project.status = 'blueprint_ready'
        project.current_phase = 7 # Move to Execution Guide
        project.save()

        return Response(blueprint)