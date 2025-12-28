import akshare as ak
from datetime import datetime, timedelta
import pandas as pd

print("测试AKShare指数数据获取功能...")

try:
    # 测试获取上证指数历史数据
    start_date = (datetime.now() - timedelta(days=10)).strftime('%Y%m%d')
    end_date = datetime.now().strftime('%Y%m%d')
    
    print(f"获取上证指数({start_date} to {end_date})数据...")
    df_sh = ak.stock_zh_index_daily_em(symbol="sh000001")
    df_sh['date'] = pd.to_datetime(df_sh['date']).dt.date
    df_sh_filtered = df_sh[(df_sh['date'] >= datetime.strptime(start_date, '%Y%m%d').date()) & 
                           (df_sh['date'] <= datetime.strptime(end_date, '%Y%m%d').date())]
    print(f"上证指数数据获取成功，共{len(df_sh_filtered)}条记录")
    print("最近几条记录:")
    print(df_sh_filtered[['date', 'close']].tail())
    
    # 测试获取深证成指历史数据
    print(f"\n获取深证成指({start_date} to {end_date})数据...")
    df_sz = ak.stock_zh_index_daily_em(symbol="sz399102")
    df_sz['date'] = pd.to_datetime(df_sz['date']).dt.date
    df_sz_filtered = df_sz[(df_sz['date'] >= datetime.strptime(start_date, '%Y%m%d').date()) & 
                           (df_sz['date'] <= datetime.strptime(end_date, '%Y%m%d').date())]
    print(f"深证成指数据获取成功，共{len(df_sz_filtered)}条记录")
    print("最近几条记录:")
    print(df_sz_filtered[['date', 'close']].tail())
    
    # 测试获取实时指数数据
    print("\n获取实时指数数据...")
    df_spot = ak.stock_zh_index_spot_em()
    print(f"实时指数数据获取成功，共{len(df_spot)}条记录")
    
    # 获取特定指数的实时价格
    sh_data = df_spot[df_spot['代码'] == '000001']
    if not sh_data.empty:
        print(f"上证指数实时价格: {sh_data.iloc[0]['最新价']}")
    
    sz_data = df_spot[df_spot['代码'] == '399102']
    if not sz_data.empty:
        print(f"深证成指实时价格: {sz_data.iloc[0]['最新价']}")
    
    print("\nAKShare指数数据获取测试完成！")
    
except Exception as e:
    print(f"AKShare测试失败: {e}")