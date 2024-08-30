import json
from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from .models import Friend, Task
from .forms import TaskForm
from django.contrib.auth.models import User
from .models import CustomUser
from django.views.decorators.csrf import csrf_exempt

import logging

logger = logging.getLogger(__name__)

DATABASE_FILE = 'data.txt'

def load_users():
    try:
        with open(DATABASE_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_users(data):
    with open(DATABASE_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def get_all_users():
    users_data = load_users()
    return sorted(users_data.values(), key=lambda x: x['amount'], reverse=True)

def get_user_rank(users, current_user_id):
    for index, user in enumerate(users):
        if user['user_id'] == current_user_id:
            return index + 1
    return None

def get_user_data(user_id):
    users_data = load_users()
    return users_data.get(str(user_id))

def friends(request):
    user_id = request.GET.get('user_id') or request.session.get('user_id')
    if not user_id:
        raise Http404('User ID not provided.')

    request.session['user_id'] = user_id
    user_data = get_user_data(user_id)

    if not user_data:
        return render(request, 'a_friends.html', {'friends': [], 'user_id': user_id, 'message': 'User data not found'})

    invited_usernames = user_data.get('invited_friends_usernames', [])
    users_data = load_users()

    friends = [users_data.get(username) for username in invited_usernames if users_data.get(username)]

    context = {
        'friends': friends,
        'user_id': user_id,
        'message': 'No friends found' if not friends else '',
    }
    
    return render(request, 'a_friends.html', context)



def home(request):
    user_id = request.GET.get('user_id') or request.session.get('user_id')
    request.session['user_id'] = user_id

    if not user_id:
        raise Http404('404.html')

    user_data = get_user_data(user_id)
    if not user_data:
        raise Http404("User not found.")

    request.session['user_id'] = user_id

    context = {
        'coins': user_data['amount'],
        'username': user_data['username'],
        'user_id': user_id,
    }
    return render(request, 'index.html', context)




def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tasks')
    else:
        form = TaskForm()
    return render(request, 'tasks.html', {'form': form})

def remove_task(request, task_id):
    task = Task.objects.get(id=task_id)
    if task:
        task.delete()
    return redirect('tasks')



def tasks(request):
    user_id = request.GET.get('user_id') or request.session.get('user_id')
    request.session['user_id'] = user_id

    tasks = Task.objects.all()

    context = {
        'tasks': tasks,
        'user_id': user_id,
    }

    return render(request, 'tasks.html', context)



def leaderboard(request):
    user_id = request.GET.get('user_id') or request.session.get('user_id')
    if not user_id:
        raise Http404("User ID not provided.")

    request.session['user_id'] = user_id

    users = get_all_users()
    user_index = get_user_rank(users, int(user_id))

    if user_index is None:
        raise Http404("User not found.")

    context = {
        'users': [{
            'username': user['username'],
            'amount': user['amount'],
            'medal': ('🥇' if i == 0 else '🥈' if i == 1 else '🥉' if i == 2 else ''),
            'order': (i + 1) if i > 2 else '',
            'is_current_user': i == (user_index - 1)
        } for i, user in enumerate(users)],
        'user_index': user_index,
        'user_id': user_id,
    }

    return render(request, 'leaderboard.html', context)


@csrf_exempt
def claim_task(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            task_id = data.get('task_id')

            user = CustomUser.objects.get(pk=user_id)
            task = Task.objects.get(pk=task_id)

            user.amount += task.points
            user.save()

            task.delete()

            return JsonResponse({'status': 'success', 'message': 'Task claimed successfully', 'new_amount': user.amount})
        except CustomUser.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        except Task.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Task not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



@csrf_exempt
def update_amount(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = str(data.get('user_id'))
        task_amount = data.get('task_amount')

        users_data = load_users()

        if user_id in users_data:
            users_data[user_id]['amount'] += task_amount
            save_users(users_data)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'User not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)



def add_task(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        points = data.get('points')
        button_link = data.get('button_link')
        
        task = Task(title=title, points=points, button_link=button_link)
        task.save()
        
        return JsonResponse({'status': 'success', 'message': 'Task added successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
