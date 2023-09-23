import requests
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import geopandas as gpd
from shapely.geometry import Point
import random
import pycountry
from countryinfo import CountryInfo
from collections import defaultdict
import qwikidata
import qwikidata.sparql
import geonamescache


def get_coordinates_from_google(city_or_province, country,api_key):
    """
    Fetch coordinates (latitude and longitude) for a given city or province using Google's Geocoding API.
    
    :param city_or_province: Name of the city or province to get coordinates for.
    :param api_key: Google API key.
    :return: Tuple containing latitude and longitude.
    """
    
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    parameters = {
        "address": city_or_province+' '+country,
        "key": api_key
    }

    response = requests.get(base_url, params=parameters)
    response_data = response.json()

    if response_data['status'] == 'OK':
        location = response_data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        print(f"Error fetching coordinates for {city_or_province}: {response_data['status']}")
        return None, None

def get_city_wikidata(city, country):
    query = """
    SELECT ?city ?cityLabel ?country ?countryLabel ?population
    WHERE
    {
      ?city rdfs:label '%s'@en.
      ?city wdt:P1082 ?population.
      ?city wdt:P17 ?country.
      ?city rdfs:label ?cityLabel.
      ?country rdfs:label ?countryLabel.
      FILTER(LANG(?cityLabel) = "en").
      FILTER(LANG(?countryLabel) = "en").
      FILTER(CONTAINS(?countryLabel, "%s")).
    }
    """ % (city, country)

    res = qwikidata.sparql.return_sparql_query_results(query)
    out = res['results']['bindings'][0]
    return out['population']['value']
# Geocoding setup
geolocator = Nominatim(user_agent="name_of_your_app")

# List of 10 largest countries by area
LARGEST_COUNTRIES = ['Russia', 'Canada', 'China', 'United States', 'Brazil', 'Australia', 'India', 'Argentina', 'Kazakhstan', 'Algeria']

def random_coordinate_from_country(country, world_data):
    print(country)
    country_geom = world_data[world_data.name == country].geometry.iloc[0]
    while True:
        minx, miny, maxx, maxy = country_geom.bounds
        random_point = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if country_geom.contains(random_point):
            return (random_point.y, random_point.x)

def get_capital_coordinates(country_name):
    try:
        # Get the country object
        # country_obj = pycountry.countries.get(name=country_name)
        # if not country_obj:
            # Try with common name if official name doesn't match
            # country_obj = pycountry.countries.search_fuzzy(country_name)[0]
        # Get the capital name
        country_obj = CountryInfo(country_name)
        capital_name = country_obj.capital()
    except:
        capital_name = None
    # Geocode the capital
    location = geolocator.geocode(f"{capital_name}, {country_name}") if capital_name is not None else geolocator.geocode(country_name)
    return (location.latitude, location.longitude)

def fetch_mapbox_image(lat, lon, width=1000, height=500, zoom=12, bearing=0):
    MAPBOX_ENDPOINT = "https://api.mapbox.com/styles/v1/{username}/{style_id}/static/{lon},{lat},{zoom},{bearing}/{width}x{height}"
    USERNAME = "mapbox"
    STYLE_ID = "satellite-v9"
    MAPBOX_TOKEN = "pk.eyJ1Ijoic2FsZWhhbHdlciIsImEiOiJjbG1vYmdvaDgwdmNqMnNyMjBxNDVrdzFhIn0.OO8AOMjU_4YnSX9ROXkZ-A" 
    url = MAPBOX_ENDPOINT.format(
        username=USERNAME,
        style_id=STYLE_ID,
        lon=lon,
        lat=lat,
        zoom=zoom,
        bearing=bearing,
        width=width,
        height=height
    ) + f"?access_token={MAPBOX_TOKEN}"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return None

