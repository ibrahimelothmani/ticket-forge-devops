import http from 'k6/http';
import { check, sleep } from 'k6';

// 1. تهيئة بروفايل الحمل (Load Profile) - محاكاة هجوم فجائي (Spike)
export const options = {
    stages: [
        { duration: '10s', target: 100 }, // الارتفاع سريعاً من 0 إلى 100 مستخدم في 10 ثوانٍ
        { duration: '30s', target: 800 }, // الانفجار: القفز فجأة إلى 800 مستخدم متزامن (لحظة فتح بيع التذاكر)
        { duration: '20s', target: 800 }, // الثبات عند قمة الضغط لمدة 20 ثانية
        { duration: '10s', target: 100 }, // تراجع الترافيك بعد نفاد التذاكر
        { duration: '10s', target: 0 },   // العودة للاستقرار
    ],
    // شروط نجاح الـ Pipeline أمنياً وتقنياً (SLA Thresholds)
    thresholds: {
        http_req_failed: ['rate<0.01'],   // يجب أن تكون نسبة الأخطاء أقل من 1%
        http_req_duration: ['p(95)<250'], // 95% من الطلبات يجب أن ترد في أقل من 250 جزء من الثانية
    },
};

// 2. الدالة التشغيلية التي سينفذها كل مستخدم وهمي (Virtual User)
export default function () {
    // العنوان المحلي للـ API Gateway (تأكد من تشغيل الـ port-forward لـ Gateway على بورت 8000)
    const url = 'http://localhost:8000/api/v1/tickets/reserve';
    
    const payload = JSON.stringify({
        matchId: "match-tunisia-2026",
        category: "VIP",
        userId: `user-id-${__VU}-${__ITER}` // توليد معرف مستخدم ديناميكي بناءً على رقم المستخدم واللفّة
    });

    const params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    // إرسال الطلب الفعلي
    const res = http.post(url, payload, params);

    // التحقق من صحة رد السيرفر (أن الكود الراجع هو 200 أو 201 بنجاح الحجز)
    check(res, {
        'status is 200 or 201': (r) => r.status === 200 || r.status === 201,
        'transaction context valid': (r) => r.body.includes('reserved') || r.body.includes('status'),
    });

    // انتظار ثانية واحدة بين الطلبات لكل مستخدم لمحاكاة السلوك البشري الطبيعي
    sleep(1);
}