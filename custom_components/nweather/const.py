DOMAIN = "nweather"
VERSION = "1.0.0"


BSE_URL = "https://weather.naver.com/today/{}"


CONF_RGN_CD = "rgn_cd"

VAR_HOURLY  = r"var hourlyFcastListJson = [^;]+;"
VAR_WEEKLY  = r"var weeklyFcastListJson = [^;]+;"

VAR_CARDMAP = r"var cardMapJson = {[^;]+};"

VAR_LIVING  = r"var lifeIndexDataForLivingListJson = [^;]+;"
VAR_HEALTH  = r"var lifeIndexDataForHealthListJson = [^;]+;"

VAR_MONTHLY = r"var monthlyWetrOutlk2ListJson = [^;]+;"
VAR_SEASON  = r"var seasonWetrOutlk2ListJson = [^;]+;"

VAR_SUMMARY = r"var weatherSummary = {[^;]+};"


ATTR_NOWFCAST = "nowFcast"

ATTR_AIRFCAST = "airFcast"
ATTR_O3       = "stationO3"
ATTR_O3_GRADE = "stationO3Legend1"
O3_LVL   = { "좋음" : 1, "보통" : 2, "나쁨" : 3, "매우나쁨": 4 }

ATTR_HDAYFCAST = "hdayFcastList"

ATTR_UV       = "uv"

ATTR_SUNRISE  = "sunRiseTm"
ATTR_SUNSET   = "sunSetTm"

CONDITIONS = {
    "맑음": "sunny",
    "맑음(밤)":"clear-night",

    "흐림": "cloudy",
    "구름많음": "cloudy",
    "구름조금" : "partlycloudy",
    "대체로 흐림": "partlycloudy",

    "비" : "rainy",
    "가끔 비": "rainy",
    "흐리고 한때 비": "rainy",
    "흐리고 가끔 비":"rainy",
    "흐리고 비": "rainy",
    "소나기" : "rainy",
    "약한비": "rainy",
    "강한비": "pouring",

    "번개뇌우" : "lightning",

    "눈": "snowy",
    "가끔 눈": "snowy",
    "우박": "snowy",

    "황사": "fog",
    "안개": "fog",
}
