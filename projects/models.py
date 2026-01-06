import uuid
from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    # --- ENUMS ---
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    # The 10-Phase logic
    PHASE_CHOICES = [
        (0, 'Environment Setup'),
        (1, 'User System'),
        (2, 'Project Management'),
        (3, 'System Logic'),
        (4, 'User Questions'),
        (5, 'Requirement Lock'),
        (6, 'Blueprint Generation'),
        (7, 'Execution Guide'),
        (8, 'Testing'),
        (9, 'Deployment'),
        (10, 'Final Export'),
    ]

    # --- FIELDS ---
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    current_phase = models.IntegerField(choices=PHASE_CHOICES, default=0)
    
    # Future-proofing for AI Data (Stored as JSON in SQLite)
    requirements_data = models.JSONField(default=dict, blank=True)
    blueprint_data = models.JSONField(default=dict, blank=True)
    documentation_md = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.name