def fetch_google_image(lat, long, zoom=12, size="1000x500"):
    API_ENDPOINT = "https://maps.googleapis.com/maps/api/staticmap?"
    API_KEY = 'AIzaSyDcUzVY2uLwSV_bLGR6S2h_p8y2ATzpZuw'
    url = (API_ENDPOINT +
           "center={},{}&".format(lat, long) +
           "zoom={}&".format(zoom) +
           "size={}&".format(size) +
           "maptype=satellite&" +
           "key={}".format(API_KEY))
    response = requests.get(url)
    return response.content if response.status_code == 200 else None

# 1. Loop over countries and get random coordinates
COUNTRY_CENTER_COORDS = {'Bouvet Island': (-54.4202012, 3.3593786), 'Botswana': (-23.1681782, 24.5928742), 'Central African Republic': (7.0323598, 19.9981227), 'Canada': (61.0666922, -107.991707), 'Cocos (Keeling) Islands': (-12.0728315, 96.8409375), 'Switzerland': (46.7985624, 8.2319736), 'Chile': (-31.7613365, -71.3187697), 'China': (35.000074, 104.999927), "Côte d'Ivoire": (7.9897371, -5.5679458), 'Cameroon': (4.6125522, 13.1535811), 'Congo, The Democratic Republic of the': (-2.9814344, 23.8222636), 'Congo': (-2.9814344, 23.8222636), 'Cook Islands': (-19.99697155, -157.78587140620786), 'Colombia': (4.099917, -72.9088133), 'Comoros': (-12.2045176, 44.2832964), 'Cabo Verde': (16.0000552, -24.0083947), 'Costa Rica': (9.536456900000001, -84.17566257468567), 'Cuba': (23.0131338, -80.8328748), 'Curaçao': (12.1176488, -68.9309263), 'Christmas Island': (-10.49131475, 105.61713690269079), 'Cayman Islands': (19.703182249999998, -79.9174627243246), 'Cyprus': (34.9823018, 33.1451285), 'Czechia': (49.7439047, 15.3381061), 'Germany': (51.1638175, 10.4478313), 'Djibouti': (11.8145966, 42.8453061), 'Dominica': (19.0974031, -70.3028026), 'Denmark': (55.670249, 10.3333283), 'Dominican Republic': (19.0974031, -70.3028026), 'Algeria': (28.0000272, 2.9999825), 'Ecuador': (-1.3397668, -79.3666965), 'Egypt': (26.2540493, 29.2675469), 'Eritrea': (15.9500319, 37.9999668), 'Spain': (39.3260685, -4.8379791), 'Estonia': (58.7523778, 25.3319078), 'Ethiopia': (10.2116702, 38.6521203), 'Finland': (63.2467777, 25.9209164), 'Fiji': (-18.1239696, 179.0122737), 'Falkland Islands (Malvinas)': (-51.9492937, -59.5383657), 'France': (46.603354, 1.8883335), 'Faroe Islands': (62.0448724, -7.0322972), 'Micronesia, Federated States of': (8.6062347, 151.832744331612), 'Gabon': (-0.8999695, 11.6899699), 'United Kingdom': (54.7023545, -3.2765753), 'Georgia': (41.6809707, 44.0287382), 'Guernsey': (49.4566233, -2.5822348), 'Ghana': (8.0300284, -1.0800271), 'Gibraltar': (36.1285933, -5.3474761), 'Guinea': (10.7226226, -10.7083587), 'Guadeloupe': (16.2528827, -61.5686855), 'Gambia': (13.470062, -15.4900464), 'Guinea-Bissau': (11.815215, -15.2351044), 'Equatorial Guinea': (1.613172, 10.5170357), 'Greece': (38.9953683, 21.9877132), 'Grenada': (12.1360374, -61.6904045), 'Greenland': (77.6192349, -42.8125967), 'Guatemala': (15.5855545, -90.345759), 'French Guiana': (4.0039882, -52.999998), 'Guam': (13.4499943, 144.7651677), 'Guyana': (4.8417097, -58.6416891), 'Hong Kong': (22.2793278, 114.1628131), 'Heard Island and McDonald Islands': (-53.0166353, 72.955751), 'Honduras': (15.2572432, -86.0755145), 'Croatia': (45.3658443, 15.6575209), 'Haiti': (19.1399952, -72.3570972), 'Hungary': (47.1817585, 19.5060937), 'Indonesia': (-2.4833826, 117.8902853), 'Isle of Man': (54.1936805, -4.5591148), 'India': (22.3511148, 78.6677428), 'British Indian Ocean Territory': (-5.3497093499999995, 71.86064227010121), 'Ireland': (52.865196, -7.9794599), 'Iran, Islamic Republic of': (36.2665119, 59.5999861), 'Iraq': (33.0955793, 44.1749775), 'Iceland': (64.9841821, -18.1059013), 'Israel': (30.8124247, 34.8594762), 'Italy': (42.6384261, 12.674297), 'Jamaica': (18.1850507, -77.3947693), 'Jersey': (49.2214561, -2.1358386), 'Jordan': (31.1667049, 36.941628), 'Japan': (36.5748441, 139.2394179), 'Kazakhstan': (48.1012954, 66.7780818), 'Kenya': (1.4419683, 38.4313975), 'Kyrgyzstan': (41.5089324, 74.724091), 'Cambodia': (12.5433216, 104.8144914), 'Kiribati': (0.3448612, 173.6641773), 'Saint Kitts and Nevis': (17.250512, -62.6725973), 'Korea, Republic of': (53.7276489, 91.4189745), 'Kuwait': (29.2733964, 47.4979476), "Lao People's Democratic Republic": (20.0171109, 103.378253), 'Lebanon': (33.8750629, 35.843409), 'Liberia': (5.7499721, -9.3658524), 'Libya': (26.8234472, 18.1236723), 'Saint Lucia': (13.8250489, -60.975036), 'Liechtenstein': (47.1416307, 9.5531527), 'Sri Lanka': (7.5554942, 80.7137847), 'Lesotho': (-29.6039267, 28.3350193), 'Lithuania': (55.3500003, 23.7499997), 'Luxembourg': (49.8158683, 6.1296751), 'Latvia': (56.8406494, 24.7537645), 'Macao': (22.1757605, 113.5514142), 'Saint Martin (French part)': (18.0814066, -63.0467131), 'Morocco': (31.1728205, -7.3362482), 'Monaco': (48.1371079, 11.5753822), 'Moldova, Republic of': (46.6745434, 29.7521996), 'Madagascar': (-18.9249604, 46.4416422), 'Maldives': (3.7203503, 73.2244152), 'Mexico': (23.6585116, -102.0077097), 'Marshall Islands': (8.230816999999998, 167.7953223704529), 'North Macedonia': (41.6171214, 21.7168387), 'Mali': (16.3700359, -2.2900239), 'Malta': (35.8885993, 14.4476911), 'Myanmar': (17.1750495, 95.9999652), 'Montenegro': (42.9868853, 19.5180992), 'Mongolia': (46.8250388, 103.8499736), 'Northern Mariana Islands': (15.1753648, 145.7379338), 'Mozambique': (-19.302233, 34.9144977), 'Mauritania': (20.2540382, -9.2399263), 'Montserrat': (16.7417041, -62.1916844), 'Martinique': (14.6113732, -60.9620777), 'Mauritius': (-20.2759451, 57.5703566), 'Malawi': (-13.2687204, 33.9301963), 'Malaysia': (4.5693754, 102.2656823), 'Mayotte': (-12.823048, 45.1520755), 'Namibia': (-23.2335499, 17.3231107), 'New Caledonia': (-21.3019905, 165.4880773), 'Niger': (17.7356214, 9.3238432), 'Norfolk Island': (-29.0328038, 167.9483137), 'Nigeria': (9.6000359, 7.9999721), 'Nicaragua': (12.6090157, -85.2936911), 'Niue': (-19.0536414, -169.861341), 'Netherlands': (52.2434979, 5.6343227), 'Norway': (61.1529386, 8.7876653), 'Nepal': (28.1083929, 84.0917139), 'Nauru': (-0.5252306, 166.9324426), 'New Zealand': (-41.5000831, 172.8344077), 'Oman': (21.0000287, 57.0036901), 'Pakistan': (30.3308401, 71.247499), 'Panama': (8.559559, -81.1308434), 'Pitcairn': (-25.0657719, -130.101782), 'Peru': (-6.8699697, -75.0458515), 'Philippines': (12.7503486, 122.7312101), 'Palau': (5.3783537, 132.9102573), 'Papua New Guinea': (-5.6816069, 144.2489081), 'Poland': (52.215933, 19.134422), 'Puerto Rico': (18.2247706, -66.4858295), "Korea, Democratic People's Republic of": (38.233686649999996, 127.00873073371443), 'Portugal': (39.6621648, -8.1353519), 'Paraguay': (-23.3165935, -58.1693445), 'Palestine': (31.978333, 35.205721), 'French Polynesia': (-17.0243749, -144.6434898), 'Qatar': (25.3336984, 51.2295295), 'Réunion': (-21.1309332, 55.5265771), 'Romania': (45.9852129, 24.6859225), 'Russia': (64.6863136, 97.7453061), 'Rwanda': (-1.9646631, 30.0644358), 'Saudi Arabia': (25.6242618, 42.3528328), 'Sudan': (14.5844444, 29.4917691), 'Senegal': (14.4750607, -14.4529612), 'Singapore': (1.357107, 103.8194992), 'South Georgia and the South Sandwich Islands': (-54.8432857, -35.8090698), 'Svalbard and Jan Mayen': (78.7198519, 20.3493328), 'Solomon Islands': (-8.7053941, 159.1070693851845), 'Sierra Leone': (8.6400349, -11.8400269), 'El Salvador': (13.8000382, -88.9140683), 'San Marino': (43.9458623, 12.458306), 'Somalia': (8.3676771, 49.083416), 'Saint Pierre and Miquelon': (46.8374544, -56.2120555), 'Serbia': (44.1534121, 20.55144), 'South Sudan': (7.8699431, 29.6667897), 'Sao Tome and Principe': (0.9713095, 7.02255), 'Suriname': (4.1413025, -56.0771187), 'Slovakia': (48.7411522, 19.4528646), 'Slovenia': (46.1199444, 14.8153333), 'Sweden': (59.6749712, 14.5208584), 'Eswatini': (-26.5624806, 31.3991317), 'Sint Maarten (Dutch part)': (18.03319875, -63.09292513566134), 'Seychelles': (-4.6574977, 55.4540146), 'Syria': (34.6401861, 39.0494106), 'Turks and Caicos Islands': (21.721746, -71.5527809), 'Chad': (15.6134137, 19.0156172), 'Togo': (8.7800265, 1.0199765), 'Thailand': (14.8971921, 100.83273), 'Tajikistan': (38.6281733, 70.8156541), 'Tokelau': (-9.1676396, -171.819687), 'Turkmenistan': (39.3763807, 59.3924609), 'Timor-Leste': (-8.7443169, 126.063482), 'Tonga': (-19.9160819, -175.202642), 'Trinidad and Tobago': (10.7466905, -61.0840075), 'Tunisia': (33.8439408, 9.400138), 'Turkey': (38.9597594, 34.9249653), 'Tuvalu': (-8.6405212, 179.1582918181797),'Taiwan': (23.9739374, 120.9820179), 'Tanzania, United Republic of': (-6.5247123, 35.7878438), 'Uganda': (1.5333554, 32.2166578), 'Ukraine': (49.4871968, 31.2718321), 'United States Minor Outlying Islands': (16.7288207, -169.5333824), 'Uruguay': (-32.8755548, -56.0201525), 'United States': (39.7837304, -100.445882), 'Uzbekistan': (41.32373, 63.9528098), 'Saint Vincent and the Grenadines': (12.90447, -61.2765569), 'Venezuela': (8.0018709, -66.1109318), 'Virgin Islands, British': (18.4024395, -64.5661642), 'Virgin Islands, U.S.': (17.7289564, -64.75901597858353), 'Viet Nam': (15.9266657, 107.9650855),
'Vanuatu': (-16.5255069, 168.1069154), 'Wallis and Futuna': (-13.289402, -176.204224), 'Samoa': (-13.7693895, -172.12005), 'Yemen': (16.3471243, 47.8915271), 'South Africa': (-28.8166236, 24.991639), 'Zambia': (-14.5189121, 27.5589884), 'Zimbabwe': (-18.4554963, 29.7468414)}
# # world_data = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
# countries = world_data["name"].unique()[:5]
# Function to get coordinates of a city within a country

