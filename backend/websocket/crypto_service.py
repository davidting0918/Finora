# crypto_price_service.py - 加密貨幣價格推送服務
import asyncio
import json
import random
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()


class PriceData:
    """價格資料類別"""

    def __init__(self, symbol: str, price: float):
        self.symbol = symbol
        self.price = price
        self.timestamp = time.time()
        self.change_24h = 0.0  # 24小時變化百分比
        self.volume_24h = random.uniform(1000000, 10000000)  # 24小時交易量

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "price": round(self.price, 6),
            "timestamp": self.timestamp,
            "change_24h": round(self.change_24h, 2),
            "volume_24h": round(self.volume_24h, 2),
            "formatted_time": datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S"),
        }


class CryptoPriceService:
    def __init__(self):
        # 支援的交易對
        self.symbols = [
            "BTCUSDT",
            "ETHUSDT",
            "ADAUSDT",
            "BNBUSDT",
            "XRPUSDT",
            "SOLUSDT",
            "DOGEUSDT",
            "DOTUSDT",
            "AVAXUSDT",
            "MATICUSDT",
        ]

        # 初始價格（模擬真實價格）
        self.initial_prices = {
            "BTCUSDT": 43250.00,
            "ETHUSDT": 2580.00,
            "ADAUSDT": 0.48,
            "BNBUSDT": 315.50,
            "XRPUSDT": 0.62,
            "SOLUSDT": 98.75,
            "DOGEUSDT": 0.087,
            "DOTUSDT": 7.25,
            "AVAXUSDT": 36.80,
            "MATICUSDT": 0.89,
        }

        # 當前價格資料
        self.price_data: Dict[str, PriceData] = {}

        # 初始化價格
        for symbol, price in self.initial_prices.items():
            self.price_data[symbol] = PriceData(symbol, price)

        # 訂閱管理 {symbol: set(websockets)}
        self.subscriptions: Dict[str, Set[WebSocket]] = defaultdict(set)

        # 所有連接的客戶端 {websocket: client_info}
        self.clients: Dict[WebSocket, dict] = {}

        # 價格更新任務
        self.price_update_task = None

    async def add_client(self, websocket: WebSocket):
        """添加新客戶端"""
        await websocket.accept()
        client_info = {"connect_time": time.time(), "subscribed_symbols": set(), "messages_sent": 0}
        self.clients[websocket] = client_info
        print(f"📱 新客戶端連接，目前客戶端數：{len(self.clients)}")

        # 發送歡迎訊息和可用交易對
        welcome_msg = {
            "type": "welcome",
            "message": "歡迎使用加密貨幣價格推送服務！",
            "available_symbols": self.symbols,
            "commands": {
                "subscribe": "訂閱價格推送 - {'type': 'subscribe', 'symbol': 'BTCUSDT'}",
                "unsubscribe": "取消訂閱 - {'type': 'unsubscribe', 'symbol': 'BTCUSDT'}",
                "get_price": "取得即時價格 - {'type': 'get_price', 'symbol': 'BTCUSDT'}",
                "get_all_prices": "取得所有價格 - {'type': 'get_all_prices'}",
                "my_subscriptions": "查看我的訂閱 - {'type': 'my_subscriptions'}",
            },
        }
        await self.send_message(websocket, welcome_msg)

    def remove_client(self, websocket: WebSocket):
        """移除客戶端"""
        if websocket in self.clients:
            client_info = self.clients[websocket]
            # 從所有訂閱中移除
            for symbol in client_info["subscribed_symbols"]:
                self.subscriptions[symbol].discard(websocket)

            del self.clients[websocket]
            print(f"📱 客戶端斷開，目前客戶端數：{len(self.clients)}")

    async def send_message(self, websocket: WebSocket, message: dict):
        """發送訊息給特定客戶端"""
        try:
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
            if websocket in self.clients:
                self.clients[websocket]["messages_sent"] += 1
            return True
        except Exception as e:
            print(f"💥 發送訊息失敗：{e}")
            self.remove_client(websocket)
            return False

    async def subscribe_symbol(self, websocket: WebSocket, symbol: str):
        """訂閱特定交易對"""
        if symbol not in self.symbols:
            await self.send_message(
                websocket, {"type": "error", "message": f"不支援的交易對：{symbol}", "available_symbols": self.symbols}
            )
            return

        # 添加到訂閱
        self.subscriptions[symbol].add(websocket)
        if websocket in self.clients:
            self.clients[websocket]["subscribed_symbols"].add(symbol)

        # 發送確認和當前價格
        current_price = self.price_data[symbol]
        await self.send_message(
            websocket,
            {
                "type": "subscribed",
                "symbol": symbol,
                "message": f"已訂閱 {symbol} 價格推送",
                "current_price": current_price.to_dict(),
            },
        )

        print(f"📊 客戶端訂閱 {symbol}，該交易對訂閱者數：{len(self.subscriptions[symbol])}")

    async def unsubscribe_symbol(self, websocket: WebSocket, symbol: str):
        """取消訂閱特定交易對"""
        self.subscriptions[symbol].discard(websocket)
        if websocket in self.clients:
            self.clients[websocket]["subscribed_symbols"].discard(symbol)

        await self.send_message(
            websocket, {"type": "unsubscribed", "symbol": symbol, "message": f"已取消訂閱 {symbol} 價格推送"}
        )

        print(f"📊 客戶端取消訂閱 {symbol}，該交易對訂閱者數：{len(self.subscriptions[symbol])}")

    def generate_price_update(self, symbol: str) -> PriceData:
        """生成價格更新（模擬真實市場波動）"""
        current_price_data = self.price_data[symbol]
        current_price = current_price_data.price

        # 模擬價格波動（-2% 到 +2%）
        change_percent = random.uniform(-0.02, 0.02)
        new_price = current_price * (1 + change_percent)

        # 確保價格不會變成負數或過小
        new_price = max(new_price, 0.000001)

        # 計算24小時變化（模擬）
        initial_price = self.initial_prices[symbol]
        change_24h = ((new_price - initial_price) / initial_price) * 100

        # 更新價格資料
        new_price_data = PriceData(symbol, new_price)
        new_price_data.change_24h = change_24h

        return new_price_data

    async def broadcast_price_update(self, symbol: str, price_data: PriceData):
        """廣播價格更新給訂閱者"""
        if symbol not in self.subscriptions:
            return

        subscribers = self.subscriptions[symbol].copy()  # 複製避免修改時出錯

        if not subscribers:
            return

        # 準備價格更新訊息
        message = {"type": "price_update", "data": price_data.to_dict()}

        # 發送給所有訂閱者
        dead_connections = []
        success_count = 0

        for websocket in subscribers:
            if await self.send_message(websocket, message):
                success_count += 1
            else:
                dead_connections.append(websocket)

        # 清理死連接
        for dead_ws in dead_connections:
            self.subscriptions[symbol].discard(dead_ws)

        if success_count > 0:
            price_change_sign = "📈" if price_data.change_24h >= 0 else "📉"
            print(
                f"💸 {symbol} 價格更新：${price_data.price:.6f} {price_change_sign}"
                f"{price_data.change_24h:+.2f}% -> 推送給 {success_count} 個客戶端"
            )

    async def price_update_loop(self):
        """價格更新迴圈（每秒更新）"""
        while True:
            try:
                # 隨機選擇 1-3 個交易對進行價格更新
                symbols_to_update = random.sample(self.symbols, random.randint(1, 3))

                for symbol in symbols_to_update:
                    # 生成新價格
                    new_price_data = self.generate_price_update(symbol)

                    # 更新儲存的價格
                    self.price_data[symbol] = new_price_data

                    # 廣播給訂閱者
                    await self.broadcast_price_update(symbol, new_price_data)

                # 等待1秒
                await asyncio.sleep(1)

            except Exception as e:
                print(f"💥 價格更新迴圈錯誤：{e}")
                await asyncio.sleep(1)

    async def start_price_updates(self):
        """啟動價格更新服務"""
        if self.price_update_task is None:
            self.price_update_task = asyncio.create_task(self.price_update_loop())
            print("🚀 價格更新服務已啟動！")

    def get_service_stats(self):
        """取得服務統計"""
        subscription_stats = {}
        for symbol, subscribers in self.subscriptions.items():
            if subscribers:  # 只顯示有訂閱者的
                subscription_stats[symbol] = len(subscribers)

        client_stats = []
        for websocket, info in self.clients.items():
            client_stats.append(
                {
                    "connect_duration": time.time() - info["connect_time"],
                    "subscribed_symbols": list(info["subscribed_symbols"]),
                    "messages_sent": info["messages_sent"],
                }
            )

        return {
            "total_clients": len(self.clients),
            "total_subscriptions": sum(len(subs) for subs in self.subscriptions.values()),
            "subscription_by_symbol": subscription_stats,
            "client_stats": client_stats,
            "supported_symbols": self.symbols,
        }


