"""from sqlalchemy.ext.asyncio import AsyncSession
from auth.database import get_async_session, Users
from yookassa import Configuration, Payment
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from datetime import datetime, timedelta
from fastapi_users import FastAPIUsers
from auth.auth import auth_backend
from auth.menager import get_user_manager
from auth.schemas import UserRead, UserCreate
router = APIRouter()

fastapi_users = FastAPIUsers[Users, int](
    get_user_manager,
    [auth_backend],
)



current_user = fastapi_users.current_user()

Configuration.configure("996855", "test_Ea50FMw71gvcGgq-WGXcbmn74hCZCxm7DIC0jN9tvUw")

@router.post("/create-payment")
async def create_payment(
    user: Users = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        payment = Payment.create(
            {
                "amount": {
                    "value": "1000.00",
                    "currency": "RUB",
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": "http://127.0.0.1:8000/payments/success",
                },
                "capture": True,
                "description": f"Subscription for user {user.id}",
                "metadata": {
                    "user_id": user.id,
                },
            }
        )

        # Используем реальный payment.id
        payment_id = payment.id
        print(f"User ID: {user.id}, Payment ID: {payment_id}")
        new_confirmation = False
        # Обновляем last_payment_id в таблице users
        await session.execute(
            text("UPDATE users SET payment_id = :payment_id, payment_confirmation= :val WHERE id = :user_id"),
            {"payment_id": payment.id, "user_id": user.id, "val": new_confirmation}
        )
        await session.commit()

        return {"confirmation_url": payment.confirmation.confirmation_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment creation failed: {e}")



@router.get("/payments/success")
async def payment_success(
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(current_user),
):
    result = await session.execute(
        text("SELECT payment_confirmation FROM users WHERE id = :user_id"),
        {"user_id": user.id}
    )
    confirmation = result.scalar_one_or_none()
    print(confirmation)
    if confirmation:
        return {"message": "Payment not completed."}
        # Получаем информацию о платеже из YooKassa
    result = await session.execute(
        text("SELECT payment_id FROM users WHERE id = :user_id"),
        {"user_id": user.id}
    )
    payment_id = result.scalar_one_or_none()
    if payment_id == None:
        return {"message": "Payment not completed successfully."}
    payment = Payment.find_one(payment_id)
    if payment.status != "succeeded":
        return {"message": "Payment not completed successfully."}

        # Устанавливаем новую дату окончания подписки на 30 дней вперёд
    new_subscription_end = datetime.utcnow() + timedelta(days=30)

    await session.execute(
        Users.__table__.update()
        .where(Users.id == user.id)
        .values(subscription_end=new_subscription_end)
    )
    await session.commit()

    confirmation = True

    await session.execute(
        text("UPDATE users SET payment_confirmation = :payment WHERE id = :user_id"),
        {"payment": confirmation, "user_id": user.id}
    )
    await session.commit()

    return {"message": "Subscription activated for 30 days!"}


"""

"""@app.post("/create-auto-payment")
async def create_auto_payment(
    user: Users = Depends(current_user),
):
    try:
        payment = Payment.create(
            {
                "amount": {
                    "value": "1000.00",
                    "currency": "RUB",
                },
                "payment_method_id": "CARD_TOKEN_FROM_USER",  # Токен карты пользователя
                "capture": True,
                "description": f"Auto-payment for user {user.id}",
                "metadata": {
                    "user_id": user.id,
                },
            }
        )

        return {"status": payment.status, "message": "Auto-payment initialized."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-payment creation failed: {e}")"""