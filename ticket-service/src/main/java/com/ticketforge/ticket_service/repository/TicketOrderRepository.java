package com.ticketforge.ticket_service.repository;

import com.ticketforge.ticket_service.model.TicketOrder;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface TicketOrderRepository extends JpaRepository<TicketOrder, Long> {
}