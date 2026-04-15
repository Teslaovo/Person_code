import httpx

USER_SERVICE_URL = "http://localhost:8081"


async def verify_user_exists(user_id: int) -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # 调用公开的验证接口
            response = await client.get(f"{USER_SERVICE_URL}/api/users/verify/{user_id}")
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("exists", False)
            return False
    except Exception:
        return False
