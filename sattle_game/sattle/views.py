from django.shortcuts import render, redirect
from .models import SatelliteImage, Guess, WebsiteStats,Feedback, UserScore
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Max
from datetime import datetime, timedelta
import random
import math
from django.http import JsonResponse
from django.contrib.sessions.models import Session
from django.contrib.admin.views.decorators import staff_member_required
import uuid
from django.views.decorators.csrf import csrf_exempt

COUNTRY_CENTER_COORDS = {'Aruba': (12.5013629, -69.9618475), 'Afghanistan': (33.7680065, 66.2385139),
'Angola': (-11.8775768, 17.5691241), 'Anguilla': (18.1954947, -63.0750234), 'Åland Islands': (60.1715116, 20.077392261506848), 'Albania': (41.000028, 19.9999619), 'Andorra': (42.5407167, 1.5732033), 'United Arab Emirates': (24.0002488, 53.9994829), 'Argentina': (-34.9964963, -64.9672817), 'Armenia': (40.7696272, 44.6736646), 'American Samoa': (-14.297124, -170.7131481), 'Antarctica': (-79.4063075, 0.3149312), 'French Southern Territories': (-49.237441950000004, 69.62275903679347), 'Antigua and Barbuda': (17.2234721, -61.9554608), 'Australia': (-24.7761086, 134.755), 'Austria': (47.59397, 14.12456), 'Azerbaijan': (40.3936294, 47.7872508), 'Burundi': (-3.426449, 29.9324519), 'Belgium': (50.6402809, 4.6667145), 'Benin': (9.5293472, 2.2584408), 'Burkina Faso': (12.0753083, -1.6880314), 'Bangladesh': (24.4769288, 90.2934413), 'Bulgaria': (42.6073975, 25.4856617), 'Bahrain': (26.1551249, 50.5344606), 'Bahamas': (24.7736546, -78.0000547), 'Bosnia and Herzegovina': (44.3053476, 17.5961467), 'Saint Barthélemy': (17.8967693, -62.825598), 'Belarus': (53.4250605, 27.6971358), 'Belize': (16.8259793, -88.7600927), 'Bermuda': (32.2937417, -64.7815286), 'Bolivia, Plurinational State of': (-17.0568696, -64.9912286), 'Brazil': (-10.3333333, -53.2), 'Barbados': (13.1500331, -59.5250305), 'Brunei Darussalam': (4.4137155, 114.5653908), 'Bhutan': (27.549511, 90.5119273), 'Bouvet Island': (-54.4202012, 3.3593786), 'Botswana': (-23.1681782, 24.5928742), 'Central African Republic': (7.0323598, 19.9981227), 'Canada': (61.0666922, -107.991707), 'Cocos (Keeling) Islands': (-12.0728315, 96.8409375), 'Switzerland': (46.7985624, 8.2319736), 'Chile': (-31.7613365, -71.3187697), 'China': (35.000074, 104.999927), "Côte d'Ivoire": (7.9897371, -5.5679458), 'Cameroon': (4.6125522, 13.1535811), 'Congo, The Democratic Republic of the': (-2.9814344, 23.8222636), 'Congo': (-2.9814344, 23.8222636), 'Cook Islands': (-19.99697155, -157.78587140620786), 'Colombia': (4.099917, -72.9088133), 'Comoros': (-12.2045176, 44.2832964), 'Cabo Verde': (16.0000552, -24.0083947), 'Costa Rica': (9.536456900000001, -84.17566257468567), 'Cuba': (23.0131338, -80.8328748), 'Curaçao': (12.1176488, -68.9309263), 'Christmas Island': (-10.49131475, 105.61713690269079), 'Cayman Islands': (19.703182249999998, -79.9174627243246), 'Cyprus': (34.9823018, 33.1451285), 'Czechia': (49.7439047, 15.3381061), 'Germany': (51.1638175, 10.4478313), 'Djibouti': (11.8145966, 42.8453061), 'Dominica': (19.0974031, -70.3028026), 'Denmark': (55.670249, 10.3333283), 'Dominican Republic': (19.0974031, -70.3028026), 'Algeria': (28.0000272, 2.9999825), 'Ecuador': (-1.3397668, -79.3666965), 'Egypt': (26.2540493, 29.2675469), 'Eritrea': (15.9500319, 37.9999668), 'Western Sahara': (24.16819605, -13.892143025000001), 'Spain': (39.3260685, -4.8379791), 'Estonia': (58.7523778, 25.3319078), 'Ethiopia': (10.2116702, 38.6521203), 'Finland': (63.2467777, 25.9209164), 'Fiji': (-18.1239696, 179.0122737), 'Falkland Islands (Malvinas)': (-51.9492937, -59.5383657), 'France': (46.603354, 1.8883335), 'Faroe Islands': (62.0448724, -7.0322972), 'Micronesia, Federated States of': (8.6062347, 151.832744331612), 'Gabon': (-0.8999695, 11.6899699), 'United Kingdom': (54.7023545, -3.2765753), 'Georgia': (41.6809707, 44.0287382), 'Guernsey': (49.4566233, -2.5822348), 'Ghana': (8.0300284, -1.0800271), 'Gibraltar': (36.1285933, -5.3474761), 'Guinea': (10.7226226, -10.7083587), 'Guadeloupe': (16.2528827, -61.5686855), 'Gambia': (13.470062, -15.4900464), 'Guinea-Bissau': (11.815215, -15.2351044), 'Equatorial Guinea': (1.613172, 10.5170357), 'Greece': (38.9953683, 21.9877132), 'Grenada': (12.1360374, -61.6904045), 'Greenland': (77.6192349, -42.8125967), 'Guatemala': (15.5855545, -90.345759), 'French Guiana': (4.0039882, -52.999998), 'Guam': (13.4499943, 144.7651677), 'Guyana': (4.8417097, -58.6416891), 'Hong Kong': (22.2793278, 114.1628131), 'Heard Island and McDonald Islands': (-53.0166353, 72.955751), 'Honduras': (15.2572432, -86.0755145), 'Croatia': (45.3658443, 15.6575209), 'Haiti': (19.1399952, -72.3570972), 'Hungary': (47.1817585, 19.5060937), 'Indonesia': (-2.4833826, 117.8902853), 'Isle of Man': (54.1936805, -4.5591148), 'India': (22.3511148, 78.6677428), 'British Indian Ocean Territory': (-5.3497093499999995, 71.86064227010121), 'Ireland': (52.865196, -7.9794599), 'Iran, Islamic Republic of': (36.2665119, 59.5999861), 'Iraq': (33.0955793, 44.1749775), 'Iceland': (64.9841821, -18.1059013), 'Israel': (30.8124247, 34.8594762), 'Italy': (42.6384261, 12.674297), 'Jamaica': (18.1850507, -77.3947693), 'Jersey': (49.2214561, -2.1358386), 'Jordan': (31.1667049, 36.941628), 'Japan': (36.5748441, 139.2394179), 'Kazakhstan': (48.1012954, 66.7780818), 'Kenya': (1.4419683, 38.4313975), 'Kyrgyzstan': (41.5089324, 74.724091), 'Cambodia': (12.5433216, 104.8144914), 'Kiribati': (0.3448612, 173.6641773), 'Saint Kitts and Nevis': (17.250512, -62.6725973), 'Korea, Republic of': (53.7276489, 91.4189745), 'Kuwait': (29.2733964, 47.4979476), "Lao People's Democratic Republic": (20.0171109, 103.378253), 'Lebanon': (33.8750629, 35.843409), 'Liberia': (5.7499721, -9.3658524), 'Libya': (26.8234472, 18.1236723), 'Saint Lucia': (13.8250489, -60.975036), 'Liechtenstein': (47.1416307, 9.5531527), 'Sri Lanka': (7.5554942, 80.7137847), 'Lesotho': (-29.6039267, 28.3350193), 'Lithuania': (55.3500003, 23.7499997), 'Luxembourg': (49.8158683, 6.1296751), 'Latvia': (56.8406494, 24.7537645), 'Macao': (22.1757605, 113.5514142), 'Saint Martin (French part)': (18.0814066, -63.0467131), 'Morocco': (31.1728205, -7.3362482), 'Monaco': (48.1371079, 11.5753822), 'Moldova, Republic of': (46.6745434, 29.7521996), 'Madagascar': (-18.9249604, 46.4416422), 'Maldives': (3.7203503, 73.2244152), 'Mexico': (23.6585116, -102.0077097), 'Marshall Islands': (8.230816999999998, 167.7953223704529), 'North Macedonia': (41.6171214, 21.7168387), 'Mali': (16.3700359, -2.2900239), 'Malta': (35.8885993, 14.4476911), 'Myanmar': (17.1750495, 95.9999652), 'Montenegro': (42.9868853, 19.5180992), 'Mongolia': (46.8250388, 103.8499736), 'Northern Mariana Islands': (15.1753648, 145.7379338), 'Mozambique': (-19.302233, 34.9144977), 'Mauritania': (20.2540382, -9.2399263), 'Montserrat': (16.7417041, -62.1916844), 'Martinique': (14.6113732, -60.9620777), 'Mauritius': (-20.2759451, 57.5703566), 'Malawi': (-13.2687204, 33.9301963), 'Malaysia': (4.5693754, 102.2656823), 'Mayotte': (-12.823048, 45.1520755), 'Namibia': (-23.2335499, 17.3231107), 'New Caledonia': (-21.3019905, 165.4880773), 'Niger': (17.7356214, 9.3238432), 'Norfolk Island': (-29.0328038, 167.9483137), 'Nigeria': (9.6000359, 7.9999721), 'Nicaragua': (12.6090157, -85.2936911), 'Niue': (-19.0536414, -169.861341), 'Netherlands': (52.2434979, 5.6343227), 'Norway': (61.1529386, 8.7876653), 'Nepal': (28.1083929, 84.0917139), 'Nauru': (-0.5252306, 166.9324426), 'New Zealand': (-41.5000831, 172.8344077), 'Oman': (21.0000287, 57.0036901), 'Pakistan': (30.3308401, 71.247499), 'Panama': (8.559559, -81.1308434), 'Pitcairn': (-25.0657719, -130.101782), 'Peru': (-6.8699697, -75.0458515), 'Philippines': (12.7503486, 122.7312101), 'Palau': (5.3783537, 132.9102573), 'Papua New Guinea': (-5.6816069, 144.2489081), 'Poland': (52.215933, 19.134422), 'Puerto Rico': (18.2247706, -66.4858295), "Korea, Democratic People's Republic of": (38.233686649999996, 127.00873073371443), 'Portugal': (39.6621648, -8.1353519), 'Paraguay': (-23.3165935, -58.1693445), 'Palestine': (31.978333, 35.205721), 'French Polynesia': (-17.0243749, -144.6434898), 'Qatar': (25.3336984, 51.2295295), 'Réunion': (-21.1309332, 55.5265771), 'Romania': (45.9852129, 24.6859225),'Russia': (64.6863136, 97.7453061), 'Rwanda': (-1.9646631, 30.0644358), 'Saudi Arabia': (25.6242618, 42.3528328), 'Sudan': (14.5844444, 29.4917691), 'Senegal': (14.4750607, -14.4529612), 'Singapore': (1.357107, 103.8194992), 'South Georgia and the South Sandwich Islands': (-54.8432857, -35.8090698), 'Svalbard and Jan Mayen': (78.7198519, 20.3493328), 'Solomon Islands': (-8.7053941, 159.1070693851845), 'Sierra Leone': (8.6400349, -11.8400269), 'El Salvador': (13.8000382, -88.9140683), 'San Marino': (43.9458623, 12.458306), 'Somalia': (8.3676771, 49.083416), 'Saint Pierre and Miquelon': (46.8374544, -56.2120555), 'Serbia': (44.1534121, 20.55144), 'South Sudan': (7.8699431, 29.6667897), 'Sao Tome and Principe': (0.9713095, 7.02255), 'Suriname': (4.1413025, -56.0771187), 'Slovakia': (48.7411522, 19.4528646), 'Slovenia': (46.1199444, 14.8153333), 'Sweden': (59.6749712, 14.5208584), 'Eswatini': (-26.5624806, 31.3991317), 'Sint Maarten (Dutch part)': (18.03319875, -63.09292513566134), 'Seychelles': (-4.6574977, 55.4540146), 'Syria': (34.6401861, 39.0494106), 'Turks and Caicos Islands': (21.721746, -71.5527809), 'Chad': (15.6134137, 19.0156172), 'Togo': (8.7800265, 1.0199765), 'Thailand': (14.8971921, 100.83273), 'Tajikistan': (38.6281733, 70.8156541), 'Tokelau': (-9.1676396, -171.819687), 'Turkmenistan': (39.3763807, 59.3924609), 'Timor-Leste': (-8.7443169, 126.063482), 'Tonga': (-19.9160819, -175.202642), 'Trinidad and Tobago': (10.7466905, -61.0840075), 'Tunisia': (33.8439408, 9.400138), 'Turkey': (38.9597594, 34.9249653), 'Tuvalu': (-8.6405212, 179.1582918181797),'Taiwan': (23.9739374, 120.9820179), 'Tanzania, United Republic of': (-6.5247123, 35.7878438), 'Uganda': (1.5333554, 32.2166578), 'Ukraine': (49.4871968, 31.2718321), 'United States Minor Outlying Islands': (16.7288207, -169.5333824), 'Uruguay': (-32.8755548, -56.0201525), 'United States': (39.7837304, -100.445882), 'Uzbekistan': (41.32373, 63.9528098), 'Saint Vincent and the Grenadines': (12.90447, -61.2765569), 'Venezuela': (8.0018709, -66.1109318), 'Virgin Islands, British': (18.4024395, -64.5661642), 'Virgin Islands, U.S.': (17.7289564, -64.75901597858353), 'Viet Nam': (15.9266657, 107.9650855),
'Vanuatu': (-16.5255069, 168.1069154), 'Wallis and Futuna': (-13.289402, -176.204224), 'Samoa': (-13.7693895, -172.12005), 'Yemen': (16.3471243, 47.8915271), 'South Africa': (-28.8166236, 24.991639), 'Zambia': (-14.5189121, 27.5589884), 'Zimbabwe': (-18.4554963, 29.7468414)}

