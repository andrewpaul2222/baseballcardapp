from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404
from .models import Card
from django.db.models import Avg

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid login credentials'})
    return render(request, 'login.html')


def create_account(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'create_account.html', {'form': form})
    

@login_required
def dashboard(request):
    user = request.user

    if request.method == 'POST':
        name = request.POST['name']
        team = request.POST['team']
        description = request.POST['description']
        price = request.POST['price']
        condition = request.POST['condition']

        Card.objects.create(
            user=user,
            name=name,
            team=team,
            description=description,
            price=price,
            condition=condition
        )

    user_baseball_cards = Card.objects.filter(user=user)

    return render(request, 'dashboard.html', {'user': user, 'user_baseball_cards': user_baseball_cards})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def edit_card(request, card_id):
    card = get_object_or_404(Card, id=card_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        team = request.POST.get('team')
        description = request.POST.get('description')
        price = request.POST.get('price')
        condition = request.POST.get('condition')

        card.name = name
        card.team = team
        card.description = description
        card.price = price
        card.condition = condition
        card.save()

        return redirect('dashboard')

    return render(request, 'edit_card.html', {'card': card})


@login_required
def delete_card(request, card_id):
    card = get_object_or_404(Card, id=card_id)

    if request.method == 'POST':
        card.delete()
        return redirect('dashboard')

    return render(request, 'delete_card.html', {'card': card})


def view_all_cards(request):
    all_baseball_cards = Card.objects.all()
    teams = Card.objects.values('team').distinct()
    return render(request, 'view_all_cards.html', {'all_baseball_cards': all_baseball_cards, 'teams': teams})



def like_card(request, card_id):
    card = get_object_or_404(Card, id=card_id)
    card.numLikes += 1
    card.save()
    return redirect('view_all_cards')

def dislike_card(request, card_id):
    card = get_object_or_404(Card, id=card_id)
    card.numDislikes += 1
    card.save()
    return redirect('view_all_cards')


@login_required
def return_to_dashboard(request):
    return redirect('dashboard')

def filter_cards(request):
    player_filter = request.POST.get('player_filter')
    team_filter = request.POST.get('team_filter')
    condition_filter = request.POST.get('condition_filter')
    min_price = request.POST.get('min_price')
    max_price = request.POST.get('max_price')

    filtered_card_ids = Card.objects.values_list('id', flat=True)

    if player_filter:
        filtered_card_ids = filtered_card_ids.filter(name=player_filter).values_list('id', flat=True)

    if team_filter:
        filtered_card_ids = Card.objects.filter(id__in=filtered_card_ids, team=team_filter).values_list('id', flat=True)

    if condition_filter:
        filtered_card_ids = Card.objects.filter(id__in=filtered_card_ids, condition=condition_filter).values_list('id', flat=True)

    if min_price and max_price:
        filtered_card_ids = Card.objects.filter(id__in=filtered_card_ids, price__range=(min_price, max_price)).values_list('id', flat=True)

    all_players = Card.objects.values_list('name', flat=True).distinct()
    teams = Card.objects.values_list('team', flat=True).distinct()
    conditions = Card.objects.values_list('condition', flat=True).distinct()

    request.session['filtered_card_ids'] = list(filtered_card_ids)

    filtered_cards = Card.objects.filter(id__in=filtered_card_ids)

    return render(request, 'view_all_cards.html', {'all_players': all_players, 'all_baseball_cards': filtered_cards, 'teams': teams, 'conditions': conditions})


def generate_report(request):
    filtered_card_ids = request.session.get('filtered_card_ids', [])

    filtered_cards = Card.objects.filter(id__in=filtered_card_ids)

    avg_likes = filtered_cards.aggregate(Avg('numLikes'))['numLikes__avg'] if filtered_cards else 0
    avg_dislikes = filtered_cards.aggregate(Avg('numDislikes'))['numDislikes__avg'] if filtered_cards else 0

    card_with_max_likes = filtered_cards.order_by('-numLikes').first()
    card_with_max_dislikes = filtered_cards.order_by('-numDislikes').first()

    return render(request, 'generate_report.html', {
        'avg_likes': avg_likes,
        'avg_dislikes': avg_dislikes,
        'card_with_max_likes': card_with_max_likes,
        'card_with_max_dislikes': card_with_max_dislikes,
    })









from django.db import connection

def filter_cards1(request):
    player_filter = request.POST.get('player_filter')
    team_filter = request.POST.get('team_filter')
    condition_filter = request.POST.get('condition_filter')
    min_price = request.POST.get('min_price')
    max_price = request.POST.get('max_price')

    query = """
        SELECT id FROM baseballcards_card WHERE 1=1
    """
    params = []

    if player_filter:
        query += " AND name = %s"
        params.append(player_filter)

    if team_filter:
        query += " AND team = %s"
        params.append(team_filter)

    if condition_filter:
        query += " AND condition = %s"
        params.append(condition_filter)

    if min_price and max_price:
        query += " AND price BETWEEN %s AND %s"
        params.extend([min_price, max_price])

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        filtered_card_ids = [row[0] for row in cursor.fetchall()]

    all_players = Card.objects.values_list('name', flat=True).distinct()
    teams = Card.objects.values_list('team', flat=True).distinct()
    conditions = Card.objects.values_list('condition', flat=True).distinct()

    request.session['filtered_card_ids'] = filtered_card_ids

    filtered_cards = Card.objects.filter(id__in=filtered_card_ids)

    return render(request, 'view_all_cards.html', {'all_players': all_players, 'all_baseball_cards': filtered_cards, 'teams': teams, 'conditions': conditions})


def generate_report1(request):
    filtered_card_ids = request.session.get('filtered_card_ids', [])

    query = "SELECT * FROM baseballcards_card WHERE id IN %s"
    with connection.cursor() as cursor:
        cursor.execute(query, [tuple(filtered_card_ids)])
        filtered_cards = [Card(*row) for row in cursor.fetchall()]

    avg_likes = sum(card.numLikes for card in filtered_cards) / len(filtered_cards) if filtered_cards else 0
    avg_dislikes = sum(card.numDislikes for card in filtered_cards) / len(filtered_cards) if filtered_cards else 0

    query_max_likes = "SELECT * FROM baseballcards_card WHERE id IN %s ORDER BY numLikes DESC LIMIT 1"
    query_max_dislikes = "SELECT * FROM baseballcards_card WHERE id IN %s ORDER BY numDislikes DESC LIMIT 1"

    with connection.cursor() as cursor:
        cursor.execute(query_max_likes, [tuple(filtered_card_ids)])
        card_with_max_likes = Card(*cursor.fetchone()) if cursor.rowcount else None

        cursor.execute(query_max_dislikes, [tuple(filtered_card_ids)])
        card_with_max_dislikes = Card(*cursor.fetchone()) if cursor.rowcount else None

    return render(request, 'generate_report.html', {
        'avg_likes': avg_likes,
        'avg_dislikes': avg_dislikes,
        'card_with_max_likes': card_with_max_likes,
        'card_with_max_dislikes': card_with_max_dislikes,
    })
