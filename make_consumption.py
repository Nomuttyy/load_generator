import yaml
import csv
import pandas as pd
# yaml読み込み①
# yaml読み込み②
# csv読み込み(家電オンオフのやつ)
# ③の列カラムに対応したキーを持つ消費電力を掛けて待機電力を全体に足す
# csv読み込み→消費電力作成の流れをもう一回やって休日用・平日用で作り分ける
# 電力をw/mに変換
class Load:
    def __init__(self) -> None:
        with open('homeappliances_rated.yaml')as f:
            self.rated_power = yaml.safe_load(f)
        with open('homeappliances_standby.yaml')as f:
            self.standby_power = yaml.safe_load(f)
        self.operation_df = pd.read_csv('lifecycle.csv',index_col=0, parse_dates=True)
        self.operation_df.index = [ts.time() for ts in self.operation_df.index.to_pydatetime()]
        
    def run(self):
        datetime_list = pd.date_range('2020-01-01', '2020-12-31 23:30:00', freq='30T').to_pydatetime()
        load_df = pd.DataFrame(columns=self.rated_power['rated'].keys(), index=datetime_list)
        for ts in datetime_list:
            for key, watt in self.rated_power['rated'].items():
                usedtime = self.operation_df.loc[ts.time()][key] / 60
                load_df.loc[ts][key] = usedtime * watt
        return load_df


if __name__ == "__main__":
    load = Load()
    # print(load.operation_df)
    df = load.run()
    df.to_csv("result.csv")
    
    

