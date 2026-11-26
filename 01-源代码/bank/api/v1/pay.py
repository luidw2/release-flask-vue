from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from utils import SM2
from utils.db import Session, Merchant, Transaction
import uuid
import time

user = Blueprint('pay', __name__)

SIGN_TEMPLATE = "{order_id}|{amount}|{merchant_id}|{timestamp}"

TIMESTAMP_VALIDITY = 60


def build_response(code, message='', data=None, error=None, status=200):
    payload = {
        'code': code,
        'message': message,
        'error': error,
        'data': data,
        'time': datetime.utcnow().isoformat() + 'Z'
    }
    return jsonify(payload), status


@user.route('/pay', methods=['GET'])
def pay():
    try:
        # 1. 获取请求参数
        order_id = request.args.get('order_id')
        amount = request.args.get('amount')
        merchant_id = request.args.get('merchant_id')
        timestamp = request.args.get('timestamp')
        sign = request.args.get('sign')
        # 2. 参数校验
        if not all([order_id, amount, merchant_id, timestamp, sign]):
            return render_template('pay_error.html',
                                   error_title='参数缺失',
                                   error_message='缺少必要的支付参数')

        # 3. 从数据库获取商户信息（包含公钥）
        session = Session()
        merchant = session.query(Merchant).filter_by(merchant_id=merchant_id).first()
        if not merchant:
            session.close()
            return render_template('pay_error.html',
                                       error_title='商户不存在',
                                       error_message='商户信息不存在')
        if not merchant.public_key:
            session.close()
            return render_template('pay_error.html',
                                       error_title='配置错误',
                                       error_message='商户公钥未配置')
            # 获取公钥
        public_key = (merchant.public_key or "").replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\r", "\r")



        # 4. 构建签名原文并验证
        sign_raw = SIGN_TEMPLATE.format(
            order_id=order_id,
            amount=amount,
            merchant_id=merchant_id,
            timestamp=timestamp
        )

        try:
            signature_bytes = bytes.fromhex(sign)
            verify_result = SM2.sm2_verify(public_key, sign_raw.encode('utf-8'), signature_bytes)
            print("验签成功")
        except Exception as e:
            session.close()
            return render_template('pay_error.html',
                                   error_title='签名格式错误',
                                   error_message=f'{e}')

        if not verify_result:
            session.close()
            return render_template('pay_error.html',
                                   error_title='签名验证错误',
                                   error_message=f'签名验证错误')

        # 4.5 时间戳有效期检查（防重放攻击）
        try:
            request_timestamp = int(timestamp)
            current_time = int(time.time())
            time_diff = abs(current_time - request_timestamp)

            if time_diff > TIMESTAMP_VALIDITY:
                session.close()
                return render_template('pay_error.html',
                                       error_title='请求过期',
                                       error_message=f'支付请求已过期（有效期5分钟），请重新发起支付')
        except ValueError:
            session.close()
            return render_template('pay_error.html',
                                   error_title='时间戳格式错误',
                                   error_message='时间戳格式无效')

        # 5. 验证商户状态
        if merchant.status != 'active':
            session.close()
            return render_template('pay_error.html',
                                   error_title='商户异常',
                                   error_message='商户状态异常')

        # 6. 幂等性检查：检查是否已存在相同订单的交易
        existing_tx = session.query(Transaction).filter(
            Transaction.order_id == order_id,
            Transaction.merchant_id == merchant_id
        ).first()

        if existing_tx:
            # 如果订单已支付，返回重复支付错误
            if existing_tx.status == 'paid':
                session.close()
                return render_template('pay_error.html',
                                       error_title='重复支付',
                                       error_message='该订单已完成支付，请勿重复提交')
            
            # 如果订单未完成，直接返回已存在的交易
            else :
                tem = existing_tx.transaction_id
                session.close()

            '''return render_template('pay_error.html',
                                   error_title='重复支付',
                                   error_message='该订单已完成支付，请勿重复提交')'''

        # 7. 创建交易记录
        else :
            tem = str(uuid.uuid4()).replace('-', '')

        transaction_id =tem

        new_transaction = Transaction(
            transaction_id=transaction_id,
            order_id=order_id,
            merchant_id=merchant_id,
            amount=int(amount),
            status='pending',
            sign=sign
        )

        session.add(new_transaction)
        session.commit()
        session.close()

        # 7. 返回成功响应
        return render_template('pay_confirm.html',
                               order_id=order_id,
                               amount=str(int(amount) / 100),
                               merchant_name='安全电商系统',
                               transaction_id=transaction_id
                               )

    except Exception as e:
        return build_response(500, '服务器内部错误', error=str(e))