import httpx
import uuid
from config import CRYPTO_BOT_TOKEN

class CryptoBotAPI:
    def __init__(self):
        self.token = CRYPTO_BOT_TOKEN
        self.headers = {
            "Crypto-Pay-API-Token": self.token,
            "Content-Type": "application/json"
        }

    async def create_invoice(self, user_id: int, amount: float):
        try:
            payload = f"deposit_{user_id}_{uuid.uuid4().hex[:8]}"

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://pay.crypt.bot/api/createInvoice",
                    json={
                        "asset": "USDT",
                        "amount": str(amount),
                        "description": f"Пополнение | ID: {user_id}",
                        "payload": payload,
                        "paid_btn_name": "openBot",
                        "paid_btn_url": f"https://t.me/{user_id}",
                        "allow_comments": True,
                        "expires_in": 3600,
                        "allow_multiple_currency": True
                    },
                    headers=self.headers
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        return {
                            "invoice_id": data["result"]["invoice_id"],
                            "pay_url": data["result"]["pay_url"]
                        }
                return None

        except Exception as e:
            print(f"Ошибка создания счета: {e}")
            return None

    async def create_check(self, user_id: int, amount: float):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://pay.crypt.bot/api/createCheck",
                    json={
                        "asset": "USDT",
                        "amount": str(amount),
                        "pin_to_user_id": user_id
                    },
                    headers=self.headers
                )

                print(f"📡 ОТВЕТ ОТ CRYPTOBOT (createCheck): {response.text}")

                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        return {
                            "check_id": data["result"]["check_id"],
                            "bot_check_url": data["result"]["bot_check_url"]
                        }
                return None

        except Exception as e:
            print(f"❌ Ошибка в create_check: {e}")
            return None

    async def check_invoice(self, invoice_id: str):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    "https://pay.crypt.bot/api/getInvoices",
                    params={"invoice_ids": invoice_id},
                    headers=self.headers
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        invoices = data["result"].get("items", [])
                        if invoices:
                            invoice = invoices[0]
                            return {
                                "status": invoice.get("status"),
                                "amount": float(invoice.get("amount", 0)),
                                "asset": invoice.get("asset")
                            }
                return None

        except Exception as e:
            print(f"Ошибка проверки счета: {e}")
            return None
