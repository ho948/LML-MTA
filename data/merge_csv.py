import pandas as pd
import glob
import os
from datetime import datetime
from pyproj import CRS, Transformer

start_time = datetime.now()
print(f"시작 시각: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

# 1. CSV 파일들이 있는 폴더 지정
folder_path = "./csv/"
file_list = glob.glob(os.path.join(folder_path, "*.csv"))

# 2. 모든 CSV 읽어 합치기
df_list = []
for file in file_list:
    if file == "./csv/ULSAN_NG_201801_201805.csv": # 해당 파일은 csv 타입이 아니라 바이너리 타입이라 읽을 수가 없음.
        continue
    df_list.append(pd.read_csv(file))
df = pd.concat(df_list, ignore_index=True)

# 3. 나이대별 컬럼 통합 생성
df["age_00_09"] = df["m00"] + df["f00"]
df["age_10_19"] = df["m10"] + df["f10"] + df["m15"] + df["f15"]
df["age_20_39"] = (df["m20"] + df["f20"] + df["m25"] + df["f25"] +
                   df["m30"] + df["f30"] + df["m35"] + df["f35"])
df["age_40_64"] = (df["m40"] + df["f40"] + df["m45"] + df["f45"] +
                   df["m50"] + df["f50"] + df["m55"] + df["f55"] +
                   df["m60"] + df["f60"])
df["age_65_up"] = df["m65"] + df["f65"] + df["m70"] + df["f70"]

# 4. cell id 기준으로 aggregation
final_df = df.groupby("id", as_index=False).agg({
    "x": "first",
    "y": "first",
    "age_00_09": "sum",
    "age_10_19": "sum",
    "age_20_39": "sum",
    "age_40_64": "sum",
    "age_65_up": "sum",
    "total": "sum",
    "admi_cd": "first"
})

# 5. x, y -> 경도(longitude), 위도(lattitude) 변환
proj4 = "+proj=tmerc +lat_0=38 +lon_0=128 +k=0.9999 +x_0=400000 +y_0=600000 " \
        "+ellps=bessel +towgs84=-115.8,474.99,674.11,1.16,-2.31,-1.63,6.43 +units=m +no_defs"
src_crs = CRS.from_proj4(proj4)
dst_crs = CRS.from_epsg(4326)  # WGS84
transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
xs = final_df["x"].to_numpy()
ys = final_df["y"].to_numpy()
lons, lats = transformer.transform(xs, ys)
final_df["lon"] = lons
final_df["lat"] = lats

# 6. CSV 저장
file_name = "result/merged.csv"
final_df.to_csv(file_name, index=False)
end_time = datetime.now()
print(f"✅ 완료: {file_name}")
print(f"종료 시각: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"총 실행 시간: {str(end_time - start_time)}")