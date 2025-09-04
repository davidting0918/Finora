# main.py
import uvicorn
from fastapi import FastAPI, WebSocket

# 步驟 3a：創建 FastAPI 應用程式
app = FastAPI()
# 這就像開一家店，app 就是你的店


# 步驟 3b：創建一個 WebSocket 端點
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 步驟 3c：接受客戶端的連接請求
    await websocket.accept()
    print("有客戶端連接了！")

    # 步驟 3d：保持連接，等待和處理訊息
    try:
        while True:  # 無限迴圈，一直等待訊息
            # 等待客戶端傳訊息給我們
            data = await websocket.receive_text()
            print(f"收到訊息：{data}")

            # 回傳訊息給客戶端
            response = f"伺服器收到：{data}"
            await websocket.send_text(response)
            print(f"回傳訊息：{response}")

    except Exception as e:
        print(f"連接出問題了：{e}")


# 步驟 3e：加一個普通的網頁路由，方便測試
@app.get("/")
async def read_root():
    return {"message": "WebSocket 伺服器運行中！"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