def reset_score(request):
    request.session['score'] = 0
    return JsonResponse({"message": "Score reset successfully", "score": 0})

def calculate_direction(lat1, lon1, lat2, lon2):
    lat_diff = lat2 - lat1
    lon_diff = lon2 - lon1

    lat_threshold = 12  # or adjust based on your preference
    lon_threshold = 12  # or adjust based on your preference

    if abs(lat_diff) < lat_threshold and abs(lon_diff) < lon_threshold:
        if abs(lat_diff) > abs(lon_diff):
            lat_direction = "S" if lat_diff > 0 else "N"
            lon_direction = ""
        else:
            lon_direction = "W" if lon_diff > 0 else "E"
            lat_direction = ""
    else:
        lat_direction = "S" if lat_diff > 0 else "N" if lat_diff < 0 else ""
        lon_direction = "W" if lon_diff > 0 else "E" if lon_diff < 0 else ""

    return lat_direction + lon_direction

def calculate_distance(image, guessed_country):
    # Splitting the coordinates from the model
    lat1, lon1 = map(float, image.coordinates.split(','))

    # Fetching the center coordinates of the guessed country
    lat2, lon2 = COUNTRY_CENTER_COORDS.get(guessed_country, (0, 0))

    # Radius of the Earth in kilometers
    R = 6371.0

    # Differences in coordinates
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    correct = True if guessed_country.lower() == image.country.lower() else False
    direction = calculate_direction(lat1, lon1, lat2, lon2)
    return distance, correct, direction
    
