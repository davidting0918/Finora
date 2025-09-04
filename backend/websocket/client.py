# client.py
import asyncio

import websockets


# 步驟 6a：定義客戶端主要函數
async def client_main():
    # WebSocket 伺服器的地址
    uri = "ws://localhost:8000/ws"

    print("準備連接到 WebSocket 伺服器...")

    try:
        # 步驟 6b：建立 WebSocket 連接
        async with websockets.connect(uri) as websocket:
            print("✅ 連接成功！")

            # 步驟 6c：發送幾個測試訊息
            test_messages = ["Hello, Server!", "這是第二個訊息", "WebSocket 真好用！", "再見！"]

            for message in test_messages:
                # 步驟 6d：發送訊息
                print(f"📤 發送：{message}")
                await websocket.send(message)

                # 步驟 6e：等待並接收回應
                response = await websocket.recv()
                print(f"📨 收到：{response}")

                # 步驟 6f：等待 1 秒再發下一個訊息
                await asyncio.sleep(1)

            print("測試完成！")

    except Exception as e:
        print(f"💥 發生錯誤：{e}")


# 步驟 6g：如果直接執行這個檔案，就跑客戶端
if __name__ == "__main__":
    # 運行非同步函數
    asyncio.run(client_main())