def get_city_coordinates(city_name, country_name):
    location = geolocator.geocode(f"{city_name}, {country_name}")
    if location:
        return (location.latitude, location.longitude)
    return None

country_info_to_coords_name = {}
country_to_cities_coords = {}

# Generating list of countries based on criteria
all_countries = [CountryInfo(name) for name in COUNTRY_CENTER_COORDS.keys()]

def area_key_function(x):
    try:
        if x.info()['area'] is not None:
            return x.info()['area']
        else:
            return -1
    except KeyError:
        print('not found', x.name())
        return -1  # This will push problematic countries to the end of the sorted list

def population_key_function(x):
    try:
        if x.info()['population'] is not None:
            return x.info()['population']
        else:
            return -1
    except KeyError:
        print('not found',x.name())
        return -1  # This will push problematic countries to the end of the sorted list
# For sorting by area

sorted_by_area = sorted(all_countries, key=area_key_function, reverse=True)[:30]
# For sorting by population
sorted_by_population = sorted(all_countries, key=population_key_function, reverse=True)[:70]
selected_countries = set([country.name() for country in sorted_by_area] + [country.name() for country in sorted_by_population])
# Constructing the dictionary
country_to_cities_coords = defaultdict(list)

def get_city_population(city, country_name):
    city_data = get_city_wikidata(city, country_name)
    return city_data


