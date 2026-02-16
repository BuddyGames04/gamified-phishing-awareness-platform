from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Scenario(models.Model):
    company_name = models.CharField(max_length=255, default="")
    sector = models.CharField(max_length=255, default="")
    role_title = models.CharField(max_length=255, default="")
    department_name = models.CharField(max_length=255, default="")
    line_manager_name = models.CharField(max_length=255, default="")
    responsibilities = models.JSONField(default=list, blank=True)
    intro_text = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name} - {self.role_title}"


class Level(models.Model):
    scenario = models.ForeignKey(
        Scenario, on_delete=models.CASCADE, related_name="levels"
    )
    number = models.IntegerField()  # IMPORTANT: this is the GLOBAL level number (1..10)
    title = models.CharField(max_length=255, default="")
    briefing = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("scenario", "number")
        ordering = ["scenario_id", "number"]

    def __str__(self):
        return f"Level {self.number}: {self.title} ({self.scenario.company_name})"


class Email(models.Model):
    sender_name = models.CharField(max_length=255, default="")
    sender_email = models.EmailField(max_length=255, default="")
    subject = models.CharField(max_length=255, default="")
    body = models.TextField()
    is_phish = models.BooleanField()
    difficulty = models.IntegerField(default=1)  # 1 = easy, 5 = hard
    category = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    links = models.JSONField(default=list, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    level_number = models.IntegerField(default=1)

    scenario = models.ForeignKey(
        Scenario,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="emails",
    )
    mode = models.CharField(
        max_length=20,
        default="arcade",
        choices=[("arcade", "Arcade"), ("simulation", "Simulation")],
    )

    def clean(self):
        super().clean()
        links = self.links or []
        attachments = self.attachments or []

        has_links = len(links) > 0
        has_attachments = len(attachments) > 0

        if has_links and has_attachments:
            raise ValidationError(
                "Email must have either links or attachments, not both."
            )
        if not has_links and not has_attachments:
            raise ValidationError(
                "Email must have at least one link or one attachment."
            )

    def __str__(self):
        return f"{self.subject} ({'Phish' if self.is_phish else 'Legit'})"


class UserProgress(models.Model):
    user_id = models.CharField(max_length=255)  # placeholder for now (no auth)
    score = models.IntegerField(default=0)
    correct = models.IntegerField(default=0)
    incorrect = models.IntegerField(default=0)
    total_attempts = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Progress({self.user_id}): {self.score}pts"


class InteractionEvent(models.Model):
    user_id = models.CharField(max_length=255)  # placeholder for now (no auth)
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(
        max_length=50
    )  # link_click, attachment_open, open_anyway, etc
    value = models.CharField(max_length=1024, blank=True, null=True)  # url or filename
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interaction({self.user_id}, {self.event_type})"


class LevelEmail(models.Model):
    level = models.ForeignKey(
        Level, on_delete=models.CASCADE, related_name="level_emails"
    )
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name="in_levels")
    sort_order = models.IntegerField(default=0)

    class Meta:
        unique_together = ("level", "email")
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.level} -> {self.email.subject}"

class LevelRun(models.Model):
    user_id = models.CharField(max_length=255)
    mode = models.CharField(
        max_length=20,
        default="simulation",
        choices=[("arcade", "Arcade"), ("simulation", "Simulation")],
    )

    # Optional but strongly recommended: tie to Level for clean aggregation
    level = models.ForeignKey(Level, null=True, blank=True, on_delete=models.SET_NULL, related_name="runs")
    scenario = models.ForeignKey(Scenario, null=True, blank=True, on_delete=models.SET_NULL, related_name="runs")
    level_number = models.IntegerField(default=1)  # keep the global number for convenience

    emails_total = models.IntegerField(default=0)
    correct = models.IntegerField(default=0)
    incorrect = models.IntegerField(default=0)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def mark_complete(self, correct: int, incorrect: int):
        self.correct = int(correct)
        self.incorrect = int(incorrect)
        self.completed_at = timezone.now()
        self.save(update_fields=["correct", "incorrect", "completed_at"])

    def __str__(self):
        return f"LevelRun({self.user_id}, L{self.level_number}, {self.mode})"


class EmailDecisionEvent(models.Model):
    DECISION_CHOICES = [
        ("report_phish", "Report Phish"),
        ("mark_read", "Mark as Read"),
        ("mark_safe", "Mark Safe"),
    ]

    user_id = models.CharField(max_length=255)
    run = models.ForeignKey(LevelRun, null=True, blank=True, on_delete=models.SET_NULL, related_name="decisions")
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name="decisions")

    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    was_correct = models.BooleanField(default=False)

    # behaviour flags computed server-side from InteractionEvent
    had_link_click = models.BooleanField(default=False)
    had_attachment_open = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Decision({self.user_id}, {self.decision}, correct={self.was_correct})"