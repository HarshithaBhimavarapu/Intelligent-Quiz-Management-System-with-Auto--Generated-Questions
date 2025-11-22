


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

# Register Page
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect("login")

    return render(request, "quiz_app/register.html")


# Login Page
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate using username (Django default)
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return redirect("login")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")  # Redirect to your homepage/dashboard
        else:
            messages.error(request, "Invalid credentials")
            return redirect("login")

    return render(request, "quiz_app/login.html")


# Logout
def logout_view(request):
    logout(request)
    return redirect("login")


# Example Home Page (after login)
def home_view(request):
    return render(request, "quiz_app/home.html")


from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

# Register view
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "quiz_app/register.html", {"form": form})

# Login view
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "quiz_app/login.html", {"form": form})

# Logout view
def logout_view(request):
    logout(request)
    return redirect("login")

# Home page (only if logged in)
@login_required
def home_view(request):
    return render(request, "quiz_app/home.html")


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def start_quiz(request):
    return render(request, "quiz_app/start_quiz.html")


def logout_view(request):
    logout(request)  # this removes the session
    return render(request, "quiz_app/logout.html")



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from .models import Profile


# -----------------------
# Home Page (show quiz attempts)
# -----------------------
@login_required
def home(request):
    # If Profile has relation to attempts, fetch them
    attempts = getattr(request.user, "quizattempt_set", None)
    return render(request, "home.html", {"attempts": attempts})


# -----------------------
# Profile View (View & Update)
# -----------------------

@login_required
def profile_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        # Update username & email
        user.username = request.POST.get("username", user.username)
        user.email = request.POST.get("email", user.email)
        user.save()

        # Update profile age
        age = request.POST.get("age")
        if age:
            profile.age = age

        # Update avatar image
        if "profile_image" in request.FILES:
            # Delete old avatar if not default
            if profile.avatar and profile.avatar.url != '/media/avatars/default.png':
                profile.avatar.delete(save=False)
            profile.avatar = request.FILES["profile_image"]

        profile.save()
        return redirect("profile")

    return render(request, "quiz_app/profile.html", {"user": user, "profile": profile})

# -----------------------
# Logout
# -----------------------
def logout_view(request):
    auth_logout(request)
    return redirect("register")  # or redirect to login


# -----------------------
# Quiz Categories
# -----------------------
@login_required
def quiz_categories(request):
    categories = [
        "Entertainment", "Maths", "Physics",
        "Chemistry", "Sports", "General Knowledge"
    ]
    return render(request, "quiz_app/categories.html", {"categories": categories})

        
from django.shortcuts import render, get_object_or_404
from .models import Category, Subcategory

def categories(request):
    categories = Category.objects.all()
    return render(request, "quiz_app/categories.html", {"categories": categories})

def subcategories(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    subcategories = Subcategory.objects.filter(category=category)
    return render(request, "quiz_app/subcategories.html", {
        "category": category,
        "subcategories": subcategories
    })



from django.shortcuts import render
from .models import Category

def quiz_categories(request):
    categories = Category.objects.all()
    return render(request, "quiz_app/categories.html", {"categories": categories})

from django.shortcuts import render, get_object_or_404
from .models import Subcategory, Quiz

def quiz_list(request, subcategory_id):
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)
    quizzes = Quiz.objects.filter(subcategory=subcategory)
    return render(request, "quiz_app/quiz_list.html", {
        "subcategory": subcategory,
        "quizzes": quizzes
    })

def home(request):
    attempts = QuizAttempt.objects.filter(user=request.user).count()
    score = QuizAttempt.objects.filter(user=request.user).aggregate(total=Sum('score'))['total'] or 0

    return render(request, "quiz_app/home.html", {
        "attempts": attempts,
        "score": score,
    })

from django.db.models import Sum
from .models import QuizAttempt

def home(request):
    attempts = QuizAttempt.objects.filter(user=request.user).count()
    score = QuizAttempt.objects.filter(user=request.user).aggregate(total=Sum('score'))['total'] or 0

    #  Get latest quiz attempt
    latest_attempt = QuizAttempt.objects.filter(user=request.user).order_by('-attempted_at').first()

    return render(request, "quiz_app/home.html", {
        "attempts": attempts,
        "score": score,
        "latest_attempt": latest_attempt,
    })