def home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        random_image = random.choice(SatelliteImage.objects.all())
        old_correct_answer = request.session.get('correct_answer')
        request.session['correct_answer'] = random_image.country
        return JsonResponse({
            "new_image_url": random_image.image.url,
            "new_image_id": random_image.id,
            "old_correct_answer": old_correct_answer
        })
    user_identifier = request.COOKIES.get('user_identifier')
    user_score = UserScore.objects.filter(user_identifier=user_identifier).first()
    user_high_score = user_score.high_score if user_score else 0

    global_high_score = UserScore.objects.aggregate(Max('high_score'))['high_score__max'] or 0

    # Get a random satellite image for the game
    request.session['score'] = 0
    random_image = random.choice(SatelliteImage.objects.all())
    context = {
        'image_url': random_image,
        'image': random_image,
        'countries': COUNTRY_CENTER_COORDS.keys(),
        'user_high_score': user_high_score,
        'global_high_score': global_high_score
    }
    request.session['correct_answer'] = random_image.country
    stats, created = WebsiteStats.objects.get_or_create(pk=1)
    stats.total_sessions += 1
    stats.save()
    user_identifier = request.COOKIES.get('user_identifier')
    if not user_identifier:
        user_identifier = str(uuid.uuid4())
    response = render(request, 'sattle/home.html', context)
    response.set_cookie('user_identifier', user_identifier, max_age=60*60*24*365)
    return response

