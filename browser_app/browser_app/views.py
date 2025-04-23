import os
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def start_browser(request):
    browser = request.GET.get('browser')
    url = request.GET.get('url')
    
    script = f'''
    tell application "{browser}"
        activate
        open location "{url}"
    end tell
    '''

    try:
        subprocess.run(['osascript', '-e', script], check=True)
        return JsonResponse({'message': f'{browser} started with {url}'})
    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def stop_browser(request):
    browser = request.GET.get('browser')
    
    # script = f'tell application "{browser}" to quit'
    script = f'tell application "{browser}" to close front window'

    try:
        subprocess.run(['osascript', '-e', script], check=True)
        return JsonResponse({'message': f'{browser} quit successfully'})
    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_active_tab_url(request):
    browser = request.GET.get('browser')
    
    try:
        if browser == "Google Chrome":
            command = 'tell application "Google Chrome" to return URL of active tab of front window'
        elif browser == "Safari":
            command = 'tell application "Safari" to return URL of front document'
        elif browser == "Firefox":
            command = '''
            tell application "System Events"
                tell process "Firefox"
                    set frontmost to true
                    delay 0.5
                    try
                        set theURL to value of text field 1 of toolbar 1 of window 1
                        return theURL
                    on error
                        return "Could not get URL"
                    end try
                end tell
            end tell
            '''

        output = subprocess.check_output(['osascript', '-e', command]).decode().strip()
        return JsonResponse({'active_tab_url': output})
    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': 'Unable to fetch active tab URL'}, status=500)


@csrf_exempt
def cleanup_browser(request):
    browser = request.GET.get('browser', '').lower()

    try:
        if browser == "google chrome":
            chrome_path = os.path.expanduser('~/Library/Application Support/Google/Chrome')
            subprocess.run(['rm', '-rf', chrome_path], check=True)
        
        elif browser == "firefox":
            firefox_path = os.path.expanduser('~/Library/Application Support/Firefox')
            subprocess.run(['rm', '-rf', firefox_path], check=True)
        
        elif browser == "safari":
            safari_cache = os.path.expanduser('~/Library/Caches/com.apple.Safari')
            safari_history = os.path.expanduser('~/Library/Safari/History.db')
            safari_cookies = os.path.expanduser('~/Library/Cookies/Cookies.binarycookies')
            safari_local_storage = os.path.expanduser('~/Library/Safari/LocalStorage')
            safari_databases = os.path.expanduser('~/Library/Safari/Databases')

            # Clear Safari cache & related data
            for path in [safari_cache, safari_history, safari_cookies, safari_local_storage, safari_databases]:
                subprocess.run(['rm', '-rf', path], check=True)

        else:
            return JsonResponse({'error': f'Unsupported browser: {browser}'}, status=400)

        return JsonResponse({'message': f'{browser} data cleaned up'})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': f'Error cleaning browser data: {str(e)}'}, status=500)
