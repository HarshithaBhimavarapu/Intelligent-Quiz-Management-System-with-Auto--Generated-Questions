from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# -----------------------
# Custom User Model
# -----------------------
class User(AbstractUser):
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


# -----------------------
# Profile Model
# -----------------------
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    age = models.IntegerField(default=0)
    quiz_score = models.IntegerField(default=0)
    avatar = models.ImageField(
        upload_to="avatars/",
        default="avatars/default.png",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.email


# -----------------------
# Category & Subcategory Models
# -----------------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.category.name} → {self.name}"


# -----------------------
# Quiz Models
# -----------------------
class Quiz(models.Model):
    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]

    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name="quizzes")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="easy")
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=1)  # 'A', 'B', 'C', or 'D'
    hint = models.TextField(blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text[:50]}..."


# -----------------------
# Quiz Attempt Model 
# -----------------------
class QuizAttempt(models.Model):
    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("in_progress", "In Progress"),
        ("abandoned", "Abandoned"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="in_progress")
    attempted_at = models.DateTimeField(auto_now_add=True)

    # Store all questions, options, answers, explanations in JSON
    answers = models.JSONField(default=dict, blank=True)
    """
    Example structure:
    {
        "586": {
            "text": "Question text...",
            "options": {"a": "...", "b": "...", "c": "...", "d": "..."},
            "correct_answer": "a",
            "user_answer": "b",
            "explanation": "..."
        },
        ...
    }
    """

    def __str__(self):
        return f"{self.user.email} - {self.subcategory.name if self.subcategory else 'No Subcategory'} - {self.score}"

    # --- NEW METHOD TO FIX THE ATTRIBUTE ERROR ---
    # In quiz_app/models.py, inside the QuizAttempt model

def get_questions_with_answers(self):
    questions = []
    
    if not isinstance(self.answers, dict):
        return questions

    for qid, data in self.answers.items():
        
        # Safety Check: Ensure 'data' for each question is a dictionary 
        if not isinstance(data, dict):
            data = {} 
        
        # --- CRITICAL FIX: Ensure every key is retrieved safely with a default ---
        question_text = data.get("text", "Question text not available")
        raw_options = data.get("options", {})
        
        # Convert options dictionary to a list of its values (the option text)
        options_list = list(raw_options.values())
        
        user_ans = data.get("user_answer", "N/A")
        correct_ans = data.get("correct_answer", "N/A")
        
        questions.append({
            "id": qid, 
            # 1. Use a default string if 'text' is missing
            "question": question_text, 
            # 2. Use the list of option texts
            "options": options_list,
            # 3. Retrieve user and correct answers with defaults
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            # 4. Check correctness
            "is_correct": user_ans == correct_ans and user_ans != "N/A",
            "explanation": data.get("explanation", "No explanation provided."),
        })
        
    return questions