from django.shortcuts import render, get_object_or_404
from .models import Category, Subcategory, Quiz

def quiz_list(request, subcategory_id):
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)
    category = subcategory.category

    # Fetch questions for this subcategory
    questions = Quiz.objects.filter(subcategory=subcategory)

    context = {
        "subcategory": subcategory,
        "category": category,
        "questions": questions,
        "options": ["A", "B", "C", "D"],   #  options passed here
        "question_count": questions.count(),
        "error_message": None if questions else "No questions found for this subcategory."
    }

    return render(request, "quiz_app/quiz_list.html", context)

from django.shortcuts import render
from django.db.models import Sum
from quiz_app.models import QuizAttempt

def home_view(request):
    user = request.user
    attempts = QuizAttempt.objects.filter(user=user).count()
    score = QuizAttempt.objects.filter(user=user).aggregate(total_score=Sum('score'))['total_score'] or 0
    latest_attempt = QuizAttempt.objects.filter(user=user).order_by('-attempted_at').first()

    return render(request, "quiz_app/home.html", {
        "attempts": attempts,
        "score": score,
        "latest_attempt": latest_attempt,
    })








from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from openai import OpenAI
from .models import Quiz, Category, Subcategory, QuizAttempt
import json
import re

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_quiz(request, category_id, subcategory_id, difficulty, question_count=5):
    """
    Generate or resume a quiz for a given subcategory, difficulty, and question count.
    Ensures generated questions are accurate, validated, and correctly mapped to answers.
    """
    category = get_object_or_404(Category, id=category_id)
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)
    question_count = int(question_count)

    # Check if user has a paused quiz attempt
    paused_attempt = QuizAttempt.objects.filter(
        user=request.user,
        subcategory=subcategory,
        status="in_progress"
    ).last()

    if paused_attempt:
        # Resume paused quiz
        questions = Quiz.objects.filter(id__in=paused_attempt.answers.keys())
        prefilled_answers = paused_attempt.answers
        question_count = len(questions)

    else:
        # Fetch or generate new questions
        questions = Quiz.objects.filter(subcategory=subcategory, difficulty=difficulty, is_used=False)[:question_count]

        if questions.count() < question_count:
            existing_questions = Quiz.objects.filter(subcategory=subcategory, difficulty=difficulty)
            existing_texts = [q.text for q in existing_questions]

            # --- Improved AI prompt for reliable and consistent generation ---
            prompt = f"""
            You are a strict and accurate quiz generator.
            Generate {question_count - questions.count()} unique, factually correct
            multiple-choice questions for the subcategory: "{subcategory.name}" at {difficulty} difficulty.

            Rules:
            1. Each question must have exactly 4 options labeled a, b, c, d.
            2. Exactly one option must be correct.
            3. The "answer" field MUST match one of the keys in "options" ("a", "b", "c", or "d").
            4. All math and logic must be verified correct before answering.
            5. Each explanation must clearly justify the correct answer.
            6. Avoid repeating these questions: {json.dumps(existing_texts, ensure_ascii=False)}.

            Output ONLY valid JSON, in this format:
            [
              {{
                "question": "string",
                "options": {{"a": "option1", "b": "option2", "c": "option3", "d": "option4"}},
                "answer": "a/b/c/d",
                "explanation": "short factual explanation"
              }}
            ]
            """

            try:
                # --- Call OpenAI for question generation ---
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert quiz generator that always produces valid JSON and checks correctness carefully."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                )

                # --- Clean and extract JSON safely ---
                content = response.choices[0].message.content.strip()
                json_start = content.find("[")
                json_end = content.rfind("]") + 1
                json_str = content[json_start:json_end]
                new_data = json.loads(json_str)

                # --- Optional: validate math consistency ---
                def validate_math(q_text, correct_opt, all_opts):
                    """
                    Basic validation for arithmetic-type questions to prevent mismatches.
                    """
                    numbers = re.findall(r"\d+", q_text)
                    if len(numbers) >= 2 and any(op in q_text for op in ["+", "-", "×", "x", "*", "/", "÷"]):
                        try:
                            expr = (
                                q_text.replace("×", "*")
                                .replace("x", "*")
                                .replace("÷", "/")
                                .replace("?", "")
                            )
                            match = re.findall(r"\d+\s*[\+\-\*\/]\s*\d+", expr)
                            if match:
                                result = eval(match[0])
                                correct_value = all_opts.get(correct_opt)
                                if str(result) not in str(correct_value):
                                    return False
                        except Exception:
                            return True
                    return True

                # --- Save generated questions  ---
                for q in new_data:
                    options = q["options"]
                    answer = q["answer"].strip().lower()
                    explanation = q.get("explanation", "").strip()

                    
                    if answer not in options:
                        continue  # skip invalid answer keys

                    #  Validate math and then save
                    if validate_math(q["question"], answer, options):
                        Quiz.objects.create(
                            subcategory=subcategory,
                            difficulty=difficulty,
                            text=q["question"].strip(),
                            option_a=options["a"].strip(),
                            option_b=options["b"].strip(),
                            option_c=options["c"].strip(),
                            option_d=options["d"].strip(),
                            correct_answer=answer,
                            explanation=explanation,
                            is_used=False,
                        )

                # Refresh the list of available questions
                questions = Quiz.objects.filter(subcategory=subcategory, difficulty=difficulty, is_used=False)[:question_count]

            except Exception as e:
                return render(request, "quiz_app/quiz_list.html", {
                    "category": category,
                    "subcategory": subcategory,
                    "questions": [],
                    "error_message": f"Error generating quiz: {e}"
                })

        # Mark selected questions as used
        for q in questions:
            q.is_used = True
            q.save()

        prefilled_answers = {}

    # --- Render quiz page ---
    return render(request, "quiz_app/quiz_list.html", {
        "category": category,
        "subcategory": subcategory,
        "questions": questions,
        "question_count": question_count,
        "prefilled_answers": prefilled_answers,
    })