def submit_guess(request):
    if request.method == 'POST':
        # Fetch image_id and guessed_country from POST data, provide default values
        image_id = request.POST.get('image_id', '')
        guessed_country = request.POST.get('guessed_country_no_autofill', '')
        # Ensure image_id is an integer
        try:
            image_id = int(image_id)
        except ValueError:
            return JsonResponse({"error": "Invalid image ID provided."}, status=400)

        # Get the selected satellite image
        image = get_object_or_404(SatelliteImage, pk=image_id)
        # Calculate the distance
        distance, correct, direction = calculate_distance(image, guessed_country)
        user_identifier = request.COOKIES.get('user_identifier', 'unknown')
        # Save the guess

        # Return the correct/incorrect status based on the 'correct' value
        stats, created = WebsiteStats.objects.get_or_create(pk=1)
        stats.total_guesses += 1
        request.session['correct_answer'] = image.country
        user_score, created = UserScore.objects.get_or_create(user_identifier=user_identifier)
        if correct:
            request.session['score'] = request.session.get('score', 0) + 1
            score = request.session.get('score')
            new_image = SatelliteImage.objects.order_by('?').first()
            stats.total_correct_guesses += 1
            stats.save()
            beat_user_high_score, beat_global_high_score= False, False
            if score > user_score.high_score:
                user_score.high_score = score
                user_score.save()
                if not request.session.get('beat_user_high_score', False):
                    beat_user_high_score = True
            global_high_score = UserScore.objects.aggregate(Max('high_score'))['high_score__max'] or 0
            if score > global_high_score and not request.session.get('beat_global_high_score', False):
                beat_global_high_score = True
            if beat_user_high_score:
                request.session['beat_user_high_score'] = True
            if beat_global_high_score:
                request.session['beat_global_high_score'] = True
            request.session['correct_answer'] = new_image.country
            response = JsonResponse({
                "correct": True, 
                "message": "Correct!", 
                "score": score, 
                "new_image_url": new_image.image.url, 
                "new_image_id": new_image.id,
                'correct_answer': new_image.country,
                'user_high_score': user_score.high_score,
                'global_high_score':UserScore.objects.aggregate(Max('high_score'))['high_score__max'] or 0,
                'beat_user_high_score': beat_user_high_score,
                'beat_global_high_score': beat_global_high_score,
                })
        else:
            stats.save()
            score = request.session.get('score')
            response = JsonResponse({
        "correct": False,
        "message": f"The distance between the center of {guessed_country} and the image coordinates is {distance:.2f} km {direction}.",
        "score": score,
        "new_image_url": image.image.url,  # Use current image
        "new_image_id": image.id,  # Use current image ID
        'correct_answer': image.country,
        'user_high_score': user_score.high_score,
        'global_high_score':UserScore.objects.aggregate(Max('high_score'))['high_score__max'] or 0,
        'beat_global_high_score': False,
        'beat_user_high_score': False,
    })
        guess = Guess(image=image, guessed_country=guessed_country, distance=distance,user_identifier=user_identifier,correct=correct, direction=direction,correct_country=image.country)
        guess.save()
    # Redirect to home if request is not POST
    return response

@csrf_exempt
def submit_feedback(request):
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback')
        user_identifier = request.COOKIES.get('user_identifier', 'unknown')
        Feedback.objects.create(feedback_text=feedback_text, user_identifier=user_identifier)
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})

@staff_member_required
def view_guesses(request):
    # Directly fetch all guesses from the Guess model
    all_guesses = Guess.objects.all()
    
    stats = WebsiteStats.objects.get(pk=1)

    # # Stats for the last 24 hours
    last_24_hours = datetime.now() - timedelta(days=1)
    total_guesses_24h = Guess.objects.filter(timestamp__gte=last_24_hours).count()
    total_correct_guesses_24h = Guess.objects.filter(timestamp__gte=last_24_hours, correct=True).count()

    # User table stats
    user_stats = Guess.objects.values('user_identifier').annotate(
        total_guesses=Count('id'),
        correct_guesses=Count('id', filter=Q(correct=True))
    ).order_by('-total_guesses')

    context = {
        'guesses': all_guesses,
        'stats': stats,
        'user_stats': user_stats,
        'total_guesses_24h': total_guesses_24h,
        'total_correct_guesses_24h': total_correct_guesses_24h,
    }

    return render(request, 'sattle/guesses.html', context)