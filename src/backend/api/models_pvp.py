from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

VISIBILITY_CHOICES = [
    ("unlisted", "Unlisted"),
    ("posted", "Posted"),
]


class PvpScenario(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pvp_scenarios"
    )
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, default="")
    sector = models.CharField(max_length=255, default="")
    role_title = models.CharField(max_length=255, default="")
    department_name = models.CharField(max_length=255, default="")
    line_manager_name = models.CharField(max_length=255, default="")
    responsibilities = models.JSONField(default=list, blank=True)
    intro_text = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class PvpLevel(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pvp_levels"
    )
    scenario = models.ForeignKey(
        PvpScenario, on_delete=models.CASCADE, related_name="levels"
    )

    title = models.CharField(max_length=255, default="")
    briefing = models.TextField(default="", blank=True)

    visibility = models.CharField(
        max_length=20, choices=VISIBILITY_CHOICES, default="unlisted"
    )

    plays = models.IntegerField(default=0)
    avg_accuracy = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class PvpEmail(models.Model):
    level = models.ForeignKey(PvpLevel, on_delete=models.CASCADE, related_name="emails")

    sender_name = models.CharField(max_length=255, default="")
    sender_email = models.EmailField(max_length=255, default="")
    subject = models.CharField(max_length=255, default="")
    body = models.TextField()

    is_phish = models.BooleanField(default=False)
    difficulty = models.IntegerField(default=1)                              
    category = models.CharField(max_length=100, blank=True, null=True)

    links = models.JSONField(default=list, blank=True)
    attachments = models.JSONField(default=list, blank=True)

    is_wave = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    shadow_email = models.OneToOneField(
        "api.Email",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pvp_source",
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

    def sync_shadow_email(self):
        from .models import Email

        if self.shadow_email_id:
            shadow = self.shadow_email
            shadow.sender_name = self.sender_name
            shadow.sender_email = self.sender_email
            shadow.subject = self.subject
            shadow.body = self.body
            shadow.is_phish = self.is_phish
            shadow.difficulty = self.difficulty
            shadow.category = self.category
            shadow.links = self.links or []
            shadow.attachments = self.attachments or []
            shadow.mode = "pvp"
            shadow.pvp_level = self.level
            shadow.save()
            return shadow

        shadow = Email.objects.create(
            sender_name=self.sender_name,
            sender_email=self.sender_email,
            subject=self.subject,
            body=self.body,
            is_phish=self.is_phish,
            difficulty=self.difficulty,
            category=self.category,
            links=self.links or [],
            attachments=self.attachments or [],
            mode="pvp",
            pvp_level=self.level,
        )
        self.shadow_email = shadow
        self.save(update_fields=["shadow_email"])
        return shadow

    class Meta:
        ordering = ["is_wave", "sort_order", "id"]
