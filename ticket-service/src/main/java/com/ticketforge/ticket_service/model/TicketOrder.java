package com.ticketforge.ticket_service.model;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "ticket_orders")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TicketOrder {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String userId;
    private String matchId;
    private String seatNumber;

    @Enumerated(EnumType.STRING)
    private OrderValue status;

    private LocalDateTime createdAt;
}