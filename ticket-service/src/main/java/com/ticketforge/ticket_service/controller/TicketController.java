package com.ticketforge.ticket_service.controller;

import com.ticketforge.ticket_service.model.TicketOrder;
import com.ticketforge.ticket_service.service.TicketService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/tickets")
@RequiredArgsConstructor
public class TicketController {

    private final TicketService ticketService;

    @PostMapping("/reserve")
    public ResponseEntity<?> reserve(@RequestParam String userId,
                                     @RequestParam String matchId,
                                     @RequestParam String seatNumber) {
        try {
            TicketOrder order = ticketService.reserveTicket(userId, matchId, seatNumber);
            return ResponseEntity.ok(order);
        } catch (IllegalStateException e) {
            return ResponseEntity.status(409).body(e.getMessage()); // 409 Conflict
        }
    }
}