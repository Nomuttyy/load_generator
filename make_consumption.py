from pathlib import Path
from datetime import date

import yaml
import csv
import pandas as pd
import jpholiday

class Load:
    rated_yaml = Path(__file__).parent / "config"/ "homeappliances_rated.yaml" # yaml読み込み
    standby_yaml = Path(__file__).parent / "config"/ "homeappliances_standby.yaml"
    with open(rated_yaml)as f:
        rated_power = yaml.safe_load(f)
    with open(standby_yaml)as f:
        standby_power = yaml.safe_load(f)

    def __init__(self, 
        wdcsv: Path = Path(__file__).parent / "config"/ "weekday.csv",  # パス指定
        hdcsv: Path = Path(__file__).parent / "config"/ "holiday.csv"   # パス指定
    ) -> None:
        self.operationwd_df = pd.read_csv(wdcsv,index_col=0, parse_dates=True) # CSV読み込み
        self.operationwd_df.index = [ts.time() for ts in self.operationwd_df.index.to_pydatetime()]
        self.operationhd_df = pd.read_csv(hdcsv,index_col=0, parse_dates=True) # CSV読み込み
        self.operationhd_df.index = [ts.time() for ts in self.operationhd_df.index.to_pydatetime()]
        
    def run(self):
        """
        指定された日時の範囲で30分おきに消費電力を計算する
        """
        datetime_list = pd.date_range('2020-01-01', '2020-12-31 23:30:00', freq='30T').to_pydatetime()
        load_df = pd.DataFrame(columns=self.rated_power['rated'].keys(), index=datetime_list) # 空データフレーム作成
        for ts in datetime_list:
            if (ts.weekday() in [5,6]) or (jpholiday.is_holiday(ts)): # 土日祝日判定
                operationdf = self.operationhd_df
            else:
                operationdf = self.operationwd_df
            for appliance, watt in self.rated_power['rated'].items():
                usedtime = operationdf.loc[ts.time()][appliance] / 60 # ワット数を1分単位に小分け
                load_df.loc[ts][appliance] = usedtime * watt # データフレームに消費電力を加算
            for appliance, watt in self.standby_power['standby'].items():
                if operationdf.loc[ts.time()][appliance] != 0: # 待機電力判定
                    pass
                else:
                    load_df.loc[ts][appliance] = watt / 2 # データフレームに待機電力を加算
        return load_df


if __name__ == "__main__":
    load = Load()
    # print(load.operation_df)
    df = load.run()
    df.to_csv("result.csv") # CSV出力
    
    

