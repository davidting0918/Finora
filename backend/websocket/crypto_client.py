# simple_crypto_client.py - 簡單的加密貨幣客戶端
import asyncio
import json
from typing import Dict, List

import websockets


class SimpleCryptoClient:
    def __init__(self):
        self.uri = "ws://localhost:8000/ws/crypto"
        self.websocket = None
        self.running = False

        # 儲存最新價格
        self.latest_prices: Dict[str, dict] = {}
        self.available_symbols: List[str] = []

    async def connect(self):
        """連接到服務"""
        try:
            self.websocket = await websockets.connect(self.uri)
            self.running = True
            print("✅ 連接成功！")
            return True
        except Exception as e:
            print(f"❌ 連接失敗：{e}")
            return False

    async def listen(self):
        """監聽價格更新"""
        try:
            while self.running:
                message = await self.websocket.recv()
                data = json.loads(message)

                # 處理歡迎訊息
                if data.get("type") == "welcome":
                    print(f"🎉 {data['message']}")
                    self.available_symbols = data.get("available_symbols", [])
                    print(f"📋 找到 {len(self.available_symbols)} 個交易對")

                    # 自動訂閱所有交易對
                    await self.subscribe_all()

                # 處理價格更新
                elif data.get("type") == "price_update":
                    price_data = data["data"]
                    symbol = price_data["symbol"]
                    price = price_data["price"]
                    change = price_data["change_24h"]

                    # 儲存最新價格
                    self.latest_prices[symbol] = price_data

                    # 顯示價格更新
                    trend = "📈" if change >= 0 else "📉"
                    print(f"{trend} {symbol}: ${price:.6f} ({change:+.2f}%)")

                # 處理訂閱確認
                elif data.get("type") == "subscribed":
                    symbol = data["symbol"]
                    print(f"✅ 已訂閱 {symbol}")

                # 處理錯誤
                elif data.get("type") == "error":
                    print(f"❌ 錯誤：{data['message']}")

        except websockets.exceptions.ConnectionClosed:
            print("🔌 連接已關閉")
        except Exception as e:
            print(f"💥 錯誤：{e}")

    async def subscribe_all(self):
        """訂閱所有交易對"""
        print(f"📊 訂閱所有 {len(self.available_symbols)} 個交易對...")

        for symbol in self.available_symbols:
            command = {"type": "subscribe", "symbol": symbol}
            await self.websocket.send(json.dumps(command))
            await asyncio.sleep(0.1)  # 稍微延遲

        print("🎯 完成訂閱！")

    async def get_all_prices(self):
        """取得所有價格"""
        if self.websocket:
            command = {"type": "get_all_prices"}
            await self.websocket.send(json.dumps(command))

    async def disconnect(self):
        """斷開連接"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
        print("👋 已斷開連接")


# 使用範例
async def main():
    client = SimpleCryptoClient()

    # 連接
    if not await client.connect():
        return

    # 開始監聽（這會自動訂閱所有交易對）
    listen_task = asyncio.create_task(client.listen())

    try:
        print("\n⏰ 即時價格監控中... (按 Ctrl+C 停止)")

        # 每 30 秒顯示一次統計
        while True:
            await asyncio.sleep(30)

            print(f"\n📊 統計：已收到 {len(client.latest_prices)} 個交易對的價格")

            # 顯示所有最新價格
            print("💰 最新價格：")
            for symbol, data in client.latest_prices.items():
                change = data["change_24h"]
                trend = "📈" if change >= 0 else "📉"
                print(f"   {trend} {symbol}: ${data['price']:.6f} ({change:+.2f}%)")

            print("-" * 50)

    except KeyboardInterrupt:
        print("\n⏹️ 停止監控...")

    finally:
        listen_task.cancel()
        await client.disconnect()


if __name__ == "__main__":
    print("🪙 簡單加密貨幣價格客戶端")
    print("⚠️  請先啟動價格服務：python crypto_price_service.py")
    print("然後運行此客戶端來訂閱所有價格更新")
    print()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程式結束")
