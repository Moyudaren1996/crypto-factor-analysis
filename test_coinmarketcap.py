"""
测试CoinMarketCap API能否获取5分钟级别的市值数据
"""
import requests
from datetime import datetime, timedelta
import json

# CoinMarketCap API配置
CMC_API_KEY = "YOUR_API_KEY_HERE"  # 需要在 https://coinmarketcap.com/api/ 注册获取
BASE_URL = "https://pro-api.coinmarketcap.com"

def test_latest_quotes():
    """测试获取最新的市值数据"""
    print("=== 测试1: 获取最新市值数据 ===")

    url = f"{BASE_URL}/v2/cryptocurrency/quotes/latest"

    parameters = {
        'symbol': 'BTC',  # 测试比特币
        'convert': 'USD'
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
    }

    try:
        response = requests.get(url, params=parameters, headers=headers)
        data = response.json()

        if response.status_code == 200:
            print(f"✓ 成功获取数据")
            btc_data = data['data']['BTC'][0]
            quote = btc_data['quote']['USD']

            print(f"币种: {btc_data['name']} ({btc_data['symbol']})")
            print(f"价格: ${quote['price']:.2f}")
            print(f"市值: ${quote['market_cap']:,.0f}")
            print(f"24h交易量: ${quote['volume_24h']:,.0f}")
            print(f"流通供应量: {btc_data['circulating_supply']:,.0f}")
            print(f"最后更新: {quote['last_updated']}")
            print()
            return True
        else:
            print(f"✗ 请求失败: {data}")
            return False

    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_historical_quotes():
    """测试获取历史市值数据（5分钟间隔）"""
    print("=== 测试2: 获取历史市值数据（5分钟间隔）===")

    url = f"{BASE_URL}/v2/cryptocurrency/quotes/historical"

    # 测试最近1小时的数据，5分钟间隔
    time_end = datetime.now()
    time_start = time_end - timedelta(hours=1)

    parameters = {
        'symbol': 'BTC',
        'time_start': time_start.isoformat(),
        'time_end': time_end.isoformat(),
        'interval': '5m',  # 5分钟间隔
        'convert': 'USD'
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
    }

    try:
        response = requests.get(url, params=parameters, headers=headers)
        data = response.json()

        if response.status_code == 200:
            print(f"✓ 成功获取历史数据")

            if 'data' in data and 'BTC' in data['data']:
                quotes = data['data']['BTC'][0]['quotes']
                print(f"获取到 {len(quotes)} 个数据点")
                print()

                # 显示前3个数据点
                for i, quote_data in enumerate(quotes[:3]):
                    quote = quote_data['quote']['USD']
                    print(f"数据点 {i+1}:")
                    print(f"  时间: {quote_data['timestamp']}")
                    print(f"  价格: ${quote['price']:.2f}")
                    print(f"  市值: ${quote['market_cap']:,.0f}")
                    print(f"  交易量: ${quote['volume_24h']:,.0f}")
                    print()

                if len(quotes) > 3:
                    print(f"... (共 {len(quotes)} 个数据点)")

                return True
            else:
                print(f"✗ 数据格式异常: {data}")
                return False
        else:
            print(f"✗ 请求失败 (状态码: {response.status_code})")
            print(f"错误信息: {data}")

            # 检查是否是权限问题
            if 'status' in data and 'error_message' in data['status']:
                error_msg = data['status']['error_message']
                if 'plan' in error_msg.lower() or 'upgrade' in error_msg.lower():
                    print()
                    print("⚠️  这可能需要付费订阅计划才能使用")
                    print("   免费计划可能不支持历史数据或5分钟间隔")

            return False

    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_ohlcv_historical():
    """测试获取OHLCV历史数据"""
    print("=== 测试3: 获取OHLCV历史数据 ===")

    url = f"{BASE_URL}/v2/cryptocurrency/ohlcv/historical"

    time_end = datetime.now()
    time_start = time_end - timedelta(hours=1)

    parameters = {
        'symbol': 'BTC',
        'time_start': time_start.isoformat(),
        'time_end': time_end.isoformat(),
        'interval': '5m',
        'convert': 'USD'
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
    }

    try:
        response = requests.get(url, params=parameters, headers=headers)
        data = response.json()

        if response.status_code == 200:
            print(f"✓ 成功获取OHLCV数据")
            print(json.dumps(data, indent=2)[:500] + "...")
            return True
        else:
            print(f"✗ 请求失败: {data.get('status', {}).get('error_message', '未知错误')}")
            return False

    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def main():
    print("CoinMarketCap API 市值数据测试")
    print("=" * 60)
    print()

    if CMC_API_KEY == "YOUR_API_KEY_HERE":
        print("⚠️  请先设置你的CoinMarketCap API Key")
        print("   1. 访问 https://coinmarketcap.com/api/")
        print("   2. 注册账号并获取免费API Key")
        print("   3. 将API Key填入本脚本的 CMC_API_KEY 变量")
        print()
        return

    # 运行测试
    test1 = test_latest_quotes()
    test2 = test_historical_quotes()
    test3 = test_ohlcv_historical()

    print()
    print("=" * 60)
    print("测试总结:")
    print(f"  最新数据: {'✓ 通过' if test1 else '✗ 失败'}")
    print(f"  历史数据(5分钟): {'✓ 通过' if test2 else '✗ 失败'}")
    print(f"  OHLCV数据: {'✓ 通过' if test3 else '✗ 失败'}")
    print()
    print("注意事项:")
    print("  - 免费计划每月有API调用次数限制")
    print("  - 历史数据和5分钟间隔可能需要付费计划")
    print("  - Enterprise计划才提供高分辨率历史数据")


if __name__ == "__main__":
    main()
