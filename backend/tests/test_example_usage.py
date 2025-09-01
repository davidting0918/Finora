"""
示範如何使用新的模組作用域 fixture 的範例測試檔案
這個檔案展示了最佳實踐和不同的使用模式
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import status

class TestModuleScopeUsage:
    """展示如何使用模組作用域的 fixture"""
    
    @pytest.mark.asyncio
    async def test_using_dual_users(
        self, 
        module_async_client: AsyncClient,
        module_test_users: dict
    ):
        """測試使用兩個不同的用戶"""
        
        # 使用用戶1的認證
        response1 = await module_async_client.get(
            "/user/profile",
            headers=module_test_users["user1"]["headers"]
        )
        assert response1.status_code == 200
        
        # 使用用戶2的認證
        response2 = await module_async_client.get(
            "/user/profile", 
            headers=module_test_users["user2"]["headers"]
        )
        assert response2.status_code == 200
        
        # 驗證是不同的用戶
        user1_data = response1.json()["data"]
        user2_data = response2.json()["data"]
        assert user1_data["id"] != user2_data["id"]
        assert user1_data["email"] != user2_data["email"]

    @pytest.mark.asyncio 
    async def test_using_comprehensive_data(
        self,
        module_async_client: AsyncClient,
        comprehensive_test_data: dict
    ):
        """測試使用綜合測試資料"""
        
        # 可以同時獲得用戶和交易資料
        user1 = comprehensive_test_data["user1"]
        transactions = comprehensive_test_data["transactions"]
        
        # 使用用戶1的標頭
        response = await module_async_client.get(
            "/transaction/list",
            headers=comprehensive_test_data["user1_headers"]
        )
        
        assert response.status_code == 200
        assert len(transactions) > 0  # 驗證有交易資料

    @pytest.mark.asyncio
    async def test_analytics_with_existing_data(
        self,
        module_async_client: AsyncClient,
        analytics_test_data: dict
    ):
        """測試使用現成的分析資料"""
        
        # analytics_test_data 已經包含了用戶和交易
        response = await module_async_client.get(
            "/analytics/overview",
            headers={"Authorization": f"Bearer {analytics_test_data['access_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 1
        assert len(analytics_test_data["transactions"]) > 0

class TestMixedScopeUsage:
    """展示混合使用不同作用域 fixture 的方式"""
    
    @pytest.mark.asyncio
    async def test_readonly_with_module_fixture(
        self,
        module_async_client: AsyncClient,    # 模組級 - 共享 HTTP 客戶端
        module_auth_headers: dict            # 模組級 - 共享認證
    ):
        """只讀操作，適合使用模組 fixture"""
        response = await module_async_client.get(
            "/user/profile",
            headers=module_auth_headers
        )
        assert response.status_code == 200
        # 這個測試不會修改任何資料，所以安全使用共享資源
    
    @pytest.mark.asyncio
    async def test_isolated_with_function_fixture(
        self,
        async_client: AsyncClient,     # 函數級 - 隔離的 HTTP 客戶端  
        fresh_test_user: dict          # 函數級 - 每次都是新用戶
    ):
        """需要隔離的操作，使用函數 fixture"""
        
        # 修改用戶資料 - 不會影響其他測試
        response = await async_client.put(
            "/user/update",
            headers=fresh_test_user["headers"],
            json={"name": "Modified Name"}
        )
        assert response.status_code == 200
        # 每個測試都有獨立的用戶，所以安全修改

class TestFixtureLifecycle:
    """展示 fixture 的生命週期"""
    
    @pytest.mark.asyncio
    async def test_first_usage(self, module_test_users):
        """第一次使用模組 fixture"""
        print(f"🔥 第一次使用: User1 ID = {module_test_users['user1']['user'].id}")
        # 這時候 fixture 會被建立（如果還沒建立的話）
        
    @pytest.mark.asyncio
    async def test_second_usage(self, module_test_users):
        """第二次使用相同的模組 fixture"""
        print(f"♻️  重複使用: User1 ID = {module_test_users['user1']['user'].id}")
        # 這時候使用的是相同的 fixture，不會重新建立
        
    @pytest.mark.asyncio
    async def test_third_usage(self, module_test_users):
        """第三次使用相同的模組 fixture"""
        print(f"♻️  再次重複使用: User1 ID = {module_test_users['user1']['user'].id}")
        # 依然是相同的用戶 ID，證明是共享的