from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .models_pvp import PvpEmail, PvpLevel, PvpScenario  # noqa


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
    number = models.IntegerField()
    title = models.CharField(max_length=255, default="")
    briefing = models.TextField(default="", blank=True)
    scenario_overrides = models.JSONField(default=dict, blank=True)
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
    difficulty = models.IntegerField(default=1)
    category = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    links = models.JSONField(default=list, blank=True)
    attachments = models.JSONField(default=list, blank=True)

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
        choices=[
            ("arcade", "Arcade"),
            ("simulation", "Simulation"),
            ("pvp", "PVP"),
        ],
    )

    pvp_level = models.ForeignKey(
        "api.PvpLevel",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="emails_shadow",
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
    user_id = models.CharField(max_length=255)
    score = models.IntegerField(default=0)
    correct = models.IntegerField(default=0)
    incorrect = models.IntegerField(default=0)
    total_attempts = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Progress({self.user_id}): {self.score}pts"


class InteractionEvent(models.Model):
    user_id = models.CharField(max_length=255)
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=50)
    value = models.CharField(max_length=1024, blank=True, null=True)
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
        choices=[
            ("arcade", "Arcade"),
            ("simulation", "Simulation"),
            ("pvp", "PVP"),
        ]
    )

    # Optional but strongly recommended: tie to Level for clean aggregation
    level = models.ForeignKey(
        Level, null=True, blank=True, on_delete=models.SET_NULL, related_name="runs"
    )
    scenario = models.ForeignKey(
        Scenario, null=True, blank=True, on_delete=models.SET_NULL, related_name="runs"
    )
    pvp_level = models.ForeignKey(
        "api.PvpLevel",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="runs",
    )
    level_number = models.IntegerField(
        default=1
    )  # keep the global number for convenience

    emails_total = models.IntegerField(default=0)
    correct = models.IntegerField(default=0)
    incorrect = models.IntegerField(default=0)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # timing + score (used later; not necessarily shown to users)
    duration_ms = models.IntegerField(default=0)
    client_duration_ms = models.IntegerField(null=True, blank=True)
    points = models.IntegerField(default=0)

    def mark_complete(
        self,
        correct: int,
        incorrect: int,
        duration_ms: int | None = None,
        points: int | None = None,
        client_duration_ms: int | None = None,
    ):
        self.correct = int(correct)
        self.incorrect = int(incorrect)
        self.completed_at = timezone.now()
        self.emails_total = max(int(self.emails_total or 0), self.correct + self.incorrect)

        # Server duration: prefer explicit duration_ms if provided, else compute
        if duration_ms is not None:
            self.duration_ms = max(0, int(duration_ms))
        else:
            server_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)
            self.duration_ms = max(0, server_ms)

        # Client duration
        self.client_duration_ms = None if client_duration_ms is None else int(client_duration_ms)

        # Points: prefer explicit points if provided, else compute
        if points is not None:
            self.points = int(points)
        else:
            from .scoring import compute_levelrun_points
            self.points = int(compute_levelrun_points(self))

        self.save(
            update_fields=[
                "correct",
                "incorrect",
                "completed_at",
                "emails_total",
                "duration_ms",
                "client_duration_ms",
                "points",
            ]
        )

class EmailDecisionEvent(models.Model):
    DECISION_CHOICES = [
        ("report_phish", "Report Phish"),
        ("mark_read", "Mark as Read"),
        ("mark_safe", "Mark Safe"),
    ]

    user_id = models.CharField(max_length=255)
    run = models.ForeignKey(
        LevelRun,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="decisions",
    )
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name="decisions")

    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    was_correct = models.BooleanField(default=False)

    had_link_click = models.BooleanField(default=False)
    had_attachment_open = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Decision({self.user_id}, {self.decision}, correct={self.was_correct})"


class ArcadeState(models.Model):
    user_id = models.CharField(max_length=255, unique=True)
    difficulty_float = models.FloatField(default=2.0)
    streak = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    correct = models.IntegerField(default=0)
    last_email = models.ForeignKey(
        Email, null=True, blank=True, on_delete=models.SET_NULL
    )
    updated_at = models.DateTimeField(auto_now=True)

    def clamp(self, lo=1.0, hi=5.0):
        self.difficulty_float = max(lo, min(hi, self.difficulty_float))


class ArcadeAttempt(models.Model):
    user_id = models.CharField(max_length=255)
    email = models.ForeignKey(Email, on_delete=models.CASCADE)
    guess_is_phish = models.BooleanField()
    was_correct = models.BooleanField()
    response_time_ms = models.IntegerField(null=True, blank=True)

    target_difficulty = models.FloatField()
    email_difficulty = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user_id", "created_at"]),
            models.Index(fields=["user_id", "email"]),
        ]
