from pathlib import Path
from datetime import date

import yaml
import csv
import pandas as pd
import jpholiday
# yaml読み込み①
# yaml読み込み②
# csv読み込み(家電オンオフのやつ)
# ③の列カラムに対応したキーを持つ消費電力を掛けて待機電力を全体に足す
# csv読み込み→消費電力作成の流れをもう一回やって休日用・平日用で作り分ける
# 電力をw/mに変換
class Load:
    rated_yaml = Path(__file__).parent / "config"/ "homeappliances_rated.yaml"
    standby_yaml = Path(__file__).parent / "config"/ "homeappliances_standby.yaml"
    with open(rated_yaml)as f:
        rated_power = yaml.safe_load(f)
    with open(standby_yaml)as f:
        standby_power = yaml.safe_load(f)

    def __init__(self, 
        wdcsv: Path = Path(__file__).parent / "config"/ "weekday.csv", 
        hdcsv: Path = Path(__file__).parent / "config"/ "holiday.csv"
    ) -> None:
        self.operationwd_df = pd.read_csv(wdcsv,index_col=0, parse_dates=True)
        self.operationwd_df.index = [ts.time() for ts in self.operationwd_df.index.to_pydatetime()]
        self.operationhd_df = pd.read_csv(hdcsv,index_col=0, parse_dates=True)
        self.operationhd_df.index = [ts.time() for ts in self.operationhd_df.index.to_pydatetime()]
        
    def run(self):
        datetime_list = pd.date_range('2020-01-01', '2020-12-31 23:30:00', freq='30T').to_pydatetime()
        load_df = pd.DataFrame(columns=self.rated_power['rated'].keys(), index=datetime_list)
        for ts in datetime_list:
            if (ts.weekday() in [5,6]) or (jpholiday.is_holiday(ts)):
                powerdf = self.operationhd_df
            else:
                powerdf = self.operationwd_df
            for appliance, watt in self.rated_power['rated'].items():
                usedtime = powerdf.loc[ts.time()][appliance] / 60
                load_df.loc[ts][appliance] = usedtime * watt
            for appliance, watt in self.standby_power['standby'].items():
                if powerdf.loc[ts.time()][appliance] != 0:
                    pass
                else:
                    load_df.loc[ts][appliance] = watt / 2
        return load_df


if __name__ == "__main__":
    load = Load()
    # print(load.operation_df)
    df = load.run()
    df.to_csv("result.csv")
    
    

