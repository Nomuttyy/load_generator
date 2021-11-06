from abc import abstractproperty
from pathlib import Path
from datetime import date,datetime

import yaml
import pandas as pd
import jpholiday
from tqdm import tqdm

class Load:
    rated_yaml = Path(__file__).parent / "config"/ "rated.yaml" # yaml読み込み
    standby_yaml = Path(__file__).parent / "config"/ "standby.yaml"
    with open(rated_yaml)as f:
        rated_power = yaml.safe_load(f)
    with open(standby_yaml)as f:
        standby_power = yaml.safe_load(f)
    

    def __init__(self, 
        wdcsv: Path = Path(__file__).parent / "config"/ "weekday.csv",  # 平日の行動パターンcsvパス指定
        hdcsv: Path = Path(__file__).parent / "config"/ "holiday.csv",  # 休日の行動パターンcsvパス指定
        weather2020: Path = Path(__file__).parent / "data"/ "hakusantemp_2020.csv"
    ) -> None:
        self.operationwd_df = pd.read_csv(wdcsv,index_col=0, parse_dates=True) # csv読み込み
        self.operationwd_df.index = [ts.time() for ts in self.operationwd_df.index.to_pydatetime()]
        self.operationhd_df = pd.read_csv(hdcsv,index_col=0, parse_dates=True) # csv読み込み
        self.operationhd_df.index = [ts.time() for ts in self.operationhd_df.index.to_pydatetime()]
        self.weather2020_df = pd.read_csv(weather2020,index_col=0, parse_dates=True)

    def aircon(self, temp: float, used_minutes: float, time) -> float:
        standby_minutes = 30 - used_minutes
        wh = 0
        getup_time = datetime.datetime.strptime("08:00:00", '%H:%M:%S')
        goodnight_time = datetime.datetime.strptime("23:59:59", '%H:%M:%S')
        if getup_time < time < goodnight_time :
            if temp > 25:
                wh += self.rated_power["aircon_cooler"] * used_minutes /60
            elif temp < 15:
                wh += self.rated_power["aircon_heater"] * used_minutes /60 
        wh += self.standby_power["aircon_cooler"] * standby_minutes / 60
        return wh


    def refrigerator(self, temp: float, used_minutes: float) -> float:
        return self.rated_power["refrigerator"]
    

    def other_appliances(self, appliances: str, used_minutes: float) -> float:
        standby_minutes: float = 30 - used_minutes
        wh: float = 0
        wh += self.standby_power[appliances] * standby_minutes / 60
        wh += self.rated_power[appliances] * used_minutes / 60
        return wh

    def run(self):
        """
        指定された日時の範囲で30分おきに消費電力を計算する

        """
        datetime_list = pd.date_range('2020-01-01', '2020-12-31 23:30:00', freq='30T').to_pydatetime()
        load_df = pd.DataFrame(columns=self.standby_power.keys(), index=datetime_list) # 空データフレーム作成
        # print(load_df)
        # return
        for ts in tqdm(datetime_list):
            if (ts.weekday() in [5,6]) or (jpholiday.is_holiday(ts)): # 土日祝日判定
                operationdf = self.operationhd_df
            else:
                operationdf = self.operationwd_df
            for appliance in self.rated_power.items():
                used_time = operationdf.loc[ts.time()][appliance]
                if (appliance == "aircon_cooler") or (appliance == "aircon_heater"):
                    temp = self.weather2020_df.loc[ts]["気温"]
                    time = ts.time()
                    load_df.loc[ts][appliance] = self.aircon(temp, used_time, time)
                elif appliance == "refrigerator":
                    temp = self.weather2020_df.loc[ts]["気温"]
                    load_df.loc[ts][appliance] = self.refrigerator(temp, used_time)
                else:
                    load_df.loc[ts][appliance] = self.other_appliances(appliance, used_time)
        return load_df



if __name__ == "__main__":
    load = Load()
    # print(load.operation_df)
    df = load.run()
    df.to_csv("result.csv") # CSV出力
    
    

