import tushare as ts
import os
from datetime import datetime, timedelta

# 设置token（请替换为您的实际token）
token = os.getenv('TUSHARE_TOKEN', 'your_token_here')
ts.set_token(token)
pro = ts.pro_api()

print("测试tushare API连接...")

try:
    # 测试获取股票数据
    df = pro.daily(ts_code='600001.SH', 
                   start_date=(datetime.now() - timedelta(days=10)).strftime('%Y%m%d'),
                   end_date=datetime.now().strftime('%Y%m%d'))
    print(f"成功获取股票数据，共{len(df)}条记录")
    print(df.head())
except Exception as e:
    print(f"获取股票数据失败: {e}")

try:
    # 测试获取指数数据
    df_index = pro.index_daily(ts_code='000001.SH',
                               start_date=(datetime.now() - timedelta(days=10)).strftime('%Y%m%d'),
                               end_date=datetime.now().strftime('%Y%m%d'))
    print(f"\n成功获取指数数据，共{len(df_index)}条记录")
    print(df_index.head())
except Exception as e:
    print(f"获取指数数据失败: {e}")