from geopy.geocoders import Nominatim

# 初始化地理編碼器
geolocator = Nominatim(user_agent="my_application")

# 獲取當前位置
location = geolocator.geocode("當前位置")

# 獲取經緯度
if location:
    latitude = location.latitude
    longitude = location.longitude
    print(f"經度: {longitude}, 緯度: {latitude}")
else:
    print("無法獲取當前位置")