# 創建價格服務實例
price_service = CryptoPriceService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用生命週期管理"""
    # 啟動時執行
    await price_service.start_price_updates()
    print("🚀 應用啟動完成")

    yield

    # 關閉時執行（可選）
    if price_service.price_update_task:
        price_service.price_update_task.cancel()
        print("🛑 價格更新服務已停止")


app = FastAPI(lifespan=lifespan)


@app.websocket("/ws/crypto")
async def websocket_endpoint(websocket: WebSocket):
    await price_service.add_client(websocket)

    try:
        while True:
            # 接收客戶端訊息
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                message_type = message.get("type", "")

                if message_type == "subscribe":
                    symbol = message.get("symbol", "").upper()
                    await price_service.subscribe_symbol(websocket, symbol)

                elif message_type == "unsubscribe":
                    symbol = message.get("symbol", "").upper()
                    await price_service.unsubscribe_symbol(websocket, symbol)

                elif message_type == "get_price":
                    symbol = message.get("symbol", "").upper()
                    if symbol in price_service.price_data:
                        price_data = price_service.price_data[symbol]
                        await price_service.send_message(
                            websocket, {"type": "price_response", "data": price_data.to_dict()}
                        )
                    else:
                        await price_service.send_message(websocket, {"type": "error", "message": f"找不到交易對：{symbol}"})

                elif message_type == "get_all_prices":
                    all_prices = {symbol: data.to_dict() for symbol, data in price_service.price_data.items()}
                    await price_service.send_message(websocket, {"type": "all_prices_response", "data": all_prices})

                elif message_type == "my_subscriptions":
                    if websocket in price_service.clients:
                        subscriptions = list(price_service.clients[websocket]["subscribed_symbols"])
                        await price_service.send_message(
                            websocket,
                            {
                                "type": "subscriptions_response",
                                "subscribed_symbols": subscriptions,
                                "count": len(subscriptions),
                            },
                        )

                else:
                    await price_service.send_message(websocket, {"type": "error", "message": f"未知的訊息類型：{message_type}"})

            except json.JSONDecodeError:
                await price_service.send_message(websocket, {"type": "error", "message": "訊息格式錯誤，請使用 JSON 格式"})

    except WebSocketDisconnect:
        price_service.remove_client(websocket)
    except Exception as e:
        print(f"💥 WebSocket 錯誤：{e}")
        price_service.remove_client(websocket)


# API 端點
@app.get("/api/prices")
async def get_all_prices():
    """HTTP API 取得所有價格"""
    return {symbol: data.to_dict() for symbol, data in price_service.price_data.items()}


@app.get("/api/prices/{symbol}")
async def get_symbol_price(symbol: str):
    """HTTP API 取得特定交易對價格"""
    symbol = symbol.upper()
    if symbol in price_service.price_data:
        return price_service.price_data[symbol].to_dict()
    else:
        return {"error": f"找不到交易對：{symbol}"}


@app.get("/api/stats")
async def get_service_stats():
    """取得服務統計"""
    return price_service.get_service_stats()


@app.get("/")
async def get_demo_page():
    return HTMLResponse(
        """
    <!DOCTYPE html>
    <html>
        <head>
            <title>🪙 加密貨幣價格推送服務</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 30px; }
                .controls { background: #2d2d2d; padding: 20px; border-radius: 10px; margin: 20px 0; }
                .price-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 15px; margin: 20px 0; }
                .price-card {
                    background: #2d2d2d; padding: 15px; border-radius: 8px; border: 2px solid #444;
                    transition: all 0.3s ease;
                }
                .price-card.subscribed { border-color: #4CAF50; box-shadow: 0 0 10px rgba(76, 175, 80, 0.3); }
                .price-card.updated { background: #4CAF50; animation: flash 1s ease-out; }
                @keyframes flash { from { background: #4CAF50; } to { background: #2d2d2d; } }
                .symbol { font-size: 1.4em; font-weight: bold; margin-bottom: 5px; }
                .price { font-size: 2em; font-weight: bold; color: #FFD700; }
                .change { font-size: 1.2em; margin: 5px 0; }
                .positive { color: #4CAF50; }
                .negative { color: #f44336; }
                .timestamp { font-size: 0.9em; color: #bbb; }
                .messages {
                    background: #1e1e1e; height: 200px; overflow-y: scroll; padding: 10px;
                    border-radius: 5px; margin: 10px 0; border: 1px solid #444;
                    font-family: monospace; font-size: 0.9em;
                }
                button {
                    padding: 8px 15px; margin: 5px; background: #007bff; color: white;
                    border: none; border-radius: 5px; cursor: pointer; transition: background 0.3s;
                }
                button:hover { background: #0056b3; }
                .subscribe-btn { background: #4CAF50; }
                .subscribe-btn:hover { background: #45a049; }
                .unsubscribe-btn { background: #f44336; }
                .unsubscribe-btn:hover { background: #da190b; }
                .status {
                    padding: 10px; border-radius: 5px; margin: 10px 0;
                    background: #2d2d2d; border: 1px solid #444;
                }
                .connected { border-color: #4CAF50; }
                .disconnected { border-color: #f44336; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🪙 加密貨幣價格推送服務</h1>
                    <p>即時價格更新 • 每秒推送 • 專業級交易所體驗</p>
                </div>

                <div class="status" id="status">
                    <div>連接狀態：<span id="connection-status">未連接</span></div>
                    <div>訂閱數：<span id="subscription-count">0</span></div>
                    <div>收到訊息：<span id="message-count">0</span></div>
                </div>

                <div class="controls">
                    <button onclick="connect()">🔗 連接</button>
                    <button onclick="disconnect()">❌ 斷開</button>
                    <button onclick="subscribeAll()">📊 訂閱所有</button>
                    <button onclick="unsubscribeAll()">🚫 取消所有</button>
                    <button onclick="getAllPrices()">💰 取得所有價格</button>
                    <button onclick="getMySubscriptions()">📋 我的訂閱</button>
                </div>

                <div class="messages" id="messages"></div>

                <div class="price-grid" id="price-grid">
                    <!-- 價格卡片將動態生成 -->
                </div>
            </div>

            <script>
                let socket = null;
                let messageCount = 0;
                let subscriptions = new Set();

                // 支援的交易對（與伺服器保持一致）
                const symbols = [
                    "BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "XRPUSDT",
                    "SOLUSDT", "DOGEUSDT", "DOTUSDT", "AVAXUSDT", "MATICUSDT"
                ];

                function addMessage(message, type = 'info') {
                    const messages = document.getElementById('messages');
                    const div = document.createElement('div');
                    const timestamp = new Date().toLocaleTimeString();
                    div.innerHTML = `<span style="color: #666">[${timestamp}]</span> ${message}`;
                    if (type === 'error') div.style.color = '#f44336';
                    if (type === 'success') div.style.color = '#4CAF50';
                    if (type === 'price') div.style.color = '#FFD700';
                    messages.appendChild(div);
                    messages.scrollTop = messages.scrollHeight;
                }

                function updateStatus() {
                    const statusEl = document.getElementById('connection-status');
                    const statusContainer = document.getElementById('status');
                    const countEl = document.getElementById('subscription-count');
                    const messageCountEl = document.getElementById('message-count');

                    if (socket && socket.readyState === WebSocket.OPEN) {
                        statusEl.textContent = '已連接';
                        statusContainer.className = 'status connected';
                    } else {
                        statusEl.textContent = '未連接';
                        statusContainer.className = 'status disconnected';
                    }

                    countEl.textContent = subscriptions.size;
                    messageCountEl.textContent = messageCount;
                }

                function createPriceCards() {
                    const grid = document.getElementById('price-grid');
                    grid.innerHTML = '';

                    symbols.forEach(symbol => {
                        const card = document.createElement('div');
                        card.className = 'price-card';
                        card.id = `card-${symbol}`;

                        card.innerHTML = `
                            <div class="symbol">${symbol}</div>
                            <div class="price" id="price-${symbol}">--</div>
                            <div class="change" id="change-${symbol}">--</div>
                            <div class="timestamp" id="time-${symbol}">--</div>
                            <div style="margin-top: 10px;">
                                <button class="subscribe-btn" onclick="subscribe('${symbol}')">訂閱</button>
                                <button class="unsubscribe-btn" onclick="unsubscribe('${symbol}')">取消</button>
                            </div>
                        `;

                        grid.appendChild(card);
                    });
                }

                function updatePriceCard(data) {
                    const symbol = data.symbol;
                    const priceEl = document.getElementById(`price-${symbol}`);
                    const changeEl = document.getElementById(`change-${symbol}`);
                    const timeEl = document.getElementById(`time-${symbol}`);
                    const cardEl = document.getElementById(`card-${symbol}`);

                    if (priceEl) priceEl.textContent = `$${data.price}`;
                    if (changeEl) {
                        changeEl.textContent = `${data.change_24h >= 0 ? '+' : ''}${data.change_24h}%`;
                        changeEl.className = `change ${data.change_24h >= 0 ? 'positive' : 'negative'}`;
                    }
                    if (timeEl) timeEl.textContent = data.formatted_time;

                    // 閃爍效果
                    if (cardEl) {
                        cardEl.classList.add('updated');
                        setTimeout(() => cardEl.classList.remove('updated'), 1000);
                    }
                }

                function connect() {
                    if (socket && socket.readyState === WebSocket.OPEN) {
                        addMessage('⚠️ 已經連接了！', 'error');
                        return;
                    }

                    socket = new WebSocket('ws://localhost:8000/ws/crypto');

                    socket.onopen = function(event) {
                        addMessage('✅ WebSocket 連接成功！', 'success');
                        updateStatus();
                    };

                    socket.onmessage = function(event) {
                        messageCount++;
                        const data = JSON.parse(event.data);

                        if (data.type === 'price_update') {
                            updatePriceCard(data.data);
                            addMessage(`💰 ${data.data.symbol}: $${data.data.price}
                            (${data.data.change_24h >= 0 ? '+' : ''}${data.data.change_24h}%)`, 'price');
                        } else if (data.type === 'welcome') {
                            addMessage(`🎉 ${data.message}`, 'success');
                        } else if (data.type === 'subscribed') {
                            subscriptions.add(data.symbol);
                            document.getElementById(`card-${data.symbol}`).classList.add('subscribed');
                            addMessage(`📊 已訂閱 ${data.symbol}`, 'success');
                            updatePriceCard(data.current_price);
                        } else if (data.type === 'unsubscribed') {
                            subscriptions.delete(data.symbol);
                            document.getElementById(`card-${data.symbol}`).classList.remove('subscribed');
                            addMessage(`🚫 已取消訂閱 ${data.symbol}`, 'success');
                        } else if (data.type === 'all_prices_response') {
                            Object.values(data.data).forEach(priceData => {
                                updatePriceCard(priceData);
                            });
                            addMessage('💰 已更新所有價格', 'success');
                        } else {
                            addMessage(`📨 ${data.type}: ${JSON.stringify(data)}`, 'info');
                        }

                        updateStatus();
                    };

                    socket.onclose = function(event) {
                        addMessage('🔌 WebSocket 連接已關閉', 'error');
                        updateStatus();
                    };

                    socket.onerror = function(error) {
                        addMessage('💥 WebSocket 錯誤', 'error');
                        updateStatus();
                    };
                }

                function disconnect() {
                    if (socket) {
                        socket.close();
                        subscriptions.clear();
                        document.querySelectorAll('.price-card').forEach(card => {
                            card.classList.remove('subscribed');
                        });
                        addMessage('👋 主動斷開連接', 'info');
                        updateStatus();
                    }
                }

                function subscribe(symbol) {
                    if (socket && socket.readyState === WebSocket.OPEN) {
                        const message = {
                            type: "subscribe",
                            symbol: symbol
                        };
                        socket.send(JSON.stringify(message));
                    } else {
                        addMessage('⚠️ 請先連接 WebSocket', 'error');
                    }
                }

                function unsubscribe(symbol) {
                    if (socket && socket.readyState === WebSocket.OPEN) {
                        const message = {
                            type: "unsubscribe",
                            symbol: symbol
                        };
                        socket.send(JSON.stringify(message));
                    } else {
                        addMessage('⚠️ 請先連接 WebSocket', 'error');
                    }
                }

                function subscribeAll() {
                    symbols.forEach(symbol => {
                        if (!subscriptions.has(symbol)) {
                            subscribe(symbol);
                        }
                    });
                }

                function unsubscribeAll() {
                    Array.from(subscriptions).forEach(symbol => {
                        unsubscribe(symbol);
                    });
                }

                function getAllPrices() {
                    if (socket && socket.readyState === WebSocket.OPEN) {
                        const message = { type: "get_all_prices" };
                        socket.send(JSON.stringify(message));
                    } else {
                        addMessage('⚠️ 請先連接 WebSocket', 'error');
                    }
                }

                function getMySubscriptions() {
                    if (socket && socket.readyState === WebSocket.OPEN) {
                        const message = { type: "my_subscriptions" };
                        socket.send(JSON.stringify(message));
                    } else {
                        addMessage('⚠️ 請先連接 WebSocket', 'error');
                    }
                }

                // 初始化
                createPriceCards();
                updateStatus();
                addMessage('🎉 加密貨幣價格推送服務已載入！點擊「連接」開始使用', 'success');
            </script>
        </body>
    </html>
    """
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    print("🪙 啟動加密貨幣價格推送服務...")
    print("📊 功能：")
    print("  - WebSocket: ws://localhost:8000/ws/crypto")
