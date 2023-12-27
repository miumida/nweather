from homeassistant.const import (
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
    PERCENTAGE,
    SPEED_METERS_PER_SECOND,
    CONCENTRATION_PARTS_PER_MILLION,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PRECIPITATION_MILLIMETERS_PER_HOUR,
    EntityCategory,
)

DOMAIN = "nweather"
VERSION = "1.0.0"


BSE_URL = "https://weather.naver.com/today/{}"


CONF_RGN_CD = "rgn_cd"

VAR_HOURLY  = r"var hourlyFcastListJson = \[[^;]+\];"
VAR_WEEKLY  = r"var weeklyFcastListJson = [^;]+;"

VAR_CARDMAP = r"var cardMapJson = {[^;]+};"

VAR_LIVING  = r"var lifeIndexDataForLivingListJson = [^;]+;"
VAR_HEALTH  = r"var lifeIndexDataForHealthListJson = [^;]+;"

VAR_MONTHLY = r"var monthlyWetrOutlk2ListJson = [^;]+;"
VAR_SEASON  = r"var seasonWetrOutlk2ListJson = [^;]+;"

VAR_SUMMARY = r"var weatherSummary = {[^;]+};"

VAR_API = r"var blockApiResult = {[^;]+};"


ATTR_NOWFCAST = "nowFcast"

ATTR_TMPR    = "tmpr"
ATTR_HUMD    = "humd"
ATTR_WETRTXT = "wetrTxt"
ATTR_YTMPR   = "ytmpr"
ATTR_STMPR   = "stmpr"
ATTR_1HRAIN = "oneHourRainAmt"

ATTR_AIRFCAST = "airFcast"

ATTR_AIR_STNM = "stationName"
ATTR_PM10  = "stationPM10"
ATTR_PM10A = "stationPM10Aqi"
ATTR_PM10L = "stationPM10Legend1"
ATTR_PM25  = "stationPM25"
ATTR_PM25A = "stationPM25Aqi"
ATTR_PM25L = "stationPM25Legend1"
ATTR_KHAI  = "stationKhai"
ATTR_KHAIL = "stationKhaiLegend1"
ATTR_SO2   = "stationSo2"
ATTR_SO2L  = "stationSo2Legend1"
ATTR_CO    = "stationCo"
ATTR_COL   = "stationCoLegend1"
ATTR_NO2   = "stationNo2"
ATTR_NO2L  = "stationNo2Legend1"

ATTR_O3       = "stationO3"
ATTR_O3_GRADE = "stationO3Legend1"
O3_LVL   = { "좋음" : 1, "보통" : 2, "나쁨" : 3, "매우나쁨": 4 }

ATTR_HDAYFCAST = "hdayFcastList"

ATTR_UV       = "uv"

ATTR_GRADE  = "grade"
ATTR_FIGURE = "figure"
ATTR_LBTXT  = "labelText"
ATTR_GTXTS  = "guideTextSummary"
ATTR_GTXTD  = "guideTextDetail"

ATTR_SUNRISE  = "sriseTm"
ATTR_SUNSET   = "ssetTm"

ATTR_NEWS1 = "news1"

ATTR_NOW = {
    ATTR_TMPR    : ["현재온도", TEMP_CELSIUS, "mdi:thermometer", "", ""],
    ATTR_HUMD    : ["현재습도", PERCENTAGE, "mdi:water-percent", "", ""],
    ATTR_WETRTXT : ["현재날씨", "", "mdi:weather-cloudy", "", ""],
    ATTR_YTMPR   : ["현재날씨정보", "", "mdi:weather-cloudy", "", ""],
    ATTR_STMPR   : ["체감온도", TEMP_CELSIUS, "mdi:thermometer", "", ""],
    ATTR_UV      : ["자외선", "", "mdi:weather-sunny-alert", "", ""],
    ATTR_PM10L    : ["미세먼지등급", "", "mdi:blur", "", ""],
    ATTR_PM25L    : ["초미세먼지등급", "", "mdi:blur-linear","", ""],
    ATTR_KHAIL    : ["통합대기등급", "", "mdi:blur", "", ""],
    ATTR_AIR_STNM : ["미세먼지 측정소", "", "mdi:map-marker-radius", EntityCategory.DIAGNOSTIC, "" ],
    ATTR_1HRAIN   : ["시간당강수량", "mm", "mdi:weather-pouring", "", ""],

    ATTR_NEWS1    : ["뉴스1", "", "mdi:newspaper", "", ""],
} 


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
    "흐려져 비": "rainy",
    "구름많고 비": "rainy",
    "구름많고 한때 비" : "rainy",
    "구름많고 가끔 비" : "rainy",
    "소나기" : "rainy",
    "약한비": "rainy",
    "강한비": "pouring",

    "번개뇌우" : "lightning",

    "눈": "snowy",
    "구름많고 가끔 눈" : "snowy",
    "구름많고 한때 눈" : "snowy",
    "가끔 눈": "snowy",
    "우박": "snowy",

    "흐리고 비/눈": "snowy",
    "구름많고 비/눈": "snowy",

    "황사": "fog",
    "안개": "fog",
}