def get_city_coordinates(city, country):
    geolocator = Nominatim(user_agent="your_app_name")
    location = geolocator.geocode(f"{city}, {country}")
    if location:
        return (location.latitude, location.longitude)
    else:
        return None, None

def top_cities_by_country(country_code, all_cities):
    # Filter the cities by the given country code
    cities_in_country = [city for city in all_cities.values() if city['countrycode'] == country_code]
    
    # Sort by population in descending order and take the top 5 cities
    top_5_cities = sorted(cities_in_country, key=lambda x: x['population'], reverse=True)[:5]
    return [cit['name'] for cit in top_5_cities]

for country_name in selected_countries:
    country_info = CountryInfo(country_name)
    # Get the two-letter country code
    # country_code = country_info.iso()['alpha2'].lower()
    # Create a mapping from CountryInfo name to COUNTRY_CENTER_COORDS name
    country_info_to_coords_name[country_info.info()['name']] = country_name

    # Get list of major cities from CountryInfo (we will later fetch detailed data from get_city_opendata)
    gc = geonamescache.GeonamesCache()
    all_cities = gc.get_cities()
    cities = top_cities_by_country(country_info.info()['ISO']['alpha2'],all_cities)

    coords_list = []
    for city in cities:
        coordinates = get_city_coordinates(city, country_name)
        coords_list.append(coordinates)

    country_to_cities_coords[country_info.info()['name']] = coords_list

# Fetching and saving images for each city
for country_info_name, coords_list in country_to_cities_coords.items():
    for lat, lon in coords_list:
        image_data = fetch_google_image(lat, lon)
        if image_data:
            # Use the country name from COUNTRY_CENTER_COORDS for saving the image
            country_coords_name = country_info_to_coords_name[country_info_name]
            filename = "images/" + f"{lat},{lon},{country_coords_name}.png"
            with open(filename, "wb") as f:
                f.write(image_data)