package com.ticketforge.ticket_service.service;

import com.ticketforge.ticket_service.model.OrderValue;
import com.ticketforge.ticket_service.model.TicketOrder;
import com.ticketforge.ticket_service.repository.TicketOrderRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class TicketService {

    private final TicketOrderRepository orderRepository;
    private final StringRedisTemplate redisTemplate;
    private final KafkaTemplate<String, Object> kafkaTemplate;

    private static final String KAFKA_TOPIC = "ticket.reserved";

    public TicketOrder reserveTicket(String userId, String matchId, String seatNumber) {
        // 1. تصنيع مفتاح فريد للقفل في Redis بناءً على الماتش ورقم الكرسي
        String lockKey = "lock:match:" + matchId + ":seat:" + seatNumber;

        // 2. محاولة أخذ القفل (SETNX) في الـ Redis لمدة 5 دقائق
        // إذا المفتاح موجود مسبقاً، الدالة ترجع false تلقائياً (يعني الكرسي محجوز)
        Boolean isLocked = redisTemplate.opsForValue().setIfAbsent(lockKey, userId, Duration.ofMinutes(5));

        if (Boolean.FALSE.equals(isLocked)) {
            log.warn("Seat {} for Match {} is already locked by another user!", seatNumber, matchId);
            throw new IllegalStateException("Sorry, this seat is currently reserved or already sold!");
        }

        log.info("Successfully acquired Redis lock for seat {}! Processing database record...", seatNumber);

        // 3. إذا أخذنا القفل بنجاح، نسجل الحجز المبدئي في PostgreSQL
        TicketOrder order = TicketOrder.builder()
                .userId(userId)
                .matchId(matchId)
                .seatNumber(seatNumber)
                .status(OrderValue.PENDING)
                .createdAt(LocalDateTime.now())
                .build();

        TicketOrder savedOrder = orderRepository.save(order);

        // 4. إرسال Event إلى كافكا بشكل غير متزامن (Fire and Forget) ليستهلكه سيرفيس الدفع
        Map<String, Object> eventPayload = new HashMap<>();
        eventPayload.put("orderId", savedOrder.getId());
        eventPayload.put("userId", userId);
        eventPayload.put("matchId", matchId);
        eventPayload.put("seatNumber", seatNumber);

        kafkaTemplate.send(KAFKA_TOPIC, eventPayload);
        log.info("Sent ticket.reserved event to Kafka for order ID: {}", savedOrder.getId());

        return savedOrder;
    }
}