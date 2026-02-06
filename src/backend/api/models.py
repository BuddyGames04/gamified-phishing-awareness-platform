from django.db import models


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
