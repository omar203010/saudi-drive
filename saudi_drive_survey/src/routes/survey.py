from flask import Blueprint, request, jsonify, current_app
from src.models.survey import SurveyResponse
from src.models.user import db
import traceback

survey_bp = Blueprint('survey', __name__)

@survey_bp.route('/survey', methods=['POST'])
def submit_survey():
    try:
        data = request.get_json(force=True)

        # ✅ التحقق من وجود الحقل المطلوب
        if not data.get('customer_suggestions', '').strip():
            return jsonify({'error': 'اقتراحات وملاحظات العملاء مطلوبة'}), 400

        # ✅ التحقق من طول النص
        customer_suggestions = data.get('customer_suggestions', '')
        if len(customer_suggestions) > 1000:
            return jsonify({'error': 'اقتراحات العملاء يجب أن تكون أقل من 1000 حرف'}), 400

        # ✅ معالجة الحقول متعددة الاختيارات بشكل أنظف
        def normalize_list_field(field_name):
            value = data.get(field_name, '')
            if isinstance(value, list):
                return ','.join(value)
            return value.strip() if isinstance(value, str) else None

        important_factors = normalize_list_field('important_factors')
        current_problems = normalize_list_field('current_problems')
        preferred_payment = normalize_list_field('preferred_payment')

        # ✅ إنشاء رد جديد
        new_response = SurveyResponse(
            name=data.get('name', '').strip() or None,
            gender=data.get('gender', '').strip() or None,
            phone=data.get('phone', '').strip() or None,

            # الأسئلة الجديدة
            current_app=data.get('current_app', '').strip() or None,
            usage_frequency=data.get('usage_frequency', '').strip() or None,
            important_factors=important_factors or None,
            additional_features=data.get('additional_features', '').strip() or None,
            current_problems=current_problems or None,
            additional_problems=data.get('additional_problems', '').strip() or None,
            try_saudi_app=data.get('try_saudi_app', '').strip() or None,
            preferred_payment=preferred_payment or None,
            female_captain_service=data.get('female_captain_service', '').strip() or None,
            female_service_suggestions=data.get('female_service_suggestions', '').strip() or None,

            # الأسئلة القديمة (للتوافق)
            price_suggestions=data.get('price_suggestions', '').strip() or None,
            payment_methods=data.get('payment_methods', '').strip() or None,
            captain_to_captain=data.get('captain_to_captain', '').strip() or None,
            customer_suggestions=customer_suggestions.strip(),
            ip_address=request.remote_addr
        )

        db.session.add(new_response)
        db.session.commit()

        return jsonify({
            'message': 'تم إرسال الاستبيان بنجاح',
            'id': new_response.id
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("❌ خطأ في submit_survey: %s", traceback.format_exc())
        return jsonify({'error': f'حدث خطأ أثناء إرسال الاستبيان: {str(e)}'}), 500


@survey_bp.route('/survey/responses', methods=['GET'])
def get_responses():
    try:
        responses = SurveyResponse.query.order_by(SurveyResponse.created_at.desc()).all()
        return jsonify([response.to_dict() for response in responses])
    except Exception as e:
        current_app.logger.error("❌ خطأ في get_responses: %s", traceback.format_exc())
        return jsonify({'error': 'حدث خطأ أثناء جلب البيانات'}), 500


@survey_bp.route('/survey/stats', methods=['GET'])
def get_stats():
    try:
        total_responses = SurveyResponse.query.count()
        with_phone = SurveyResponse.query.filter(SurveyResponse.phone.isnot(None)).count()
        male_count = SurveyResponse.query.filter_by(gender='ذكر').count()
        female_count = SurveyResponse.query.filter_by(gender='أنثى').count()
        captain_to_captain_yes = SurveyResponse.query.filter_by(captain_to_captain='نعم').count()

        # إحصائيات جديدة
        uber_users = SurveyResponse.query.filter_by(current_app='أوبر').count()
        careem_users = SurveyResponse.query.filter_by(current_app='كريم').count()
        daily_users = SurveyResponse.query.filter_by(usage_frequency='يومياً').count()
        will_try_saudi = SurveyResponse.query.filter_by(try_saudi_app='نعم').count()

        return jsonify({
            'total_responses': total_responses,
            'responses_with_phone': with_phone,
            'male_responses': male_count,
            'female_responses': female_count,
            'captain_to_captain_preference': captain_to_captain_yes,
            'uber_users': uber_users,
            'careem_users': careem_users,
            'daily_users': daily_users,
            'will_try_saudi_app': will_try_saudi
        })
    except Exception as e:
        current_app.logger.error("❌ خطأ في get_stats: %s", traceback.format_exc())
        return jsonify({'error': 'حدث خطأ أثناء جلب الإحصائيات'}), 500
