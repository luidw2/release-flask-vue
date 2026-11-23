import threading
import json
from flask import Blueprint, request, render_template, redirect, render_template_string
from datetime import datetime
from utils import SM2, SM4
from utils.db import Session, Merchant, Transaction,User
import uuid
import requests

user = Blueprint('pay_process', __name__)

def send_callback(callback_url, params):
    """异步回调电商后台"""
    try:
        resp = requests.post(callback_url, json=params, timeout=5)
        print(f"异步回调发送成功: status={resp.status_code}")
    except Exception as e:
        print(f"异步回调发送失败: {e}")



@user.route('/pay/process', methods=['POST'])
def pay_process():
    try:
        # 1. 获取表单数据
        username = request.form.get('username')
        password = request.form.get('password')
        order_id = request.form.get('order_id')
        amount = request.form.get('amount')
        transaction_id = request.form.get('transaction_id')

        session = Session()
        # 2. 验证银行账号
        my_user = session.query(User).filter_by(username=username).first()
        if my_user is None:
            return render_template('pay_error.html',
                                   error_title='账号验证失败',
                                   error_message='用户名或密码错误')
        if my_user.password != password:
            return render_template('pay_error.html',
                                   error_title='账号验证失败',
                                   error_message='用户名或密码错误')



        # 3. 获取交易和商户信息

        tx = session.query(Transaction).filter_by(transaction_id=transaction_id).first()
        if not tx:
            session.close()
            return render_template('pay_error.html',
                                   error_title='交易不存在',
                                   error_message='交易记录不存在')

        merchant = session.query(Merchant).filter_by(merchant_id=tx.merchant_id).first()

        if not merchant:
            session.close()
            return render_template('pay_error.html',
                                   error_title='商户不存在',
                                   error_message='商户信息不存在')

        # 4. 幂等性检查：如果交易已支付，直接返回成功
        if tx.status == 'paid':
            session.close()
            return render_template('pay_error.html',
                                   error_title='重复支付',
                                   error_message='该订单已完成支付，请勿重复提交')

        return_url = merchant.return_url
        callback_url = merchant.callback_url
        tx_amount = tx.amount  # 在关闭session前保存金额
        # 5. 更新交易状态

        public_key = merchant.public_key
        if my_user.money - tx.amount <0:
            return render_template('pay_error.html',
                                   error_title='余额不足',
                                   error_message='该订单余额不足')
        my_user.money = my_user.money - tx.amount
        balance_my = my_user.money
        tx.status = 'paid'
        session.commit()
        session.close()

        # 5. 生成加密结果（使用商户公钥）
        result_data = {
            'order_id': order_id,
            'status': 'success',
            'transaction_id': transaction_id,
            'amount': str(tx_amount),  # 使用预先保存的金额（分）
            'balance': str(balance_my),  # 添加支付后的余额（分）
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

        #生成sm4密钥
        sm4_key,sm4_iv = SM4.generate_sm4_key()
        result_data_byte = json.dumps(result_data).encode('utf-8')
        encrypted_sm4_data = SM4.sm4_encrypt(sm4_key, sm4_iv,result_data_byte)
        #sm2公钥获取


        sm4_key_enc = SM2.sm2_encrypt(public_key,sm4_key)
        sm4_iv_enc = SM2.sm2_encrypt(public_key,sm4_iv)

        encrypted_params = {
            'encrypted_key': sm4_key_enc.hex(),
            'iv': sm4_iv_enc.hex(),
            'data': encrypted_sm4_data.hex()
        }

        # 返回自动提交表单的 HTML
        html = f"""
            <html>
            <body onload="document.forms[0].submit()">
                <form action="{return_url}" method="post">
                    <input type="hidden" name="encrypted_key" value="{encrypted_params['encrypted_key']}">
                    <input type="hidden" name="iv" value="{encrypted_params['iv']}">
                    <input type="hidden" name="data" value="{encrypted_params['data']}">
                </form>
                <p>正在跳转至商户...</p>
            </body>
            </html>
            
            """
        #异步回调
        if callback_url:
            threading.Thread(
                target=send_callback,
                args=(callback_url, encrypted_params),
                daemon=True
            ).start()

        #同步回调
        return render_template_string(html)



    except Exception as e:
        return render_template('pay_error.html',
                               error_title='支付失败',
                               error_message=str(e))