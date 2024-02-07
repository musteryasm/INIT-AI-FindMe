from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
import openai
import json
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import googletrans

openai.api_key = settings.ACCESS_KEY

def index(request):
    return render(request, 'index.html')


def detect_language(text):
    url = "https://translation.googleapis.com/language/translate/v2/detect"
    params = {
        'key': settings.GOOGLE_API_KEY,
        'q': text
    }
    response = requests.post(url, params=params)
    print(text)
    print("HELLO")
    # print(response)
    return response.json()['data']['detections'][0][0]['language']


@csrf_exempt
def ai(request):
    if request.method == 'POST':
        try:            
            print(request.body.decode('utf-8'))
            user_input = request.POST.get('input')
            # print(user_input)
            inp_lang = detect_language(user_input)
            print(googletrans.LANGUAGES[inp_lang])
            if googletrans.LANGUAGES[inp_lang] == 'english':
                prompt = settings.PROMPT + user_input
                # prompt = "You are a geography expert and good at solving puzzles. The main task for you is to identify the name of place from the given input. There can be place already mentioned in the input however you need to critically think about given input and only then determine the actual location that input corresponds to. Tell me what is most relevant location by the input an also give a crisp explaination on why you think that location is most relevant. The input is as follows: "+user_input
                response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                    )
                print(response)
                context = {'generated_response': response['choices'][0]['message']['content']}
                return render(request, 'map.html', context)
            else:
                prompt = settings.LANG_PROMPT + googletrans.LANGUAGES[inp_lang]
                response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                    )
                print(response['choices'][0]['message']['content'])
                context = {'generated_response': response['choices'][0]['message']['content']}
                return render(request, 'map.html', context)
            # return HttpResponse(googletrans.LANGUAGES[inp_lang])
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)