from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from openai import OpenAI
from .models import Quiz  #  use Quiz, not Question

# Initialize OpenAI client
client = OpenAI()

def get_hint(request, question_id):
    """
    Generate an AI-powered hint for a specific quiz question.
    """
    question = get_object_or_404(Quiz, id=question_id)

    prompt = f"""
    Provide a short, helpful hint for this multiple-choice question without revealing the answer.
    Question: "{question.text}"
    Options:
    A. {question.option_a}
    B. {question.option_b}
    C. {question.option_c}
    D. {question.option_d}

    The hint should guide the student toward reasoning the correct answer, not reveal it.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful quiz assistant who gives subtle hints without revealing answers."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=80,
        )

        hint_text = response.choices[0].message.content.strip()
        return JsonResponse({"hint": hint_text})
    except Exception as e:
        return JsonResponse({"hint": f"Error generating hint: {str(e)}"})





from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
from .models import QuizAttempt, Profile
from django.contrib.auth import get_user_model
import pytz

User = get_user_model()

# Use IST timezone
IST = pytz.timezone("Asia/Kolkata")

@login_required
def dashboard_view(request):
    """Render the dashboard HTML page with history (in local IST time)"""
    user = request.user
    attempts_qs = QuizAttempt.objects.filter(user=user).order_by('-attempted_at')

    # Convert times to IST for display
    for attempt in attempts_qs:
        if attempt.attempted_at:
            attempt.local_attempted_at = timezone.localtime(attempt.attempted_at, IST)

    return render(request, "quiz_app/dashboard.html", {
        "history": attempts_qs
    })


@login_required
def dashboard_data(request):
    user = request.user
    attempts_qs = QuizAttempt.objects.filter(user=user)

    # Stats summary
    stats = {
        "completed": attempts_qs.filter(status='completed').count(),
        "in_progress": attempts_qs.filter(status='in_progress').count(),
        "abandoned": attempts_qs.filter(status='abandoned').count(),
        "average_score": round(attempts_qs.aggregate(avg=Avg('score'))['avg'] or 0, 2),
    }

    # Convert timestamps to IST for history
    IST = pytz.timezone("Asia/Kolkata")
    history = []
    for a in attempts_qs.order_by('-attempted_at'):
        local_time = timezone.localtime(a.attempted_at, IST)
        history.append({
            'subcategory__name': a.subcategory.name,
            'score': a.score,
            'status': a.status,
            'attempted_at': local_time.strftime("%d %b %Y %H:%M"),
        })

    # Daily streak for logged-in user
    today = timezone.localtime(timezone.now(), IST).date()
    unique_days = sorted({
        timezone.localtime(a.attempted_at, IST).date()
        for a in attempts_qs.filter(status='completed')
    })

    streak = 0
    temp_day = today
    for d in reversed(unique_days):
        delta = (temp_day - d).days
        if delta == 0 or delta == 1:
            streak += 1
            temp_day -= timedelta(days=1)
        else:
            break
    stats["daily_streak"] = streak

    # Quiz leaderboard (top 5 users by avg score)
    leaderboard = []
    top_users = (
        QuizAttempt.objects.values('user')
        .annotate(avg_score=Avg('score'))
        .order_by('-avg_score')[:5]
    )
    for idx, u in enumerate(top_users):
        try:
            user_obj = User.objects.get(id=u['user'])
            profile = getattr(user_obj, 'profile', None)
            avatar_url = profile.avatar.url if profile and profile.avatar else '/static/avatars/default.png'
            medal = ""
            if idx == 0: medal = "🥇"
            elif idx == 1: medal = "🥈"
            elif idx == 2: medal = "🥉"
            leaderboard.append({
                "user__username": user_obj.username,
                "avg_score": round(u['avg_score'] or 0, 2),
                "avatar_url": avatar_url,
                "medal": medal,
            })
        except User.DoesNotExist:
            continue

    # 🏆 Streak leaderboard (top 5 users by streak)
    streak_leaderboard = []
    all_users = User.objects.all()
    for u in all_users:
        attempts = QuizAttempt.objects.filter(user=u, status='completed')
        unique_days = sorted({timezone.localtime(a.attempted_at, IST).date() for a in attempts})
        user_streak = 0
        temp_day_user = today
        for d in reversed(unique_days):
            delta = (temp_day_user - d).days
            if delta == 0 or delta == 1:
                user_streak += 1
                temp_day_user -= timedelta(days=1)
            else:
                break
        if user_streak > 0:
            profile = getattr(u, 'profile', None)
            streak_leaderboard.append({
                "username": u.username,
                "streak": user_streak,
                "avatar_url": profile.avatar.url if profile and profile.avatar else '/static/avatars/default.png'
            })

    # Sort and keep top 5
    streak_leaderboard = sorted(streak_leaderboard, key=lambda x: x["streak"], reverse=True)[:5]

    data = {
        "stats": stats,
        "history": history,
        "leaderboard": leaderboard,
        "streak_leaderboard": streak_leaderboard,
    }

    return JsonResponse(data)




from django.shortcuts import render

def home(request):
    return render(request, 'quiz_app/home.html')

def about_us(request):
    return render(request, 'quiz_app/about_us.html')



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import QuizAttempt

@login_required
def view_attempt_view(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)

    if attempt.status != "completed":
        return render(request, "quiz_app/error.html", {"message": "This attempt is not completed yet."})

    questions = attempt.get_questions_with_answers()

    return render(request, "quiz_app/view_attempt.html", {
        "attempt": attempt,
        "questions": questions
    })


@login_required
def resume_quiz_view(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    questions = attempt.get_questions_with_answers()  # now it will work
    return render(request, "quiz_app/resume_quiz.html", {
        "attempt": attempt,
        "questions": questions
    })




from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import QuizAttempt

@login_required
def view_attempt_view(request, attempt_id):
    """
    Display completed quiz attempt with options A–D correctly mapped,
    handling both list or dict formats in stored answers.
    """

    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    results = []
    total_questions = 0
    correct_count = 0

    if isinstance(attempt.answers, dict):
        for qid, data in attempt.answers.items():
            if not isinstance(data, dict):
                continue

            total_questions += 1

            question_text = data.get("text", "Question text not available")
            options_raw = data.get("options", {})

            # Map options safely
            if isinstance(options_raw, dict):
                option_map = {
                    "a": options_raw.get("A") or options_raw.get("a") or "",
                    "b": options_raw.get("B") or options_raw.get("b") or "",
                    "c": options_raw.get("C") or options_raw.get("c") or "",
                    "d": options_raw.get("D") or options_raw.get("d") or "",
                }
            elif isinstance(options_raw, list):
                option_map = {
                    "a": options_raw[0] if len(options_raw) > 0 else "",
                    "b": options_raw[1] if len(options_raw) > 1 else "",
                    "c": options_raw[2] if len(options_raw) > 2 else "",
                    "d": options_raw[3] if len(options_raw) > 3 else "",
                }
            else:
                option_map = {"a": "", "b": "", "c": "", "d": ""}

            user_answer_key = (data.get("user_answer") or "").lower()
            correct_answer_key = (data.get("correct_answer") or "").lower()

            user_answer_text = option_map.get(user_answer_key, "Not Answered")
            correct_answer_text = option_map.get(correct_answer_key, "N/A")

            correct = user_answer_key == correct_answer_key
            if correct:
                correct_count += 1

            results.append({
                "question": question_text,
                "options": option_map,
                "your_answer_text": user_answer_text,
                "correct_answer_text": correct_answer_text,
                "correct_answer_key": correct_answer_key,
                "correct": correct,
                "explanation": data.get("explanation", ""),
            })

    score = round((correct_count / total_questions) * 100) if total_questions else 0

    context = {
        "subcategory": getattr(attempt.subcategory, "name", "Unknown"),
        "results": results,
        "score": f"{score}%",
        "attempt": attempt,
    }

    return render(request, "quiz_app/view_attempt.html", context)




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Quiz, QuizAttempt, Subcategory

@login_required
def submit_quiz(request, subcategory_id):
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)
    
    if request.method != "POST":
        return redirect('generate_quiz', category_id=subcategory.category.id, subcategory_id=subcategory.id, difficulty='easy')

    question_count = int(request.POST.get("question_count", 0))
    action = request.POST.get("action", "submit")  # submit, pause_quit, abandon

    attempt_answers = {}
    correct_count = 0
    results = []  # For quiz_results.html

    for i in range(1, question_count + 1):
        qid = request.POST.get(f"question_id_{i}")
        user_answer_key = request.POST.get(f"question_{i}", "").lower()
        
        try:
            question = Quiz.objects.get(id=qid)
        except Quiz.DoesNotExist:
            continue

        correct = user_answer_key == question.correct_answer.lower()
        if correct:
            correct_count += 1

        # Build structured attempt data
        attempt_answers[str(qid)] = {
            "text": question.text,
            "options": {
                "A": question.option_a,
                "B": question.option_b,
                "C": question.option_c,
                "D": question.option_d,
            },
            "correct_answer": question.correct_answer,
            "user_answer": user_answer_key,
            "explanation": question.explanation,
            "is_correct": correct,
        }

        #  Get the actual text for correct and user answers
        correct_answer_text = getattr(question, f"option_{question.correct_answer.lower()}", "")
        your_answer_text = getattr(question, f"option_{user_answer_key}", "")

        #  Add both key and text so results page can show "B - Apple"
        results.append({
            "question": question.text,
            "options": {
                "a": question.option_a,
                "b": question.option_b,
                "c": question.option_c,
                "d": question.option_d,
            },
            "correct_answer_key": question.correct_answer,
            "correct_answer_text": correct_answer_text,  #  Added
            "your_answer_key": user_answer_key,
            "your_answer_text": your_answer_text,
            "correct": correct,
            "explanation": question.explanation,
        })

    numeric_score = int((correct_count / question_count) * 100) if question_count else 0

    # Determine status and score
    if action == "submit":
        status = "completed"
        score = numeric_score
    elif action == "pause_quit":
        status = "in_progress"
        score = None
    elif action == "abandon":
        status = "abandoned"
        score = None
    else:
        status = "in_progress"
        score = None

    # Save full attempt
    QuizAttempt.objects.create(
        user=request.user,
        subcategory=subcategory,
        status=status,
        score=score,
        answers=attempt_answers,
    )

    if action in ["pause_quit", "abandon"]:
        return redirect('home')

    return render(request, "quiz_app/quiz_results.html", {
        "subcategory": subcategory,
        "results": results,
        "score": f"{correct_count}/{question_count}",
    })



from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import QuizAttempt


@login_required
def resume_quiz_view(request, attempt_id):
    """
    Allows a user to resume a quiz that was previously paused or abandoned.
    Pre-fills previously selected answers in the form.
    """

    # 1️⃣ Fetch the attempt for the logged-in user
    attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id,
        user=request.user,
        status__in=["in_progress", "abandoned"]
    )

    # 2️⃣ Build the question list to send to the template
    questions = []

    if isinstance(attempt.answers, dict):
        for qid, data in attempt.answers.items():
            if not isinstance(data, dict):
                continue

            # Extract safe values
            question_text = data.get("text", "Question text not available")
            options_dict = data.get("options", {})

            #  Ensure options are properly labeled A–D (dictionary format)
            options = {
                "A": options_dict.get("A", ""),
                "B": options_dict.get("B", ""),
                "C": options_dict.get("C", ""),
                "D": options_dict.get("D", ""),
            }

            questions.append({
                "id": qid,
                "question": question_text,
                "options": options,
                "user_answer": data.get("user_answer", ""),  # Pre-selected radio
                "correct_answer": data.get("correct_answer", ""),
                "explanation": data.get("explanation", ""),
            })

    #  Context for rendering
    context = {
        "attempt": attempt,
        "questions": questions,
    }

    #  Render the resume quiz page
    return render(request, "quiz_app/resume_quiz.html", context)


# In quiz_app/views.py

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import QuizAttempt, Quiz

@login_required
def submit_resumed_quiz(request, attempt_id):
    #  Fetch the existing attempt
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)

    if request.method != "POST":
        return redirect('dashboard')

    question_count = int(request.POST.get("question_count", 0))
    action = request.POST.get("action", "submit")

    attempt_answers = {}
    correct_count = 0

    for i in range(1, question_count + 1):
        qid = request.POST.get(f"question_id_{i}")
        user_answer_key = (request.POST.get(f"question_{i}", "") or "").strip().upper()

       
        if "A" in user_answer_key:
            user_answer_key = "A"
        elif "B" in user_answer_key:
            user_answer_key = "B"
        elif "C" in user_answer_key:
            user_answer_key = "C"
        elif "D" in user_answer_key:
            user_answer_key = "D"
        else:
            user_answer_key = "N/A"

        try:
            question = Quiz.objects.get(id=qid)
        except Quiz.DoesNotExist:
            continue

        correct_answer = (question.correct_answer or "").strip().upper()

        correct = user_answer_key == correct_answer
        if correct:
            correct_count += 1

        #  Store full answer structure for viewing later
        attempt_answers[str(qid)] = {
            "text": question.text,
            "options": {
                "A": question.option_a,
                "B": question.option_b,
                "C": question.option_c,
                "D": question.option_d,
            },
            "correct_answer": correct_answer,
            "user_answer": user_answer_key,
            "explanation": question.explanation,
            "is_correct": correct,
        }

    #  Compute score only on submission
    numeric_score = int((correct_count / question_count) * 100) if question_count and action == "submit" else None

    # Update attempt status and score
    if action == "submit":
        attempt.status = "completed"
        attempt.score = numeric_score
    elif action == "pause_quit":
        attempt.status = "in_progress"
        attempt.score = None
    elif action == "abandon":
        attempt.status = "abandoned"
        attempt.score = None

    attempt.answers = attempt_answers
    attempt.save()

    #  Redirect
    if action == "submit":
        return redirect('view_attempt', attempt_id=attempt.id)
    return redirect('dashboard')





from django.shortcuts import render

def test_static(request):
    return render(request, 'quiz_app/test_static.html')
